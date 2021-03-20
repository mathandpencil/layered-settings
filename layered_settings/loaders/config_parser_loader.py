import functools
import logging
import configparser
import os
from .base_loader import BaseLoader


logger = logging.getLogger(__name__)


class ConfigParserLoader(BaseLoader):
    def __init__(self, path, ignore_if_missing=False):
        self.path = path
        if os.path.exists(self.path):
            self.config = configparser.ConfigParser()
            self.config.read(self.path)
            # _get = functools.partial(_get_from_config_parser, cp)
            logger.debug(f"Registered .ini filename source from {self.path}")
        else:
            if not ignore_if_missing:
                raise FileNotFoundError(self.path)

    def get_setting(self, section, key):
        return _get_from_config_parser(self.config, section, key)

    def __str__(self):
        return f"ConfigParser from {self.path}"


def _get_from_config_parser(cp, section, key):
    # print(f"Checking {cp} for {section} {key}...")
    try:
        return cp.get(section, key)
    except:
        raise KeyError(section + "_" + key)
