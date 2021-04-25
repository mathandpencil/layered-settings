import logging
import os
from .base_loader import BaseLoader


logger = logging.getLogger(__name__)


class EnvLoader(BaseLoader):
    """ Load from the os.environ.  Pass a format string containing {section} and {key} markers, such as
    'APP__{section}__{key}' or just '{key}'.  Defaults to a case-insensitive search through environment variables,
    since env vars are typically uppercase and sections are typically lowercase, plus it's more Windows-friendly.
    Use is_case_sensitive=True to be case sensitive.""" 
    
    def __init__(self, format, is_case_sensitive=False):
        self.env_var_format = format
        self.is_case_sensitive = is_case_sensitive

    def get_setting(self, section, key):
        s = self.env_var_format.format(section=section, key=key)

        if self.is_case_sensitive:
           return os.environ[s]
        else:
            s = s.lower()
            for k, v in os.environ.items():
                if k.lower() == s:
                    return v
            raise KeyError(k)

    def __str__(self):
        return f"env var using {self.env_var_format}"
