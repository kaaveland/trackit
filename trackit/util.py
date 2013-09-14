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
from cStringIO import StringIO
import inspect
import os
import codecs
import itertools
import sys


def dumb_constructor(init_method):
    """Create a dumb constructor that wraps init method.

    This simply assigns all parameters provided to it to the instance
    it belongs to. Shamelessly stolen from:
    http://stackoverflow.com/questions/1389180/\
    python-automatically-initialize-instance-variables
    """
    name = init_method.__name__
    if name != "__init__":
        raise ValueError("Misplaced dumb_constructor,"
                         "expected __init__ but was {}".format(name))
    names, _, _, defaults = inspect.getargspec(init_method)
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
    """Provide a somewhat sane __repr__ method for class that subclasses."""

    def __repr__(self):
        """Returns a dict-like string of self, calling repr on attributes.

        This disregards attributes that are callable or start with an
        underscore."""

        eligible_attributes = [(name, value) for name, value in
                               self.__dict__.items()
                               if not name.startswith("_") and
                               not callable(value)]
        printed = ", ".join(["{}={}".format(name, repr(value)) for
                             name, value in eligible_attributes])
        return "<{}({})>".format(self.__class__.__name__, printed)

def _expand(path):
    """Performs path expansions on argument using os.path functions."""

    return os.path.abspath(os.path.expandvars(os.path.expanduser(path)))

class Path(DefaultRepr):
    """A path on the file system."""

    def __init__(self, path):
        self.path = _expand(path)

    def __eq__(self, other):
        return isinstance(other, Path) and self.path == other.path

    @property
    def up(self):
        """Uses os.path.dirname to go one level up in the file system tree."""
        return self.__class__(os.path.dirname(self.path))

    def join(self, other):
        """Use os.path.join to concatenate a path or name onto this path."""
        return Path(os.path.join(self.path, other.path
                                 if isinstance(other, Path) else other))

    @property
    def basename(self):
        """The basename of this path."""
        return os.path.basename(self.path)

    def open(self, mode='r', encoding=None):
        """Open as a file at location using codecs.open."""
        return codecs.open(self.path, mode=mode,
                           encoding=encoding)

    def exists(self):
        """Test whether this path exists. Present for tests."""
        return os.path.exists(self.path)

    def makedir(self):
        """Make directory at this path. Creates all intermediate paths."""
        return os.makedirs(self.path)

class ChainMap(DefaultRepr):
    """Minimalistic chainmap that delegates to a collection of dictionaries.

    Useful for prioritized lookups, e.g. settings."""

    def __init__(self, *dicts):
        self.dicts = dicts

    def __getitem__(self, key):
        for dct in self.dicts:
            try:
                return dct[key]
            except KeyError:
                continue
        raise KeyError('no such item {}'.format(repr(key)))

    def get(self, key, default=None):
        try:
            return self[key]
        except KeyError:
            return default

    def __iter__(self):
        return iter(set(itertools.chain(*self.dicts)))

    def items(self):
        for key in self:
            yield (key, self[key])

    def __contains__(self, key):
        return any(key in dct for dct in self.dicts)

    def __nonzero__(self):
        return any(self.dicts)

    def __len__(self):
        return len(iter(self))

class CaptureIO(object):
    """Context managed capture of stdin/stderr/stdout."""

    @property
    def out(self):
        return self.stdout.getvalue()

    @property
    def err(self):
        return self.stderr.getvalue()

    def __init__(self, stdin=None):
        """Optionally pass in content of fake stdin."""
        self.stdout = StringIO()
        self.stderr = StringIO()
        self.stdin = StringIO() if stdin is None else StringIO(stdin)

    def __enter__(self):

        self.old_stdout = sys.stdout
        sys.stdout = self.stdout
        self.old_stdin = sys.stdin
        sys.stdin = self.stdin
        self.old_stderr = sys.stderr
        sys.stderr = self.stderr

    def __exit__(self, *exc_info):
        sys.stdout = self.old_stdout
        sys.stdin = self.old_stdin
        sys.stderr = self.old_stderr
