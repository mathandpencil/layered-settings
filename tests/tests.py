import os
import unittest
from unittest.mock import MagicMock, patch

from layered_settings import initialize_settings
from layered_settings import loaders
from layered_settings.loaders import secrets_manager_loader

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))


class LayeredSettingsTests(unittest.TestCase):
    def setUp(self):
        pass

    def test_empty_settings(self):
        get_setting = initialize_settings([])

        with self.assertRaises(KeyError):
            self.assertEqual(None, get_setting("section1", "key1"))

    def test_dict_settings(self):
        get_setting = initialize_settings(
            [
                {
                    "general": {"CLIENT_NAME": "client"},
                }
            ]
        )

        with self.assertRaises(KeyError):
            self.assertEqual(None, get_setting("section1", "key1"))

        self.assertEqual("client", get_setting("general", "CLIENT_NAME"))

    def test_env_settings(self):
        get_setting = initialize_settings([loaders.EnvLoader("APP__{section}__{key}")])

        with self.assertRaises(KeyError):
            self.assertEqual(None, get_setting("section1", "key1"))

        with patch.dict(
            "os.environ",
            {
                "APP__section1__key1": "abc",
                "APP__section1__key2": "def",
                "APP__section2__key1": "ghi",
            },
        ):

            self.assertEqual("abc", get_setting("section1", "key1"))
            self.assertEqual("ghi", get_setting("section2", "key1"))

            with self.assertRaises(KeyError):
                self.assertEqual(None, get_setting("section2", "key2"))

    def test_env_settings_with_hyphen(self):
        get_setting = initialize_settings([loaders.EnvLoader("APP__{section}__{key}")])

        with self.assertRaises(KeyError):
            self.assertEqual(None, get_setting("section-1", "key1"))

        with patch.dict(
            "os.environ",
            {
                "APP__section-1__key1": "abc",
            },
        ):

            self.assertEqual("abc", get_setting("section-1", "key1"))

    def test_normal_usage(self):
        ALLOW_SSM_CONFIGURATION = False

        get_setting = initialize_settings(
            sources=[
                # Lowest priority is setting-defaults.ini.  All configuration values should be defaulted in here.
                loaders.ConfigParserLoader(os.path.join(SCRIPT_DIR, "inifiles", "setting-defaults.ini")),
                os.path.join(SCRIPT_DIR, "inifiles", "setting-overrides.ini"),
                # If ENV is set and we are able/willing to reach out to AWS, do so..
                loaders.SSMLoader(f"/app/stage/", aws_region="us-east-1") if ALLOW_SSM_CONFIGURATION else None,
                # Top priority -- env var
                loaders.EnvLoader("APP__{section}__{key}"),
            ]
        )

        with patch.dict(
            "os.environ",
            {
                "APP__section1__key1": "env11",
            },
        ):
            self.assertEqual("env11", get_setting("section1", "key1"))
            self.assertEqual("override21", get_setting("section2", "key1"))
            self.assertEqual("default22", get_setting("section2", "key2"))


# Sentinel: a secret whose Name maps to this has no AWSCURRENT version,
# so get_secret_value should raise ResourceNotFoundException.
_NO_AWSCURRENT = object()


class SecretsManagerLoaderTests(unittest.TestCase):
    def _patched_loader(self, secret_strings):
        """Return a context manager patching the loader's boto3 with a mock
        secretsmanager client.

        ``secret_strings`` maps a secret Name to its SecretString, or to
        ``_NO_AWSCURRENT`` to simulate a secret with no AWSCURRENT version.
        """

        class ResourceNotFoundException(Exception):
            pass

        client = MagicMock()
        client.exceptions.ResourceNotFoundException = ResourceNotFoundException

        names = list(secret_strings)
        client.list_secrets.return_value = {
            "SecretList": [{"Name": name, "ARN": f"arn:{name}"} for name in names]
        }
        arn_to_name = {f"arn:{name}": name for name in names}

        def get_secret_value(SecretId):
            value = secret_strings[arn_to_name[SecretId]]
            if value is _NO_AWSCURRENT:
                raise ResourceNotFoundException(
                    "Secrets Manager can't find the specified secret value for staging label: AWSCURRENT"
                )
            return {"SecretString": value}

        client.get_secret_value.side_effect = get_secret_value

        boto3_mock = MagicMock()
        boto3_mock.client.return_value = client
        return patch.object(secrets_manager_loader, "boto3", boto3_mock)

    def test_skips_secret_without_awscurrent_version(self):
        """A secret with no AWSCURRENT version is skipped, not fatal, and does
        not leak the previous secret's value into its key."""
        path = "/shared/global/"
        with self._patched_loader(
            {
                "/shared/global/section1/key1": "good-value",
                "/shared/global/section2/key1": _NO_AWSCURRENT,
                "/shared/global/section3/key1": "also-good",
            }
        ):
            settings = secrets_manager_loader._load_from_secrets_manager(path, "us-east-1")

        self.assertEqual("good-value", settings["section1/key1"])
        self.assertEqual("also-good", settings["section3/key1"])
        # The bad secret must be skipped entirely, not present with a stale value.
        self.assertNotIn("section2/key1", settings)

    def test_json_secret_is_flattened(self):
        """A JSON secret string is flattened into section/subkey entries."""
        path = "/shared/global/"
        with self._patched_loader(
            {
                "/shared/global/section1/anything": '{"key1": "v1", "key2": "v2"}',
            }
        ):
            settings = secrets_manager_loader._load_from_secrets_manager(path, "us-east-1")

        self.assertEqual("v1", settings["section1/key1"])
        self.assertEqual("v2", settings["section1/key2"])
