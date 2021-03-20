import functools
import io
import logging
import os
import sys
from configparser import RawConfigParser

try:
    import boto3
except ImportError:
    boto3 = None


logger = logging.getLogger(__name__)


class BaseLoader:
    def __init__(self):
        pass

    def get_setting(self, section, key):
        raise NotImplementedError("must implement in subclass.")
