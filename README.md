# layered-settings

`layered-settings` is a simple and configurable hierarchical settings library for Python, including Django, Flask, or any other
scripts that need settings from potentially a variety of sources. With it you can load
settings from the environment, Amazon's SSM, local configparser .ini files, and more.

## Installation

The package is available on pip as [layered-settings][layered-settings]. Run:

`pip install layered-settings`

then import via:

`from layered_settings import initialize_settings, `

## A Usage Scenario

## Example Usage

```python
from layered_settings import initialize_settings
from layered_settings import loaders

get_setting = initialize_settings(
    sources=[
        # Lowest priority is setting-defaults.ini.  All configuration values should be defaulted in here.
        loaders.ConfigParserLoader(os.path.join(SCRIPT_DIR, "inifiles", "setting-defaults.ini")),
        # The `loaders.ConfigParserLoader` is optional - if you pass a string ending in .ini, it wraps it in
        # a `loaders.ConfigParserLoader` for you.
        os.path.join(SCRIPT_DIR, "inifiles", "setting-overrides.ini"),
        # If ENV is set and we are able/willing to reach out to AWS, do so..
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
