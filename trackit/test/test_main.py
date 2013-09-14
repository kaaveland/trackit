# coding=utf-8
# Copyright (c) 2013 Robin Kåveland Hansen
#
# This file is a part of trackit. It is distributed under the terms
# of the modified BSD license. The full license is available in
# LICENSE, distributed as part of this software.

import sys
import os
from trackit import util, main

SIMULATION_HOME = util.Path('.').join('trackit_simulation_home')

class TestMain(object):

    def del_file(self, path):
        try:
            os.unlink(SIMULATION_HOME.join(path).path)
        except OSError:
            pass

    def setup_method(self, meth):
        self.capture = util.CaptureIO()
        self.args = ["--home", SIMULATION_HOME.path]

    def teardown_method(self, meth):
        self.del_file('db.sqlite')
        self.del_file('config')
        try:
            os.rmdir(SIMULATION_HOME.path)
        except OSError:
            pass

    def run(self, *args):
        """Runs trackit, sends in args and self.args."""
        main.main(self.args + list(args))

    def got_line_with(self, part):
        return any(part in line for line in self.capture.out.split('\n'))

    def got_err(self, part):
        return any(part in line for line in self.capture.err.split('\n'))

    def test_prints_help(self):
        with self.capture:
            self.run('--help')
        assert self.got_line_with('usage:')

    def test_starts_tracker(self):
        with self.capture:
            self.run('start', 'bugfixing')
        assert self.got_line_with("Tracking 'bugfixing'.")

    def test_status(self):
        with self.capture:
            self.run('status')
        assert self.got_line_with('Not tracking.')
        with self.capture:
            self.run('start', 'task')
        assert self.got_line_with("Tracking 'task'.")

    def test_stop(self):
        with self.capture:
            self.run('stop')
        assert self.got_line_with('Nothing to stop.')
        with self.capture:
            self.run('start', 'running')
        assert self.got_line_with("Tracking 'running'.")
        with self.capture:
            self.run('stop')
        assert self.got_line_with("Stopped 'running' after.")

    def test_invalid_command(self):
        with self.capture:
            self.run('fooeuaoeu')
        assert self.got_err_with('usage:')
