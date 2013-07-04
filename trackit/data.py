# coding=utf-8
# Copyright (c) 2013 Robin Kåveland Hansen
#
# This file is a part of trackit. It is distributed under the terms
# of the modified BSD license. The full license is available in
# LICENSE, distributed as part of this software.

"""
Interface to the data models used in trackit.
"""
import sqlite3
import time
from contextlib import closing
from .util import dumb_constructor, DefaultRepr
from . import TrackitException

class TooManyTasksInProgress(TrackitException):
    pass

class NoTaskInProgress(TrackitException):
    pass

class InconsistentTaskIntervals(TrackitException):
    pass

class ClosesCursor(object):
    """Inherit to get context managed cursor, enabling the following idiom:

    >>> with self.cursor() as cursor:
    ...  cursor.execute(sql)
    ...
    >>> # cursor was closed automatically.

    For this to work, the instance needs to have a conn attribute or property.
    """

    def cursor(self):
        return closing(self.conn.cursor())

def _execute_with_except(cursor, sql):
    try:
        cursor.execute(sql)
    except sqlite3.OperationalError:
        pass


class Task(DefaultRepr):
    """Model for a Task."""

    @dumb_constructor
    def __init__(self, _task_id, name, description):
        pass

    @property
    def task_id(self):
        """Readonly - the row id of the task."""
        return self._task_id

    @classmethod
    def map_row(cls, row):
        return cls(*row)

class Tasks(ClosesCursor):
    """Repository to use for accessing, creating and updating Task."""

    SCHEMA = """
    CREATE TABLE TASK(
        TASK INTEGER,
        NAME TEXT NOT NULL,
        DESCRIPTION TEXT,
        PRIMARY KEY(TASK)
    );
"""
    @dumb_constructor
    def __init__(self, conn):
        """Create a Tasks repository. This will attempt to register the schema.

        Arguments:
        - `conn`: sqlite3 database connection.
        """
        with self.cursor() as cursor:
            _execute_with_except(cursor, Tasks.SCHEMA)

    def create(self, name, description=None):
        """Create a Task and return a valid instance that has already been stored in the db.

        Arguments:
        - `name`: The name of the task.
        - `description`: An optional description of the task.
        """
        with self.cursor() as cursor:
            cursor.execute("INSERT INTO TASK(NAME, DESCRIPTION) VALUES(?, ?)", (name, description))
            return Task(cursor.lastrowid, name, description)

    def update(self, task):
        """Update a task in the database.

        Arguments:
        - `task`: The task to update.
        """
        with self.cursor() as cursor:
            cursor.execute("UPDATE TASK SET NAME = ?, DESCRIPTION = ? WHERE TASK = ?",
                           (task.name, task.description, task.task_id))

    def by_name(self, name):
        """Attempt to find tasks by their name, will return results in an iterable.

        Arguments:
        - `name`: the name to search for.
        """
        name_like = "%{}%".format(name)
        with self.cursor() as cursor:
            cursor.execute("SELECT TASK, NAME, DESCRIPTION FROM TASK WHERE NAME LIKE ?", (name_like,))
            return [Task.map_row(row) for row in cursor.fetchall()]

    def all(self):
        """Retrieve all tasks in the database."""
        with self.cursor() as cursor:
            cursor.execute("SELECT TASK, NAME, DESCRIPTION FROM TASK")
            return [Task.map_row(row) for row in cursor.fetchall()]

    def by_id(self, id):
        """Find a task with a given id. This will raise an exception if no such row exists.

        Arguments:
        - `id`: The id of the task to retrieve.
        """
        with self.cursor() as cursor:
            cursor.execute("SELECT TASK, NAME, DESCRIPTION FROM TASK WHERE TASK = ?", (id,))
            row = cursor.fetchone()
            if not row:
                raise KeyError("No Task with id: {}".format(id))
            return Task.map_row(row)

