import json
import logging
from .base_loader import BaseLoader

try:
    import boto3
except ImportError:
    boto3 = None


logger = logging.getLogger(__name__)


class SecretsManagerLoader(BaseLoader):
    def __init__(self, path, aws_region):
        if boto3 is None:
            raise Exception("To use Secrets Manager, please install the boto3 library.")

        self.path = path
        self.aws_region = aws_region
        self._settings = _load_from_secrets_manager(self.path, self.aws_region)

    def get_setting(self, section, key):
        return self._settings[f"{section}/{key}"]

    def __str__(self):
        return f"Secrets Manager Secret from {self.path} region {self.aws_region}"


def _load_from_secrets_manager(path, aws_region):
    """
    Return a dict of {section/key} -> value
    """
    secrets_manager_client = boto3.client("secretsmanager", region_name=aws_region)

    def get_secrets_by_path(next_token=None):
        """
        returns iterator of secrets matching the specified path
        """

        params = dict(
            IncludePlannedDeletion=False,
            Filters=[
                {
                    "Key": "name",
                    "Values": [
                        path,
                    ],
                },
            ],
            MaxResults=100,
            SortOrder="asc",
        )

        if next_token:
            params["NextToken"] = next_token
        return secrets_manager_client.list_secrets(**params)

    def secrets():
        next_token = None
        while True:
            response = get_secrets_by_path(next_token)
            secrets = response["SecretList"]
            if len(secrets) == 0:
                break
            for parameter in secrets:
                yield parameter
            if "NextToken" not in response:
                break
            next_token = response["NextToken"]

    _secrets = {}
    for secret in secrets():
        # Take the entire key and strip off the path prefix.
        # secret['Name'] will be eg /site/env/section/secret_key
        # and key might be like section/key
        # if the secret is a json object, we will flatten it and use the keys as the new "secret_key"
        # otherwise, the secret_key will remain intact and the plaintext value will assigned to it.
        arn = secret["ARN"]
        key = secret["Name"][len(path) :]
        secret_string = secrets_manager_client.get_secret_value(SecretId=arn)["SecretString"]
        try:
            secret = json.loads(secret_string)
            key = key.split("/")[0]
            for subkey, value in secret.items():
                _secrets[key + "/" + subkey] = value
        except json.JSONDecodeError:
            secret = secret_string
            _secrets[key] = secret

    return _secrets
