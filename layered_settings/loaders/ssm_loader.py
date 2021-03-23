import logging
from .base_loader import BaseLoader

try:
    import boto3
except ImportError:
    boto3 = None


logger = logging.getLogger(__name__)


class SSMLoader(BaseLoader):
    def __init__(self, path, aws_region):
        if boto3 is None:
            raise Exception("To use SSMPath, please install the boto3 library.")

        self.path = path
        self.aws_region = aws_region
        self._settings = _load_from_ssm(self.path, self.aws_region)

    def get_setting(self, section, key):
        return self._settings[f"{section}/{key}"]

    def __str__(self):
        return f"SSM from {self.path} region {self.aws_region}"


def _load_from_ssm(path, aws_region):
    """ Return a dict of {section/key} -> value """

    # For production (aka ECS and docker) read from SSM store.
    ssm = boto3.client("ssm", region_name=aws_region)

    def get_parameters_by_path(next_token=None):
        params = {"Path": path, "Recursive": True, "WithDecryption": True}
        if next_token is not None:
            params["NextToken"] = next_token
        return ssm.get_parameters_by_path(**params)

    def parameters():
        next_token = None
        while True:
            response = get_parameters_by_path(next_token)
            parameters = response["Parameters"]
            if len(parameters) == 0:
                break
            for parameter in parameters:
                yield parameter
            if "NextToken" not in response:
                break
            next_token = response["NextToken"]

    _ssm_parameters = {}
    _using_local_config = False
    for param in parameters():
        # Take the entire key and strip off the path prefix.
        # param['Name'] will be eg /site/env/section/key
        # and ssm_key might be like section/key
        ssm_key = param["Name"][len(path) :]
        _ssm_parameters[ssm_key] = param["Value"]

    return _ssm_parameters
