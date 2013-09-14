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
from util import Path, ChainMap

default = {
    'database': Path('$HOME').join('.trackitdb').path,
    'encoding': 'utf-8'
}

def dump_default(file_):
    json.dump(default, file_, indent=2)
