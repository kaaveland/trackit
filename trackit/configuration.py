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
import os
import sys
import codecs
import sys

if sys.version_info.major == 3:
    unicode = str

def _expand(path):
    return os.path.expandvars(os.path.expanduser(path))

def _abs(path):
    return os.path.abspath(path)

NOTIFICATION_INTERVAL = "notification-interval"
DATABASE_LOCATION = "database-location"
ENCODING = "encoding"
DATETIME_FORMAT = "datetime-format"
TIME_FORMAT = "time-format"
DATE_FORMAT = "date-format"

CONFIGURATION_FILE_LOCATIONS = [
    '/etc/trackit.conf',
    _expand('$HOME/.trackit/conf')
]

_time_format = "%H:%M"
_date_format = "%Y-%m-%d"

DEFAULT = {
    NOTIFICATION_INTERVAL: 15,
    DATABASE_LOCATION: "$HOME/.trackit/data.sqlite",
    ENCODING: "utf-8",
    TIME_FORMAT: _time_format,
    DATE_FORMAT: _date_format,
    DATETIME_FORMAT: _date_format + " " + _time_format
}


def generate_default_configuration():
    """Generates default configuration string that can be written to a file.
    """
    return json.dumps(DEFAULT, indent=2)

def read_configuration(path):
    """Read configuration into a dictionary from a json formatted file.

    Arguments:
    - `path`: path to a json-formatted file.
    """
    actual_path = _abs(_expand(path))
    with codecs.open(actual_path, encoding="utf-8") as configuration_file:
        return _read_config(fp)

def _read_config(fp):
    content = json.load(fp)
    for key, value in content.items():
        if isinstance(value, unicode) and "$" in value:
            content[key] = _expand(value)
    return content

def get_trackit_configuration():
    configuration = {}
    configuration.update(DEFAULT)
    for path in CONFIGURATION_FILE_LOCATIONS:
        configuration.update(read_configuration(path))
    return configuration
