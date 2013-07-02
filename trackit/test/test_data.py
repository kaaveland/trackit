# coding=utf-8
# Copyright (c) 2013 Robin Kåveland Hansen
#
# This file is a part of trackit. It is distributed under the terms
# of the modified BSD license. The full license is available in
# LICENSE, distributed as part of this software.

import pytest
import sqlite3

from ..data import Task, Tasks, TaskInterval, TaskIntervals

class TestTasks(object):

    def setup(self):
        self.conn = sqlite3.connect(":memory:")
        self.tasks = Tasks(self.conn)
        self.conn.execute("INSERT INTO TASK(NAME, DESCRIPTION) VALUES(?, ?)", ("Test", "Test"))
        self.conn.execute("INSERT INTO TASK(NAME, DESCRIPTION) VALUES(?, ?)", ("Wat", "blank"))

    def teardown(self):
        self.conn.close()

    def test_should_find_previously_inserted_tasks(self):
        tasks = self.tasks.all()
        assert len(tasks) == 2
        first = tasks[0]
        assert first.name == "Test" and first.description == "Test" and first.task_id == 1
        second = tasks[1]
        assert second.name == "Wat" and second.description == "blank" and second.task_id == 2

    def test_should_find_previously_inserted_by_name(self):
        results = self.tasks.by_name("Wat")
        assert len(results) == 1
        assert results[0].name == "Wat"

    def test_should_be_more_rows_in_database_after_create(self):
        new = self.tasks.create("Nonsense", "What's this")
        assert isinstance(new, Task)
        assert new.task_id == 3 and new.name == "Nonsense" and new.description == "What's this"
        assert len(self.tasks.all()) == 3

    def test_should_raise_exception_when_attempting_to_retrieve_non_existant_task(self):
        with pytest.raises(KeyError):
            self.tasks.by_id(9)

    def test_should_retrieve_previously_inserted_task_by_id(self):
        task = self.tasks.by_id(1)
        assert task.name == "Test" and task.description == "Test"

    def test_updates_should_be_reflected_in_database(self):
        task = self.tasks.by_id(1)
        task.name = "Not test"
        task.description = "descr"
        self.tasks.update(task)
        in_db = self.tasks.by_id(1)
        assert in_db.name == "Not test" and in_db.description == "descr"

class TestTaskIntervals(object):

    def setup(self):
        self.tt = TestTasks()
        self.tt.setup
        self.task_intervals = TaskIntervals(self.tt.conn)

    def teardown(self):
        self.tt.teardown()
