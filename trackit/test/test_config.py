# coding=utf-8
# Copyright (c) 2013 Robin Kåveland Hansen
#
# This file is a part of trackit. It is distributed under the terms
# of the modified BSD license. The full license is available in
# LICENSE, distributed as part of this software.

from cStringIO import StringIO
from ..configuration import DEFAULT, dump_settings, load_settings

def test_settings_encoder():
    file_ = StringIO()
    dump_settings(DEFAULT, file_)
    assert file_.getvalue()

def test_default_config_should_have_all_keys():
    assert 'home' in DEFAULT
    assert 'database' in DEFAULT
    assert 'encoding' in DEFAULT

def test_dumping_settings_should_result_in_json_parsable_file():
    file_ = StringIO()
    dump_settings(DEFAULT, file_)
    settings = load_settings(StringIO(file_.getvalue()))
    assert settings == DEFAULT
