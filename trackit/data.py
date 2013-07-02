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
from contextlib import closing
from .util import dumb_constructor, DefaultRepr

class Task(DefaultRepr):
    """Model for a Task."""
    @dumb_constructor
    def __init__(self, _task_id, name, description):
        pass

    @property
    def task_id(self):
        """Readonly - the row id of the task."""
        return self._task_id

def _map_task(task_tuple):
    return Task(*task_tuple)

class Tasks(object):
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
        with closing(self.conn.cursor()) as cursor:
            try:
                cursor.execute(Tasks.SCHEMA)
            except sqlite3.OperationalError:
                pass # Already exists

    def create(self, name, description=None):
        """Create a Task and return a valid instance that has already been stored in the db.

        Arguments:
        - `name`: The name of the task.
        - `description`: An optional description of the task.
        """
        with closing(self.conn.cursor()) as cursor:
            cursor.execute("INSERT INTO TASK(NAME, DESCRIPTION) VALUES(?, ?)", (name, description))
            return Task(cursor.lastrowid, name, description)

    def update(self, task):
        """Update a task in the database.

        Arguments:
        - `task`: The task to update.
        """
        with closing(self.conn.cursor()) as cursor:
            cursor.execute("UPDATE TASK SET NAME = ?, DESCRIPTION = ? WHERE TASK = ?",
                           (task.task_id, task.name, task.description))

    def by_name(self, name):
        """Attempt to find tasks by their name, will return results in an iterable.

        Arguments:
        - `name`: the name to search for.
        """
        name_like = "%{}%".format(name)
        with closing(self.conn.cursor()) as cursor:
            cursor.execute("SELECT TASK, NAME, DESCRIPTION FROM TASK WHERE NAME LIKE ?", (name_like,))
            return [_map_task(task) for task in cursor.fetchall()]

    def all(self):
        """Retrieve all tasks in the database."""
        with closing(self.conn.cursor()) as cursor:
            cursor.execute("SELECT TASK, NAME, DESCRIPTION FROM TASK")
            return [_map_task(task) for task in cursor.fetchall()]

    def by_id(self, id):
        """Find a task with a given id. This will raise an exception if no such row exists.

        Arguments:
        - `id`: The id of the task to retrieve.
        """
        with closing(self.conn.cursor()) as cursor:
            cursor.execute("SELECT TASK, NAME, DESCRIPTION FROM TASK WHERE TASK = ?", (id,))
            row = cursor.fetchone()
            if not row:
                raise KeyError("No Task with id: {}".format(id))
            return _map_task(row)