class TaskInterval(DefaultRepr):
    """Model for a time spent working on some task."""

    @dumb_constructor
    def __init__(self, _task, _task_interval, start_time, stop_time=None):
        pass

    @property
    def task(self):
        """Readonly - the task this interval was spent working with."""
        return self._task

    @property
    def task_interval(self):
        """Readonly - the id of this taskinterval."""
        return self._task_interval

    @property
    def in_progress(self):
        """True when the time interval has not been stopped."""
        return self.stop_time is None

    @property
    def duration(self):
        """Duration in seconds this task has been ongoing."""
        stop = self.stop_time if self.stop_time is not None else time.time()
        return stop - self.start_time

    @classmethod
    def map_row(cls, task, row):
        return cls(task, *row)

class TaskIntervals(ClosesCursor):
    """Repository to use for accessing, creating and updating TaskIntervals.
    """

    SCHEMA = """
    CREATE TABLE TASKINTERVAL(
        TASKINTERVAL INTEGER,
        TASK INTEGER NOT NULL,
        START_TIME INTEGER NOT NULL,
        STOP_TIME INTEGER,
        PRIMARY KEY(TASKINTERVAL),
        FOREIGN KEY(TASK) REFERENCES TASK(TASK)
    );
"""

    @dumb_constructor
    def __init__(self, conn, tasks=None):
        """Create a TaskIntervals repository. This will attempt to register the schema.

        Arguments:
        - `conn`: sqlite3 database connection.
        - `tasks`: Tasks repository - if None, one will be created.
        """
        if tasks is None:
            self.tasks = Tasks(conn)
        with self.cursor() as cursor:
            _execute_with_except(cursor, TaskIntervals.SCHEMA)

    def start(self, task, when=None):
        """Start working on a task.

        Arguments:
        - `task`: the task to start working on.
        - `when`: unix-time for when task was started."""

        assert task is not None, "may not start task None"
        in_progress = self.in_progress()
        if in_progress is not None:
            raise TooManyTasksInProgress("Must stop working on {} before starting on new task."
                                         .format(in_progress))
        when = time.time() if when is None else when
        with self.cursor() as cursor:
            sql = "INSERT INTO TASKINTERVAL(TASK, START_TIME) VALUES(?, ?)"
            cursor.execute(sql, (task.task_id, when))
            return TaskInterval(task, cursor.lastrowid, when)

    def stop(self, task, when=None):
        """Stop working on a task.

        Arguments:
        - `task`: the task to stop working on.
        - `when`: unix time for when task was stopped."""

        latest = ("SELECT TASKINTERVAL, START_TIME FROM TASKINTERVAL WHERE TASK = ? AND " +
                  "START_TIME = (SELECT MAX(START_TIME) FROM TASKINTERVAL WHERE TASK = ?)")
        when = time.time() if when is None else when
        stop = "UPDATE TASKINTERVAL SET STOP_TIME = ? WHERE TASKINTERVAL = ?"
        with self.cursor() as cursor:
            cursor.execute(latest, (task.task_id, task.task_id))
            row = cursor.fetchone()
            if not row:
                raise NoTaskInProgress("No work in progress on task: {}".format(task))
            interval_id, start_time = row
            if start_time >= when:
                message = "Start time is {} which is *after* stop time: {}".format(
                    start_time, when
                )
                raise InconsistentTaskIntervals(message)
            cursor.execute(stop, (when, interval_id))

    def for_task(self, task):
        """Extract all task intervals spent working on some task.

        Arguments:
        - `task`: the task to extract intervals for.
        """
        sql = ("SELECT TASKINTERVAL, START_TIME, STOP_TIME " +
               "FROM TASKINTERVAL WHERE TASK = ? ORDER BY TASKINTERVAL")
        with self.cursor() as cursor:
            cursor.execute(sql, (task.task_id,))
            return [TaskInterval.map_row(task, row) for row in cursor.fetchall()]

    def in_progress(self):
        """Extract the task interval currently in progress."""

        interval_sql = ("SELECT TASK, TASKINTERVAL, START_TIME, STOP_TIME FROM TASKINTERVAL " +
                        "WHERE STOP_TIME IS NULL")
        with self.cursor() as cursor:
            cursor.execute(interval_sql)
            rows = cursor.fetchall()
            if len(rows) > 1:
                message = "Should only have one task in progress, but found: {}".format(rows)
                raise TooManyTasksInProgress(message)
            if not rows:
                return None
            task_id, interval = rows[0][0], rows[0][1:]
            task = self.tasks.by_id(task_id)
            return TaskInterval.map_row(task, interval)
