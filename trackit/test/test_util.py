# coding=utf-8
# Copyright (c) 2013 Robin Kåveland Hansen
#
# This file is a part of trackit. It is distributed under the terms
# of the modified BSD license. The full license is available in
# LICENSE, distributed as part of this software.

import pytest
import os

from ..util import dumb_constructor, DefaultRepr, Path

class TestDumbConstructor(object):
    def test_should_accept_methods_named_init(self):
        @dumb_constructor
        def __init__():
            pass

    def test_should_not_accept_methods_not_named_init(self):
        with pytest.raises(ValueError):
            @dumb_constructor
            def not_init():
                pass

    def test_should_assign_arguments_to_first_argument(self):
        class TestClass(object):
            @dumb_constructor
            def __init__(obj, a, b, c=3):
                pass
        test_candidate = TestClass("a", c="c", b="b")
        assert test_candidate.a == "a"
        assert test_candidate.b == "b"
        assert test_candidate.c == "c"

class TestDefaultRepr(object):

    def test_repr_should_mention_all_variable_names(self):
        class TestClass(DefaultRepr):
            @dumb_constructor
            def __init__(self, weird_name, foobar):
                pass
        shown = repr(TestClass(3, 9))
        assert "weird_name" in shown
        assert "foobar" in shown

    def test_repr_should_mention_all_variable_values(self):
        class TestClass(DefaultRepr):
            @dumb_constructor
            def __init__(self, a, b):
                pass
        shown = repr(TestClass("foobar", 314))
        assert "foobar" in shown
        assert "314" in shown

    def test_repr_should_disregard_callable_members_and_members_starting_with_underscore(self):
        class TestClass(DefaultRepr):
            @dumb_constructor
            def __init__(self, _disregard, some_function):
                pass
        shown = repr(TestClass("should_not_be_present", lambda _: None))
        assert "_disregard" not in shown
        assert "should_not_be_present" not in shown
        assert "some_function" not in shown

class TestPath(object):

    def test_path_should_have_path_attribute(self):

        path = Path('.')
        assert path.path is not None

    def test_path_should_be_absolute(self):

        path = Path('.')
        assert path.path == os.path.abspath('.')

    def test_path_should_expand_tilde_and_home(self):

        left, right = Path('~'), Path('$HOME')
        assert left.path == right.path

    def test_path_should_support_equals_with_path(self):

        assert Path('.') == Path('.')

    def test_going_up_from_child_of_root_should_give_root(self):

        assert Path('/tmp').up == Path('/')

    def test_path_should_have_sensible_repr(self):

        assert repr(Path('/')) == "<Path('/')>"

    def test_joining_path_to_root_should_yield_child_of_root(self):

        assert Path('/').join('tmp').up == Path('/')

    def test_joining_path_to_root_should_yield_path_with_basename_of_joinee(self):
        assert Path('/').join('tmp').basename == 'tmp'

    def test_should_be_able_to_open_this_file_in_read_mode_and_read_unicode(self):
        with Path(__file__).open(encoding='utf-8') as inf:
            assert isinstance(inf.readline(), unicode)
