import functools
import io
import logging
import os
import sys
from configparser import RawConfigParser
from .loaders import BaseLoader, ConfigParserLoader

logger = logging.getLogger(__name__)


def initialize_settings(sources):
    _sources = []

    for source in reversed(sources):
        if source is None:
            continue

        try:
            if isinstance(source, BaseLoader):
                _sources.append(source.get_setting)
                logger.debug(f"Registered {source}.")

            elif isinstance(source, dict):
                _sources.append(lambda section, key: source[section][key])
                logger.debug(f"Registered dictionary source.")

            elif callable(source):
                _sources.append(source)
                logger.debug(f"Registered callable source {source}.")

            else:
                if os.path.exists(source):
                    if isinstance(source, str) and source.endswith(".ini"):
                        _sources.append(ConfigParserLoader(source).get_setting)
                    logger.debug(f"Registered .ini filename source from {source}")
                else:
                    # print(f"Did not register .ini filename source from {source}, file does not exist.")
                    pass
        except Exception as exc:
            logger.debug(f"Exception while registering source {source}, quitting: {exc}")

            sys.exit(1)

    return lambda section, key: _get_config_setting(sources, _sources, section, key)


def _get_config_setting(initial_sources, sources, section, key):
    """ Iterate through sources and return first-available. """

    for source_desc, source in zip(initial_sources, sources):
        try:
            ret = source(section, key)
            print(f"[{section}] {key} is set to {ret}.")
            return ret
        except KeyError:
            continue
        except Exception as exc:
            logger.exception(f"Exception while getting config [{section}] {key} from {source_desc}, skipping: {exc}")
            continue
    print(f"Failed to find [{section}] {key} in {initial_sources}.")
    raise KeyError(key)


def parse_bool(b):
    """ Useful for environment variables, intelligently converts any reasonable string to a Python bool. """

    if b is None:
        return None
    if b == "":
        return None
    if b is True:
        return True
    if b is False:
        return False
    b = str(b).upper()[0]
    if b in ["Y", "1", "T"]:
        return True
    if b in ["N", "0", "F"]:
        return False
    raise ValueError(b)
