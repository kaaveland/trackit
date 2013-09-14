# coding=utf-8
# Copyright (c) 2013 Robin Kåveland Hansen
#
# This file is a part of trackit. It is distributed under the terms
# of the modified BSD license. The full license is available in
# LICENSE, distributed as part of this software.

"""
Application interfaces to trackit.
"""

import sys
import argparse
from functools import wraps

from trackit import configuration, util, data

def configured(command):
    """Wrap command in a function that passes in the trackit configuration
    loaded from the file system."""
    @wraps(command)
    def wrapper(options):
        config = configuration.load_configuration(options.home)

        return command(config, options)
    return wrapper

@configured
def stop(configuration, options):
    print "Nothing to stop."

@configured
def status(configuration, options):
    print "Not tracking."

@configured
def start(configuration, options):
    pass

class ArgumentParsingException(Exception): pass

class TrackitArgparser(argparse.ArgumentParser):
    """Using this to prevent argparse from sending SystemExit.

    It's just not very testable."""

    def exit(self, status=0, message=None):
        try:
            argparse.ArgumentParser.exit(self, status, message)
        except SystemExit:
            raise ArgumentParsingException(status)

parser = TrackitArgparser(
    description="CLI interface to the trackit timetracking application."
)

parser.add_argument("-H", "--home", action='store')
subparsers = parser.add_subparsers(title="Commands")

stop_parser = subparsers.add_parser('stop', help='Stop tracking')
stop_parser.set_defaults(func=stop)

status_parser = subparsers.add_parser('status', help='Show status')
status_parser.set_defaults(func=status)

start_parser = subparsers.add_parser('start', help='Start tracking something')
start_parser.add_argument("task", nargs=1, action='store',
                          help='Name of the task you wish to track')
start_parser.set_defaults(func=start)


def main(args):
    """Entry point for trackit."""
    try:
        options = parser.parse_args(args)
        options.func(options)
        return 0
    except ArgumentParsingException, e:
        return e.message

if __name__ == '__main__':
    exit_code = main(sys.argv[1:])
    sys.exit(exit_code)
