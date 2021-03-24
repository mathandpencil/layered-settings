import functools
import io
import logging
import os
import sys
from configparser import RawConfigParser
from .loaders import BaseLoader, ConfigParserLoader, DictLoader, CallableLoader

logger = logging.getLogger(__name__)

def initialize_settings(sources):
    _sources = []

    for source in reversed(sources):
        if source is None:
            continue

        try:
            if isinstance(source, BaseLoader):
                _sources.append(source)
                logger.debug(f"Registered {source}.")

            elif isinstance(source, dict):
                _sources.append(DictLoader(source))
                logger.debug(f"Registered dictionary source.")

            elif callable(source):
                _sources.append(CallableLoader(source))
                logger.debug(f"Registered callable source {source}.")

            else:
                if os.path.exists(source):
                    if isinstance(source, str) and source.endswith(".ini"):
                        _sources.append(ConfigParserLoader(source))
                    logger.debug(f"Registered .ini filename source from {source}")
                else:
                    # print(f"Did not register .ini filename source from {source}, file does not exist.")
                    pass
        except Exception as exc:
            logger.exception(f"Exception while registering source {source}, quitting: {exc}")

            raise

    return functools.partial(_get_config_setting, sources, _sources)


def _get_config_setting(initial_sources, sources, section, key, is_sensitive=True):
    """ Iterate through sources and return first-available. """

    for ctr, (source_desc, source) in enumerate(zip(initial_sources, sources)):
        try:
            ret = source.get_setting(section, key)
            if is_sensitive:
                logger.info(f"[{section}] {key} was set to XXXX from source {ctr+1} ({source}).")
            else:
                logger.info(f"[{section}] {key} was set to {ret} from source {ctr+1} ({source}).")

            return ret
        except KeyError:
            continue
        except Exception as exc:
            logger.exception(f"Exception while getting config [{section}] {key} from {source_desc}, skipping: {exc}")
            continue
    logger.warning(f"Failed to find [{section}] {key} in {initial_sources}.")
    raise KeyError(key)


def parse_bool(b):
    """ Useful for environment variables, intelligently converts any reasonable string to a Python bool,
    or None if it is None or empty/whitespace string."""

    if b is None:
        return None
    if b is True:
        return True
    if b is False:
        return False
    if b.strip() == "":
        return None
    b = str(b).upper()[0]
    if b in ["Y", "1", "T"]:
        return True
    if b in ["N", "0", "F"]:
        return False
    raise ValueError(b)
