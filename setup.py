#!/usr/bin/env python

from distutils.core import setup

setup(
    name="noip-renewer",
    version="0.1.0",
    description="No-ip renewer",
    author="Shaun Ostoic",
    author_email="ostoic@proton.me",
    packages=[
        "noip_renewer",
    ],
    package_dir={"": "src"},
)
