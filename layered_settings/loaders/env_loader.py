import logging
import os
from .base_loader import BaseLoader


logger = logging.getLogger(__name__)


class EnvLoader(BaseLoader):
    def __init__(self, format):
        self.env_var_format = format

    def get_setting(self, section, key):
        s = self.env_var_format.format(section=section, key=key)
        return os.environ[s]

    def __str__(self):
        return f"env var using {self.env_var_format}"
