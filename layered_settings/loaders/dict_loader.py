import logging
from .base_loader import BaseLoader


logger = logging.getLogger(__name__)


class DictLoader(BaseLoader):
    def __init__(self, data):

        self.data = data

    def get_setting(self, section, key):
        return self.data[section][key]

    def __str__(self):
        return f"dict source"

