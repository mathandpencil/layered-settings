import logging
from .base_loader import BaseLoader


logger = logging.getLogger(__name__)


class CallableLoader(BaseLoader):
    def __init__(self, func):
        self.func = func

    def get_setting(self, section, key):
        return self.func(section, key)

    def __str__(self):
        return f"dict source"

