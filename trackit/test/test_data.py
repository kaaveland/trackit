# coding=utf-8
# Copyright (c) 2013 Robin Kåveland Hansen
#
# This file is a part of trackit. It is distributed under the terms
# of the modified BSD license. The full license is available in
# LICENSE, distributed as part of this software.

import pytest
import sqlite3
import time

from ..data import Task, Tasks, TaskInterval, TaskIntervals, ClosesCursor, TooManyTasksInProgress, InconsistentTaskIntervals

def test_auto_closing_cursor_closes_cursor():
    class ClosableMock(object):
        def __init__(self):
            self.closed = False
        def close(self):
            self.closed = True
    mock = ClosableMock()
    class ConnectionMock(object):
        def cursor(self):
            return mock
    class HasConnection(ClosesCursor):
        @property
        def conn(self):
            return ConnectionMock()
    with HasConnection().cursor() as cursor:
        pass
    assert mock.closed

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
        self.tt.setup()
        conn = self.tt.conn
        self.tasks = self.tt.tasks
        self.task_intervals = TaskIntervals(conn)
        now = time.time()
        conn.execute("INSERT INTO TASKINTERVAL(TASK, START_TIME, STOP_TIME) VALUES(?, ?, ?)",
                     (1, now - 15, now - 5))

    def teardown(self):
        self.tt.teardown()

    def test_should_be_able_to_find_interval_for_preexisting_task(self):
        task = self.tasks.by_id(1)
        intervals = self.task_intervals.for_task(task)
        assert len(intervals) == 1

    def test_starting_work_on_task_should_insert_new_interval(self):
        task = self.tasks.by_id(2)
        intervals = self.task_intervals.for_task(task)
        assert len(intervals) == 0
        interval = self.task_intervals.start(task)
        intervals = self.task_intervals.for_task(task)
        assert len(intervals) == 1
        assert intervals[0]._task.task_id == interval._task.task_id
        assert intervals[0]._task_interval == interval._task_interval

    def test_after_stopping_no_intervals_should_be_in_progress(self):
        task = self.tasks.by_id(1)
        self.task_intervals.start(task)
        intervals = self.task_intervals.for_task(task)
        assert any(interval.in_progress for interval in intervals)
        self.task_intervals.stop(task)
        intervals = self.task_intervals.for_task(task)
        assert len(intervals) > 0
        for interval in intervals:
            assert not interval.in_progress

    def test_should_extract_the_interval_in_progress(self):
        task = self.tasks.by_id(1)
        started = self.task_intervals.start(task)
        in_progress = self.task_intervals.in_progress()
        assert in_progress._task_interval == started._task_interval
        assert in_progress.task._task_id == started.task._task_id

    def test_should_refuse_to_start_new_task_if_one_is_already_in_progress(self):
        task = self.tasks.by_id(2)
        self.task_intervals.start(task)
        with pytest.raises(TooManyTasksInProgress):
            self.task_intervals.start(task)

    def test_should_be_able_to_start_and_stop_task_in_the_past(self):
        now = time.time()
        an_hour_ago = now - 60 * 60
        a_minute_ago = now - 60
        task = self.tasks.by_id(2)
        self.task_intervals.start(task, an_hour_ago)
        self.task_intervals.stop(task, a_minute_ago)
        latest_interval = self.task_intervals.for_task(task)[-1]
        assert latest_interval.duration == a_minute_ago - an_hour_ago

    def test_should_not_be_able_to_overlap_task_intervals(self):
        now = time.time()
        an_hour_ago = now - 60 * 60
        half_an_hour_ago = now - 30 * 60
        task = self.tasks.by_id(2)
        self.task_intervals.start(task, an_hour_ago)
        self.task_intervals.stop(task, now)
        with pytest.raises(InconsistentTaskIntervals):
            self.task_intervals.start(task, half_an_hour_ago)

    def test_should_not_be_able_to_stop_before_start(self):
        now = time.time()
        an_hour_ago = now - 60 * 60
        task = self.tasks.by_id(2)
        self.task_intervals.start(task, now)
        with pytest.raises(InconsistentTaskIntervals):
            self.task_intervals.stop(task, an_hour_ago)
