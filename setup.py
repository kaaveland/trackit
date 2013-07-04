# coding=utf-8
# Copyright (c) 2013 Robin Kåveland Hansen
#
# This file is a part of trackit. It is distributed under the terms
# of the modified BSD license. The full license is available in
# LICENSE, distributed as part of this software.

from setuptools import setup

setup(

    name = "trackit",
    version = "0.1.0",

    install_requires = [
    ],

    tests_require = [
        "py-test"
    ],

    packages = [
        "trackit",
    ],

    author = "Robin Kåveland Hansen",
    description = "Time tracking application.",

    license = "BSD",
    classifiers = [
        "License :: OSI Approved :: BSD License",
        "Development Status :: 2 - Pre-Alpha",
        "Programming Language :: Python :: 2.6",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3.2",
    ],
)
