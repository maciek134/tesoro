#!/usr/bin/env python3
# -*- encoding: utf-8 -*-
from __future__ import absolute_import, print_function

import io
from os.path import dirname, join
from setuptools import find_packages, setup

def read(*names, **kwargs):
    return io.open(
        join(dirname(__file__), *names),
        encoding=kwargs.get("encoding", "utf-8")
    ).read()

setup(
    name = "tesoro",
    version = "0.1.0",
    license = "GPLv3",
    description = "Library for interfacing with Tesoro hardware",
    author = "Maciej Sopyło",
    author_email = "maciek134@gmail.com",
    url = "https://github.com/maciek134/tesoro",
    packages = find_packages("src"),
    package_dir = { '': "src" },
    long_description = read("README.md"),
    classifiers = [
        "Development Status :: 3 - Alpha",
        "Programming Language :: Python :: 3 :: Only",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Operating System :: POSIX :: Linux", # WTF PyPi? Where is GNU/Linux???
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Intended Audience :: Developers"
    ],
    install_requires = [
        "libusb1"
    ]
)
