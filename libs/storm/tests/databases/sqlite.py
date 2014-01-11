#
# Copyright (c) 2006, 2007 Canonical
#
# Written by Gustavo Niemeyer <gustavo@niemeyer.net>
#
# This file is part of Storm Object Relational Mapper.
#
# Storm is free software; you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as
# published by the Free Software Foundation; either version 2.1 of
# the License, or (at your option) any later version.
#
# Storm is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
from datetime import timedelta
import time
import os

from storm.exceptions import OperationalError
from storm.databases.sqlite import SQLite
from storm.database import create_database
from storm.uri import URI

from tests.databases.base import DatabaseTest, UnsupportedDatabaseTest
from tests.helper import TestHelper, MakePath


class SQLiteMemoryTest(DatabaseTest, TestHelper):

    helpers = [MakePath]
    
    def get_path(self):
        return ""

    def create_database(self):
        self.database = SQLite(URI("sqlite:%s?synchronous=OFF&timeout=0" %
                                   self.get_path()))

    def create_tables(self):
        self.connection.execute("CREATE TABLE number "
                                "(one INTEGER, two INTEGER, three INTEGER)")
        self.connection.execute("CREATE TABLE test "
                                "(id INTEGER PRIMARY KEY, title VARCHAR)")
        self.connection.execute("CREATE TABLE datetime_test "
                                "(id INTEGER PRIMARY KEY,"
                                " dt TIMESTAMP, d DATE, t TIME, td INTERVAL)")
        self.connection.execute("CREATE TABLE bin_test "
                                "(id INTEGER PRIMARY KEY, b BLOB)")

    def drop_tables(self):
        pass

    def test_wb_create_database(self):
        database = create_database("sqlite:")
        self.assertTrue(isinstance(database, SQLite))
        self.assertEquals(database._filename, ":memory:")

    def test_concurrent_behavior(self):
        pass # We can't connect to the in-memory database twice, so we can't
             # exercise the concurrency behavior (nor it makes sense).

    def test_synchronous(self):
        synchronous_values = {"OFF": 0, "NORMAL": 1, "FULL": 2}
        for value in synchronous_values:
            database = SQLite(URI("sqlite:%s?synchronous=%s" %
                                  (self.get_path(), value)))
            connection = database.connect()
            result = connection.execute("PRAGMA synchronous")
            self.assertEquals(result.get_one()[0],
                              synchronous_values[value])

    def test_sqlite_specific_reserved_words(self):
        """Check sqlite-specific reserved words are recognized.

        This uses a list copied from http://www.sqlite.org/lang_keywords.html
        with the reserved words from SQL1992 removed.
        """
        reserved_words = """
            abort after analyze attach autoincrement before conflict
            database detach each exclusive explain fail glob if ignore
            index indexed instead isnull limit notnull offset plan
            pragma query raise regexp reindex release rename replace
            row savepoint temp trigger vacuum virtual
            """.split()
        for word in reserved_words:
            self.assertTrue(self.connection.compile.is_reserved_word(word),
                            "Word missing: %s" % (word,))


