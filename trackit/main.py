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
from trackit.exceptions import ArgumentParsingException

def configured(command):
    """Wrap command in a function that passes in the trackit configuration
    loaded from the file system."""
    @wraps(command)
    def wrapper(options):
        config = configuration.load_configuration(options.home)
        db = configuration.get_db(config)
        out = command(config, options, data.Data(db))
        db.commit()
        return out
    return wrapper

@configured
def stop(configuration, options, data):
    in_progress = data.intervals.in_progress()
    if in_progress is None:
        print 'Nothing to stop.'
    else:
        stopped = data.intervals.stop(in_progress.task)
        print "Stopped '{}' after {} seconds".format(stopped.task.name, stopped.duration)
    return 0

@configured
def status(configuration, options, data):
    in_progress = data.intervals.in_progress()
    if in_progress is None:
        print 'Not tracking.'
    else:
        print "Tracking '{}' for {} seconds so far.".format(in_progress.task.name, in_progress.duration)
    return 0

@configured
def start(configuration, options, data):
    tasks = data.tasks.by_name(options.task[0])
    if len(tasks) > 1:
        print '{} is ambigous, multiple entries:'
        print ' '.join([task.name for task in tasks])
    elif not tasks:
        task = data.tasks.create(options.task[0])
    else:
        task = tasks[0]
    data.intervals.start(task)
    print "Tracking '{}'.".format(task.name)
    return 0

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
        return options.func(options)
    except ArgumentParsingException, e:
        return e.message

if __name__ == '__main__':
    exit_code = main(sys.argv[1:])
    sys.exit(exit_code)
