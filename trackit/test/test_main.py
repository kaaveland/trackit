# coding=utf-8
# Copyright (c) 2013 Robin Kåveland Hansen
#
# This file is a part of trackit. It is distributed under the terms
# of the modified BSD license. The full license is available in
# LICENSE, distributed as part of this software.

import sys
import os
from trackit import util, main
from trackit.exceptions import ArgumentParsingException

SIMULATION_HOME = util.Path('.').join('trackit_simulation_home')

class TestMain(object):

    def del_file(self, path):
        try:
            os.unlink(SIMULATION_HOME.join(path).path)
        except OSError:
            pass

    @property
    def out(self):
        return self.capture.out

    @property
    def err(self):
        return self.capture.err

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
        return main.main(self.args + list(args))

    def test_prints_help(self):
        with self.capture:
            self.run('--help')
        assert 'usage:' in self.out

    def test_starts_tracker(self):
        with self.capture:
            assert self.run('start', 'bugfixing') == 0
        assert "Tracking 'bugfixing'." in self.out

    def test_status(self):
        with self.capture:
            assert self.run('status') == 0
        assert 'Not tracking.' in self.out
        with self.capture:
            assert self.run('start', 'task') == 0
        with self.capture:
            assert self.run('status') == 0
        assert "Tracking 'task' for" in self.out

    def test_stop(self):
        with self.capture:
            assert self.run('stop') == 0
        assert 'Nothing to stop.' in self.out
        with self.capture:
            assert self.run('start', 'running') == 0
        assert "Tracking 'running'." in self.out
        with self.capture:
            assert self.run('stop') == 0
        assert "Stopped 'running' after" in self.out

    def test_invalid_command(self):
        with self.capture:
            assert self.run('fooeuaoeu') != 0
        assert 'usage:' in self.err
