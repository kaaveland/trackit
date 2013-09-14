# coding=utf-8
# Copyright (c) 2013 Robin Kåveland Hansen
#
# This file is a part of trackit. It is distributed under the terms
# of the modified BSD license. The full license is available in
# LICENSE, distributed as part of this software.

import os

from cStringIO import StringIO
from trackit.util import Path
from trackit.configuration import (
    DEFAULT, load_user_settings, dump_settings, load_settings, create_home,
    load_system_settings, load_configuration
)

target = Path('trackit_test_configuration')
config = target.join('config')

def teardown_function(func):
    if config.exists():
        os.unlink(config.path)
    if target.exists():
        os.rmdir(target.path)

def test_settings_encoder():
    file_ = StringIO()
    dump_settings(DEFAULT, file_)
    assert file_.getvalue()

def test_default_config_should_have_all_keys():
    assert 'database' in DEFAULT
    assert 'encoding' in DEFAULT

def test_dumping_settings_should_result_in_json_parsable_file():
    file_ = StringIO()
    dump_settings(DEFAULT, file_)
    settings = load_settings(StringIO(file_.getvalue()))
    assert settings == DEFAULT

def test_create_home():
    assert not target.exists()
    create_home(target)
    assert target.exists()
    assert config.exists()
    with config.open() as inf:
        assert load_settings(inf) == DEFAULT

def test_load_user_settings_when_home_does_not_exists():
    assert not target.exists()
    assert load_user_settings(target) == DEFAULT

def test_load_user_settings_when_home_exists():
    target.makedir()
    with config.open('a') as outf:
        settings = DEFAULT.copy()
        settings['foo'] = 3
        dump_settings(settings, outf)
        actual = load_user_settings(target)
        assert settings == actual

def test_system_settings_should_be_default_when_file_doesnt_exist():
    assert load_system_settings() == DEFAULT

def test_user_configuration_overrides_system_configuration():
    settings = {'database': 'foobar'}
    target.makedir()
    with config.open('a') as outf:
        dump_settings(settings, outf)
    merged = load_configuration(target)
    assert merged['database'] == 'foobar'
    assert merged['encoding'] == 'utf-8'