class SQLiteFileTest(SQLiteMemoryTest):

    def get_path(self):
        return self.make_path()

    def test_wb_create_database(self):
        filename = self.make_path()
        database = create_database("sqlite:%s" % filename)
        self.assertTrue(isinstance(database, SQLite))
        self.assertEquals(database._filename, filename)

    def test_timeout(self):
        database = create_database("sqlite:%s?timeout=0.3" % self.get_path())
        connection1 = database.connect()
        connection2 = database.connect()
        connection1.execute("CREATE TABLE test (id INTEGER PRIMARY KEY)")
        connection1.commit()
        connection1.execute("INSERT INTO test VALUES (1)")
        started = time.time()
        try:
            connection2.execute("INSERT INTO test VALUES (2)")
        except OperationalError, exception:
            self.assertEquals(str(exception), "database is locked")
            self.assertTrue(time.time()-started >= 0.3)
        else:
            self.fail("OperationalError not raised")

    def test_commit_timeout(self):
        """Regression test for commit observing the timeout.
        
        In 0.10, the timeout wasn't observed for connection.commit().

        """
        # Create a database with a table.
        database = create_database("sqlite:%s?timeout=0.3" % self.get_path())
        connection1 = database.connect()
        connection1.execute("CREATE TABLE test (id INTEGER PRIMARY KEY)")
        connection1.commit()

        # Put some data in, but also make a second connection to the database,
        # which will prevent a commit until it is closed.
        connection1.execute("INSERT INTO test VALUES (1)")
        connection2 = database.connect()
        connection2.execute("SELECT id FROM test")

        started = time.time()
        try:
            connection1.commit()
        except OperationalError, exception:
            self.assertEquals(str(exception), "database is locked")
            # In 0.10, the next assertion failed because the timeout wasn't
            # enforced for the "COMMIT" statement.
            self.assertTrue(time.time()-started >= 0.3)
        else:
            self.fail("OperationalError not raised")

    def test_recover_after_timeout(self):
        """Regression test for recovering from database locked exception.
        
        In 0.10, connection.commit() would forget that a transaction was in
        progress if an exception was raised, such as an OperationalError due to
        another connection being open.  As a result, a subsequent modification
        to the database would cause BEGIN to be issued to the database, which
        would complain that a transaction was already in progress.

        """
        # Create a database with a table.
        database = create_database("sqlite:%s?timeout=0.3" % self.get_path())
        connection1 = database.connect()
        connection1.execute("CREATE TABLE test (id INTEGER PRIMARY KEY)")
        connection1.commit()

        # Put some data in, but also make a second connection to the database,
        # which will prevent a commit until it is closed.
        connection1.execute("INSERT INTO test VALUES (1)")
        connection2 = database.connect()
        connection2.execute("SELECT id FROM test")
        self.assertRaises(OperationalError, connection1.commit)

        # Close the second connection - it should now be possible to commit.
        connection2.close()

        # In 0.10, the next statement raised OperationalError: cannot start a
        # transaction within a transaction
        connection1.execute("INSERT INTO test VALUES (2)")
        connection1.commit()

        # Check that the correct data is present
        self.assertEquals(connection1.execute("SELECT id FROM test").get_all(),
                          [(1,), (2,)])

    def test_journal(self):
        journal_values = {"DELETE": u'delete', "TRUNCATE": u'truncate',
                          "PERSIST": u'persist', "MEMORY": u'memory',
                          "WAL": u'wal', "OFF": u'off'}
        for value in journal_values:
            database = SQLite(URI("sqlite:%s?journal_mode=%s" %
                                  (self.get_path(), value)))
            connection = database.connect()
            result = connection.execute("PRAGMA journal_mode").get_one()[0]
            self.assertEquals(result,
                              journal_values[value])

    def test_journal_persistency_to_rollback(self):
        journal_values = {"DELETE": u'delete', "TRUNCATE": u'truncate',
                          "PERSIST": u'persist', "MEMORY": u'memory',
                          "WAL": u'wal', "OFF": u'off'}
        for value in journal_values:
            database = SQLite(URI("sqlite:%s?journal_mode=%s" %
                                  (self.get_path(), value)))
            connection = database.connect()
            connection.execute("CREATE TABLE test (id INTEGER PRIMARY KEY)")
            connection.rollback()
            result = connection.execute("PRAGMA journal_mode").get_one()[0]
            self.assertEquals(result,
                              journal_values[value])

    def test_foreign_keys(self):
        foreign_keys_values = {"ON": 1, "OFF": 0}
        for value in foreign_keys_values:
            database = SQLite(URI("sqlite:%s?foreign_keys=%s" %
                                  (self.get_path(), value)))
            connection = database.connect()
            result = connection.execute("PRAGMA foreign_keys").get_one()[0]
            self.assertEquals(result,
                              foreign_keys_values[value])

    def test_foreign_keys_persistency_to_rollback(self):
        foreign_keys_values = {"ON": 1, "OFF": 0}
        for value in foreign_keys_values:
            database = SQLite(URI("sqlite:%s?foreign_keys=%s" %
                                  (self.get_path(), value)))
            connection = database.connect()
            connection.execute("CREATE TABLE test (id INTEGER PRIMARY KEY)")
            connection.rollback()
            result = connection.execute("PRAGMA foreign_keys").get_one()[0]
            self.assertEquals(result,
                              foreign_keys_values[value])

class SQLiteUnsupportedTest(UnsupportedDatabaseTest, TestHelper):
 
    dbapi_module_names = ["pysqlite2", "sqlite3"]
    db_module_name = "sqlite"
