#!/usr/bin/env python

import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="layered-settings",
    version="1.0.3",
    description="Flexible, simple, extensible settings loader from environment, AWS SSM, configparser .ini, and more.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/mathandpencil/layered-settings",
    author="Scott Stafford",
    author_email="scott.stafford+layered@gmail.com",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    zip_safe=False,
    extras_require={
        "ssm": ["boto3"],
    },
)
