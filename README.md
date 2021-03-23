# layered-settings

`layered-settings` is a simple and configurable hierarchical settings library for Python, including Django, Flask, or any other
scripts that need settings from potentially a variety of sources. With it you can load
settings from the environment, Amazon's SSM, local configparser .ini files, and more.

## Installation

The package is available on pip as `layered-settings`. Run:

`pip install layered-settings`

If you want to use the AWS SSM layer, include the [ssm] extra:

`pip install layered-settings[ssm]`

then import via:

`from layered_settings import initialize_settings, loaders`

## Example Usage

```python
import os
from layered_settings import initialize_settings
from layered_settings import loaders

get_setting = initialize_settings(
    sources=[
        # Lowest priority is setting-defaults.ini.  All configuration values should be defaulted in here.
        # The `loaders.ConfigParserLoader` is optional - if you pass a string ending in .ini, it wraps it in
        # a `loaders.ConfigParserLoader` for you.
        loaders.ConfigParserLoader(os.path.join(SCRIPT_DIR, "setting-defaults.ini")),

        # Next priority is a "user" settings file.
        os.path.expanduser("~/.app-settings.ini"),

        # You can include a dictionary in the sources too...
        {
            "general": {"CLIENT_NAME": "client"},
            "email": {"EMAIL_HOST": "smtp.example.com", "EMAIL_PORT": 25},
        },

        # If we are able/willing to reach out to AWS, do so.  A `None` in the initialize_settings sources
        # will simply be ignored.
        loaders.SSMLoader(f"/app/stage/", aws_region="us-east-1") if ALLOW_SSM_CONFIGURATION else None,

        # Top priority -- env var in the format APP__section__key.
        loaders.EnvLoader("APP__{section}__{key}"),
    ]
)

DATABASE_HOST = get_setting("database", "DATABASE_HOST")
AWS_SECRET_KEY = get_setting("aws", "AWS_SECRET_KEY")
...
```

## Frameworks Supported

This library is tested using Python 3.x.
