# coding=utf-8
# Copyright (c) 2013 Robin Kåveland Hansen
#
# This file is a part of trackit. It is distributed under the terms
# of the modified BSD license. The full license is available in
# LICENSE, distributed as part of this software.
"""
Configuration file management for trackit.
"""

import json
from trackit.util import Path, ChainMap

HOME = Path('$HOME').join('.trackit')

DEFAULT = {
    'database': 'db.sqlite',
    'encoding': 'utf-8'
}


class SettingsEncoder(json.JSONEncoder):
    """Specialized jsonencoder for trackit settings."""
    def default(self, obj):
        """This will encode Path instances to their path attribute."""
        if isinstance(obj, Path):
            return obj.path
        return json.JSONEncoder.default(self, obj)


def decode_path(dct):
    """json object_hook to decode into Path."""
    if 'home' in dct:
        dct['home'] = Path(dct['home'])
    return dct


def load_settings(file_):
    """Load trackit settings from file_ which is a file-like."""
    return json.load(file_, object_hook=decode_path)


def dump_settings(settings, file_):
    """Dump settings to file_, which is a file-like."""
    file_.write(SettingsEncoder(indent=2).encode(settings))

def load_user_settings(home=HOME):
    """Loads settings from users home folder."""
    config = home.join('config')
    try:
        with config.open() as inf:
            return load_settings(inf)
    except IOError:
        create_home(home)
        with config.open() as inf:
            return load_settings(inf)

def load_system_settings():
    """Loads settings from system settings catalog."""
    system = Path('/').join('etc').join('trackit')
    try:
        with system.open() as inf:
            return load_settings(inf)
    except IOError:
        return DEFAULT

def create_home(target=HOME):
    """This will create the users trackit home and settings file if
    necessary."""
    target.makedir()
    config = target.join('config')
    with config.open('ab') as outf:
        dump_settings(DEFAULT, outf)

def load_configuration(home=HOME):
    """Loads configuration into a ChainMap.

    User settings has higher priority than system settings."""
    return ChainMap(load_user_settings(home), load_system_settings())
