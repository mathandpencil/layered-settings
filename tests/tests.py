import os
import unittest
from unittest.mock import patch

from layered_settings import initialize_settings
from layered_settings import loaders

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
