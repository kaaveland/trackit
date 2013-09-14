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

HOME = Path('$HOME').join('.trackit'),

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
