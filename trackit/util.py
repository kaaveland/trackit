# coding=utf-8
# Copyright (c) 2013 Robin Kåveland Hansen
#
# This file is a part of trackit. It is distributed under the terms
# of the modified BSD license. The full license is available in
# LICENSE, distributed as part of this software.

"""
Utilities that happen to be useful for several modules in trackit.
"""

from functools import wraps
import inspect
import os
import codecs

def dumb_constructor(init_method):
    """Create a dumb constructor that wraps init method.

    This simply assigns all parameters provided to it to the instance it belongs to.
    Shamelessly stolen from:
    http://stackoverflow.com/questions/1389180/python-automatically-initialize-instance-variables
    """
    name = init_method.__name__
    if name != "__init__":
        raise ValueError("Misplaced dumb_constructor, expected __init__ but was {}".format(name))
    names, varargs, keywords, defaults = inspect.getargspec(init_method)
    @wraps(init_method)
    def wrapper(self, *args, **kargs):
        for name, arg in zip(names[1:], args) + kargs.items():
            setattr(self, name, arg)
        if defaults is not None:
            for i in range(len(defaults)):
                if not hasattr(self, names[-(i+1)]):
                    setattr(self, names[-(i+1)], defaults[i])
        init_method(self, *args, **kargs)
    return wrapper

class DefaultRepr(object):
    """Provide a somewhat sane __repr__ method for class that subclasses this."""

    def __repr__(self):
        """Returns a dict-like string of self, calling repr on attributes.

        This disregards attributes that are callable or start with an underscore."""

        eligible_attributes = [(name, value) for name, value in self.__dict__.items()
                               if not name.startswith("_") and not callable(value)]
        printed = ", ".join(["{}={}".format(name, repr(value)) for name, value in eligible_attributes])
        return "<{}({})>".format(self.__class__.__name__, printed)

def _expand(path):

    return os.path.abspath(os.path.expandvars(os.path.expanduser(path)))

class Path(object):

    def __init__(self, path):
        self.path = _expand(path)

    def __eq__(self, other):
        return isinstance(other, Path) and self.path == other.path

    @property
    def up(self):
        return self.__class__(os.path.dirname(self.path))

    def __repr__(self):
        return "<Path('{}')>".format(self.path)

    def join(self, other):
        return Path(os.path.join(self.path,
                                 other.path if isinstance(other, Path) else other))

    @property
    def basename(self):
        return os.path.basename(self.path)

    def open(self, mode='r', encoding=None):
        return codecs.open(self.path, mode=mode, encoding=encoding)
