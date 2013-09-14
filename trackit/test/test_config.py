# coding=utf-8
# Copyright (c) 2013 Robin Kåveland Hansen
#
# This file is a part of trackit. It is distributed under the terms
# of the modified BSD license. The full license is available in
# LICENSE, distributed as part of this software.
import json
import StringIO
from ..configuration import default, dump_default

def test_default_config_should_have_all_keys():
    assert 'database' in default
    assert 'encoding' in default

def test_dumping_default_should_result_in_json_parsable_file():
    file_ = StringIO.StringIO()
    dump_default(file_)
    settings = json.loads(file_.getvalue())
    assert 'database' in default
    assert 'encoding' in default
