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
from datetime import date, time, timedelta
import os

from storm.databases.postgres import (
    Postgres, compile, currval, Returning, PostgresTimeoutTracer, make_dsn)
from storm.database import create_database
from storm.exceptions import InterfaceError, ProgrammingError
from storm.variables import DateTimeVariable, RawStrVariable
from storm.variables import ListVariable, IntVariable, Variable
from storm.properties import Int
from storm.exceptions import DisconnectionError
from storm.expr import (Union, Select, Insert, Update, Alias, SQLRaw, State,
                        Sequence, Like, Column, COLUMN)
from storm.tracer import install_tracer, TimeoutError
from storm.uri import URI

# We need the info to register the 'type' compiler.  In normal
# circumstances this is naturally imported.
import storm.info
storm  # Silence lint.

from tests import has_fixtures, has_subunit
from tests.databases.base import (
    DatabaseTest, DatabaseDisconnectionTest, UnsupportedDatabaseTest,
    TwoPhaseCommitTest, TwoPhaseCommitDisconnectionTest)
from tests.expr import column1, column2, column3, elem1, table1, TrackContext
from tests.tracer import TimeoutTracerTestBase
from tests.helper import TestHelper

try:
    import pgbouncer
except ImportError:
    has_pgbouncer = False
else:
    has_pgbouncer = True


def terminate_other_backends(connection):
    """Terminate all connections to the database except the one given."""
    connection.execute(
        "SELECT pg_terminate_backend(procpid)"
        "  FROM pg_stat_activity"
        " WHERE datname = current_database()"
        "   AND procpid != pg_backend_pid()")


def terminate_all_backends(database):
    """Terminate all connections to the given database."""
    connection = database.connect()
    terminate_other_backends(connection)
    connection.close()


class PostgresTest(DatabaseTest, TestHelper):

    def is_supported(self):
        return bool(os.environ.get("STORM_POSTGRES_URI"))

    def create_database(self):
        self.database = create_database(os.environ["STORM_POSTGRES_URI"])

    def create_tables(self):
        self.connection.execute("CREATE TABLE number "
                                "(one INTEGER, two INTEGER, three INTEGER)")
        self.connection.execute("CREATE TABLE test "
                                "(id SERIAL PRIMARY KEY, title VARCHAR)")
        self.connection.execute("CREATE TABLE datetime_test "
                                "(id SERIAL PRIMARY KEY,"
                                " dt TIMESTAMP, d DATE, t TIME, td INTERVAL)")
        self.connection.execute("CREATE TABLE bin_test "
                                "(id SERIAL PRIMARY KEY, b BYTEA)")
        self.connection.execute("CREATE TABLE like_case_insensitive_test "
                                "(id SERIAL PRIMARY KEY, description TEXT)")
        self.connection.execute("CREATE TABLE returning_test "
                                "(id1 INTEGER DEFAULT 123, "
                                " id2 INTEGER DEFAULT 456)")

    def drop_tables(self):
        super(PostgresTest, self).drop_tables()
        for table in ["like_case_insensitive_test", "returning_test"]:
            try:
                self.connection.execute("DROP TABLE %s" % table)
                self.connection.commit()
            except:
                self.connection.rollback()

    def create_sample_data(self):
        super(PostgresTest, self).create_sample_data()
        self.connection.execute("INSERT INTO like_case_insensitive_test "
                                "(description) VALUES ('hullah')")
        self.connection.execute("INSERT INTO like_case_insensitive_test "
                                "(description) VALUES ('HULLAH')")
        self.connection.commit()

    def test_wb_create_database(self):
        database = create_database("postgres://un:pw@ht:12/db")
        self.assertTrue(isinstance(database, Postgres))
        self.assertEquals(database._dsn,
                          "dbname=db host=ht port=12 user=un password=pw")

    def test_wb_version(self):
        version = self.database._version
        self.assertEquals(type(version), int)
        try:
            result = self.connection.execute("SHOW server_version_num")
        except ProgrammingError:
            self.assertEquals(version, 0)
        else:
            server_version = int(result.get_one()[0])
            self.assertEquals(version, server_version)

    def test_utf8_client_encoding(self):
        connection = self.database.connect()
        result = connection.execute("SHOW client_encoding")
        encoding = result.get_one()[0]
        self.assertEquals(encoding.upper(), "UTF8")

    def test_unicode(self):
        raw_str = "\xc3\xa1\xc3\xa9\xc3\xad\xc3\xb3\xc3\xba"
        uni_str = raw_str.decode("UTF-8")

        connection = self.database.connect()
        connection.execute("INSERT INTO test VALUES (1, '%s')" % raw_str)

        result = connection.execute("SELECT title FROM test WHERE id=1")
        title = result.get_one()[0]

        self.assertTrue(isinstance(title, unicode))
        self.assertEquals(title, uni_str)

    def test_unicode_array(self):
        raw_str = "\xc3\xa1\xc3\xa9\xc3\xad\xc3\xb3\xc3\xba"
        uni_str = raw_str.decode("UTF-8")

        connection = self.database.connect()
        result = connection.execute("""SELECT '{"%s"}'::TEXT[]""" % raw_str)
        self.assertEquals(result.get_one()[0], [uni_str])
        result = connection.execute("""SELECT ?::TEXT[]""", ([uni_str],))
        self.assertEquals(result.get_one()[0], [uni_str])

    def test_time(self):
        connection = self.database.connect()
        value = time(12, 34)
        result = connection.execute("SELECT ?::TIME", (value,))
        self.assertEquals(result.get_one()[0], value)

    def test_date(self):
        connection = self.database.connect()
        value = date(2007, 6, 22)
        result = connection.execute("SELECT ?::DATE", (value,))
        self.assertEquals(result.get_one()[0], value)

    def test_interval(self):
        connection = self.database.connect()
        value = timedelta(365)
        result = connection.execute("SELECT ?::INTERVAL", (value,))
        self.assertEquals(result.get_one()[0], value)

    def test_datetime_with_none(self):
        self.connection.execute("INSERT INTO datetime_test (dt) VALUES (NULL)")
        result = self.connection.execute("SELECT dt FROM datetime_test")
        variable = DateTimeVariable()
        result.set_variable(variable, result.get_one()[0])
        self.assertEquals(variable.get(), None)

    def test_array_support(self):
        try:
            self.connection.execute("DROP TABLE array_test")
            self.connection.commit()
        except:
            self.connection.rollback()

        self.connection.execute("CREATE TABLE array_test "
                                "(id SERIAL PRIMARY KEY, a INT[])")

        variable = ListVariable(IntVariable)
        variable.set([1,2,3,4])

        state = State()
        statement = compile(variable, state)

        self.connection.execute("INSERT INTO array_test VALUES (1, %s)"
                                % statement, state.parameters)

        result = self.connection.execute("SELECT a FROM array_test WHERE id=1")

        array = result.get_one()[0]

        self.assertTrue(isinstance(array, list))

        variable = ListVariable(IntVariable)
        result.set_variable(variable, array)
        self.assertEquals(variable.get(), [1,2,3,4])

    def test_array_support_with_empty(self):
        try:
            self.connection.execute("DROP TABLE array_test")
            self.connection.commit()
        except:
            self.connection.rollback()

        self.connection.execute("CREATE TABLE array_test "
                                "(id SERIAL PRIMARY KEY, a INT[])")

        variable = ListVariable(IntVariable)
        variable.set([])

        state = State()
        statement = compile(variable, state)

        self.connection.execute("INSERT INTO array_test VALUES (1, %s)"
                                % statement, state.parameters)

        result = self.connection.execute("SELECT a FROM array_test WHERE id=1")

        array = result.get_one()[0]

        self.assertTrue(isinstance(array, list))

        variable = ListVariable(IntVariable)
        result.set_variable(variable, array)
        self.assertEquals(variable.get(), [])

    def test_expressions_in_union_order_by(self):
        # The following statement breaks in postgres:
        #     SELECT 1 AS id UNION SELECT 1 ORDER BY id+1;
        # With the error:
        #     ORDER BY on a UNION/INTERSECT/EXCEPT result must
        #     be on one of the result columns
        column = SQLRaw("1")
        Alias.auto_counter = 0
        alias = Alias(column, "id")
        expr = Union(Select(alias), Select(column), order_by=alias+1,
                     limit=1, offset=1, all=True)

        state = State()
        statement = compile(expr, state)
        self.assertEquals(statement,
                          'SELECT * FROM '
                          '((SELECT 1 AS id) UNION ALL (SELECT 1)) AS "_1" '
                          'ORDER BY id+? LIMIT 1 OFFSET 1')
        self.assertVariablesEqual(state.parameters, [Variable(1)])

        result = self.connection.execute(expr)
        self.assertEquals(result.get_one(), (1,))

    def test_expressions_in_union_in_union_order_by(self):
        column = SQLRaw("1")
        alias = Alias(column, "id")
        expr = Union(Select(alias), Select(column), order_by=alias+1,
                     limit=1, offset=1, all=True)
        expr = Union(expr, expr, order_by=alias+1, all=True)
        result = self.connection.execute(expr)
        self.assertEquals(result.get_all(), [(1,), (1,)])

    def test_sequence(self):
        expr1 = Select(Sequence("test_id_seq"))
        expr2 = "SELECT currval('test_id_seq')"
        value1 = self.connection.execute(expr1).get_one()[0]
        value2 = self.connection.execute(expr2).get_one()[0]
        value3 = self.connection.execute(expr1).get_one()[0]
        self.assertEquals(value1, value2)
        self.assertEquals(value3-value1, 1)

    def test_like_case(self):
        expr = Like("name", "value")
        statement = compile(expr)
        self.assertEquals(statement, "? LIKE ?")
        expr = Like("name", "value", case_sensitive=True)
        statement = compile(expr)
        self.assertEquals(statement, "? LIKE ?")
        expr = Like("name", "value", case_sensitive=False)
        statement = compile(expr)
        self.assertEquals(statement, "? ILIKE ?")

    def test_case_default_like(self):

        like = Like(SQLRaw("description"), u"%hullah%")
        expr = Select(SQLRaw("id"), like, tables=["like_case_insensitive_test"])
        result = self.connection.execute(expr)
        self.assertEquals(result.get_all(), [(1,)])

        like = Like(SQLRaw("description"), u"%HULLAH%")
        expr = Select(SQLRaw("id"), like, tables=["like_case_insensitive_test"])
        result = self.connection.execute(expr)
        self.assertEquals(result.get_all(), [(2,)])

    def test_case_sensitive_like(self):

        like = Like(SQLRaw("description"), u"%hullah%", case_sensitive=True)
        expr = Select(SQLRaw("id"), like, tables=["like_case_insensitive_test"])
        result = self.connection.execute(expr)
        self.assertEquals(result.get_all(), [(1,)])

        like = Like(SQLRaw("description"), u"%HULLAH%", case_sensitive=True)
        expr = Select(SQLRaw("id"), like, tables=["like_case_insensitive_test"])
        result = self.connection.execute(expr)
        self.assertEquals(result.get_all(), [(2,)])

    def test_case_insensitive_like(self):

        like = Like(SQLRaw("description"), u"%hullah%", case_sensitive=False)
        expr = Select(SQLRaw("id"), like, tables=["like_case_insensitive_test"])
        result = self.connection.execute(expr)
        self.assertEquals(result.get_all(), [(1,), (2,)])
        like = Like(SQLRaw("description"), u"%HULLAH%", case_sensitive=False)
        expr = Select(SQLRaw("id"), like, tables=["like_case_insensitive_test"])
        result = self.connection.execute(expr)
        self.assertEquals(result.get_all(), [(1,), (2,)])

    def test_none_on_string_variable(self):
        """
        Verify that the logic to enforce fix E''-styled strings isn't
        breaking on NULL values.
        """
        variable = RawStrVariable(value=None)
        result = self.connection.execute(Select(variable))
        self.assertEquals(result.get_one(), (None,))

    def test_compile_table_with_schema(self):
        class Foo(object):
            __storm_table__ = "my schema.my table"
            id = Int("my.column", primary=True)
        self.assertEquals(compile(Select(Foo.id)),
                          'SELECT "my schema"."my table"."my.column" '
                          'FROM "my schema"."my table"')

    def test_currval_no_escaping(self):
        expr = currval(Column("thecolumn", "theschema.thetable"))
        statement = compile(expr)
        expected = """currval('theschema.thetable_thecolumn_seq')"""
        self.assertEquals(statement, expected)

    def test_currval_escaped_schema(self):
        expr = currval(Column("thecolumn", "the schema.thetable"))
        statement = compile(expr)
        expected = """currval('"the schema".thetable_thecolumn_seq')"""
        self.assertEquals(statement, expected)

    def test_currval_escaped_table(self):
        expr = currval(Column("thecolumn", "theschema.the table"))
        statement = compile(expr)
        expected = """currval('theschema."the table_thecolumn_seq"')"""
        self.assertEquals(statement, expected)

    def test_currval_escaped_column(self):
        expr = currval(Column("the column", "theschema.thetable"))
        statement = compile(expr)
        expected = """currval('theschema."thetable_the column_seq"')"""
        self.assertEquals(statement, expected)

    def test_currval_escaped_column_no_schema(self):
        expr = currval(Column("the column", "thetable"))
        statement = compile(expr)
        expected = """currval('"thetable_the column_seq"')"""
        self.assertEquals(statement, expected)

    def test_currval_escaped_schema_table_and_column(self):
        expr = currval(Column("the column", "the schema.the table"))
        statement = compile(expr)
        expected = """currval('"the schema"."the table_the column_seq"')"""
        self.assertEquals(statement, expected)

    def test_get_insert_identity(self):
        column = Column("thecolumn", "thetable")
        variable = IntVariable()
        result = self.connection.execute("SELECT 1")
        where = result.get_insert_identity((column,), (variable,))
        self.assertEquals(compile(where),
                          "thetable.thecolumn = "
                          "(SELECT currval('thetable_thecolumn_seq'))")

    def test_returning_column_context(self):
        column2 = TrackContext()
        insert = Insert({column1: elem1}, table1, primary_columns=column2)
        compile(Returning(insert))
        self.assertEquals(column2.context, COLUMN)

    def test_returning_update(self):
        update = Update({column1: elem1}, table=table1,
                        primary_columns=(column2, column3))
        self.assertEquals(compile(Returning(update)),
                          'UPDATE "table 1" SET column1=elem1 '
                          'RETURNING column2, column3')

    def test_returning_update_with_columns(self):
        update = Update({column1: elem1}, table=table1,
                        primary_columns=(column2, column3))
        self.assertEquals(compile(Returning(update, columns=[column3])),
                          'UPDATE "table 1" SET column1=elem1 '
                          'RETURNING column3')

    def test_execute_insert_returning(self):
        if self.database._version < 80200:
            return # Can't run this test with old PostgreSQL versions.

        column1 = Column("id1", "returning_test")
        column2 = Column("id2", "returning_test")
        variable1 = IntVariable()
        variable2 = IntVariable()
        insert = Insert({}, primary_columns=(column1, column2),
                            primary_variables=(variable1, variable2))
        self.connection.execute(insert)

        self.assertTrue(variable1.is_defined())
        self.assertTrue(variable2.is_defined())

        self.assertEquals(variable1.get(), 123)
        self.assertEquals(variable2.get(), 456)

        result = self.connection.execute("SELECT * FROM returning_test")
        self.assertEquals(result.get_one(), (123, 456))

    def test_wb_execute_insert_returning_not_used_with_old_postgres(self):
        """Shouldn't try to use RETURNING with PostgreSQL < 8.2."""
        column1 = Column("id1", "returning_test")
        column2 = Column("id2", "returning_test")
        variable1 = IntVariable()
        variable2 = IntVariable()
        insert = Insert({}, primary_columns=(column1, column2),
                            primary_variables=(variable1, variable2))
        self.database._version = 80109

        self.connection.execute(insert)

        self.assertFalse(variable1.is_defined())
        self.assertFalse(variable2.is_defined())

        result = self.connection.execute("SELECT * FROM returning_test")
        self.assertEquals(result.get_one(), (123, 456))

    def test_execute_insert_returning_without_columns(self):
        """Without primary_columns, the RETURNING system won't be used."""
        column1 = Column("id1", "returning_test")
        variable1 = IntVariable()
        insert = Insert({column1: 123}, primary_variables=(variable1,))
        self.connection.execute(insert)

        self.assertFalse(variable1.is_defined())

        result = self.connection.execute("SELECT * FROM returning_test")
        self.assertEquals(result.get_one(), (123, 456))

    def test_execute_insert_returning_without_variables(self):
        """Without primary_variables, the RETURNING system won't be used."""
        column1 = Column("id1", "returning_test")
        insert = Insert({}, primary_columns=(column1,))
        self.connection.execute(insert)

        result = self.connection.execute("SELECT * FROM returning_test")

        self.assertEquals(result.get_one(), (123, 456))

    def test_execute_update_returning(self):
        if self.database._version < 80200:
            return # Can't run this test with old PostgreSQL versions.

        column1 = Column("id1", "returning_test")
        column2 = Column("id2", "returning_test")
        self.connection.execute(
            "INSERT INTO returning_test VALUES (1, 2)")
        update = Update({"id2": 3}, column1 == 1,
                        primary_columns=(column1, column2))
        result = self.connection.execute(Returning(update))
        self.assertEquals(result.get_one(), (1, 3))

    def test_isolation_autocommit(self):
        database = create_database(
            os.environ["STORM_POSTGRES_URI"] + "?isolation=autocommit")

        connection = database.connect()
        self.addCleanup(connection.close)

        result = connection.execute("SHOW TRANSACTION ISOLATION LEVEL")
        # It matches read committed in Postgres internel
        self.assertEquals(result.get_one()[0], u"read committed")

        connection.execute("INSERT INTO bin_test VALUES (1, 'foo')")

        result = self.connection.execute("SELECT id FROM bin_test")
        # I didn't commit, but data should already be there
        self.assertEquals(result.get_all(), [(1,)])
        connection.rollback()

    def test_isolation_read_committed(self):
        database = create_database(
            os.environ["STORM_POSTGRES_URI"] + "?isolation=read-committed")

        connection = database.connect()
        self.addCleanup(connection.close)

        result = connection.execute("SHOW TRANSACTION ISOLATION LEVEL")
        self.assertEquals(result.get_one()[0], u"read committed")

        connection.execute("INSERT INTO bin_test VALUES (1, 'foo')")

        result = self.connection.execute("SELECT id FROM bin_test")
        # Data should not be there already
        self.assertEquals(result.get_all(), [])
        connection.rollback()

        # Start a transaction
        result = connection.execute("SELECT 1")
        self.assertEquals(result.get_one(), (1,))

        self.connection.execute("INSERT INTO bin_test VALUES (1, 'foo')")
        self.connection.commit()

        result = connection.execute("SELECT id FROM bin_test")
        # Data is already here!
        self.assertEquals(result.get_one(), (1,))
        connection.rollback()

    def test_isolation_serializable(self):
        database = create_database(
            os.environ["STORM_POSTGRES_URI"] + "?isolation=serializable")

        connection = database.connect()
        self.addCleanup(connection.close)

        result = connection.execute("SHOW TRANSACTION ISOLATION LEVEL")
        self.assertEquals(result.get_one()[0], u"serializable")

        # Start a transaction
        result = connection.execute("SELECT 1")
        self.assertEquals(result.get_one(), (1,))

        self.connection.execute("INSERT INTO bin_test VALUES (1, 'foo')")
        self.connection.commit()

        result = connection.execute("SELECT id FROM bin_test")
        # We can't see data yet, because transaction started before
        self.assertEquals(result.get_one(), None)
        connection.rollback()

    def test_default_isolation(self):
        """
        The default isolation level is REPEATABLE READ, but it's only supported
        by psycopg2 2.4 and newer. Before, SERIALIZABLE is used instead.
        """
        result = self.connection.execute("SHOW TRANSACTION ISOLATION LEVEL")
        import psycopg2
        psycopg2_version = psycopg2.__version__.split(None, 1)[0]
        if psycopg2_version < "2.4":
            self.assertEquals(result.get_one()[0], u"serializable")
        else:
            self.assertEquals(result.get_one()[0], u"repeatable read")

    def test_unknown_serialization(self):
        self.assertRaises(ValueError, create_database,
            os.environ["STORM_POSTGRES_URI"] + "?isolation=stuff")

    def test_is_disconnection_error_with_ssl_syscall_error(self):
        """
        If the underlying driver raises a ProgrammingError with 'SSL SYSCALL
        error', we consider the connection dead and mark it as needing
        reconnection.
        """
        exc = ProgrammingError("SSL SYSCALL error: Connection timed out")
        self.assertTrue(self.connection.is_disconnection_error(exc))


_max_prepared_transactions = None


class PostgresTwoPhaseCommitTest(TwoPhaseCommitTest, TestHelper):
    
    def is_supported(self):
        uri = os.environ.get("STORM_POSTGRES_URI")
        if not uri:
            return False
        global _max_prepared_transactions
        if _max_prepared_transactions is None:
            database = create_database(uri)
            connection = database.connect()
            result = connection.execute("SHOW MAX_PREPARED_TRANSACTIONS")
            _max_prepared_transactions = int(result.get_one()[0])
            connection.close()
        return _max_prepared_transactions > 0

    def create_database(self):
        self.database = create_database(os.environ["STORM_POSTGRES_URI"])

    def create_tables(self):
        self.connection.execute("CREATE TABLE test "
                                "(id SERIAL PRIMARY KEY, title VARCHAR)")
        self.connection.commit()


class PostgresUnsupportedTest(UnsupportedDatabaseTest, TestHelper):

    dbapi_module_names = ["psycopg2"]
    db_module_name = "postgres"


class PostgresDisconnectionTest(DatabaseDisconnectionTest, TwoPhaseCommitDisconnectionTest,
                                TestHelper):

    environment_variable = "STORM_POSTGRES_URI"
    host_environment_variable = "STORM_POSTGRES_HOST_URI"
    default_port = 5432

    def test_rollback_swallows_InterfaceError(self):
        """Test that InterfaceErrors get caught on rollback().

        InterfaceErrors are a form of a disconnection error, so rollback()
        must swallow them and reconnect.
        """
        class FakeConnection:
            def rollback(self):
                raise InterfaceError('connection already closed')
        self.connection._raw_connection = FakeConnection()
        try:
            self.connection.rollback()
        except Exception, exc:
            self.fail('Exception should have been swallowed: %s' % repr(exc))


class PostgresDisconnectionTestWithoutProxyBase(object):
    # DatabaseDisconnectionTest uses a socket proxy to simulate broken
    # connections. This class tests some other causes of disconnection.

    database_uri = None

    def is_supported(self):
        return bool(self.database_uri) and super(
            PostgresDisconnectionTestWithoutProxyBase, self).is_supported()

    def setUp(self):
        super(PostgresDisconnectionTestWithoutProxyBase, self).setUp()
        self.database = create_database(self.database_uri)

    def test_terminated_backend(self):
        # The error raised when trying to use a connection that has been
        # terminated at the server is considered a disconnection error.
        connection = self.database.connect()
        terminate_all_backends(self.database)
        self.assertRaises(
            DisconnectionError, connection.execute,
            "SELECT current_database()")


if has_subunit:
    # Some of the following tests are prone to segfaults, presumably in
    # _psycopg.so. Run them in a subprocess if possible.
    from subunit import IsolatedTestCase
    class MisbehavingTestCase(TestHelper, IsolatedTestCase):
        pass
else:
    # If we can't run them in a subprocess we still want to create tests, but
    # prevent them from running, so that the skip is reported
    class MisbehavingTestCase(TestHelper):
        def is_supported(self):
            return False


class PostgresDisconnectionTestWithoutProxyUnixSockets(
    PostgresDisconnectionTestWithoutProxyBase, MisbehavingTestCase):
    """Disconnection tests using Unix sockets."""

    database_uri = os.environ.get("STORM_POSTGRES_URI")

class PostgresDisconnectionTestWithoutProxyTCPSockets(
    PostgresDisconnectionTestWithoutProxyBase, MisbehavingTestCase):
    """Disconnection tests using TCP sockets."""

    database_uri = os.environ.get("STORM_POSTGRES_HOST_URI")


class PostgresDisconnectionTestWithPGBouncerBase(object):
    # Connecting via pgbouncer <http://pgfoundry.org/projects/pgbouncer>
    # introduces new possible causes of disconnections.

    def is_supported(self):
        return (
            has_fixtures and has_pgbouncer and
            bool(os.environ.get("STORM_POSTGRES_HOST_URI")))

    def setUp(self):
        super(PostgresDisconnectionTestWithPGBouncerBase, self).setUp()
        database_uri = URI(os.environ["STORM_POSTGRES_HOST_URI"])
        database_user = database_uri.username or os.environ['USER']
        database_dsn = make_dsn(database_uri)
        # Create a pgbouncer fixture.
        self.pgbouncer = pgbouncer.fixture.PGBouncerFixture()
        self.pgbouncer.databases[database_uri.database] = database_dsn
        self.pgbouncer.users[database_user] = "trusted"
        self.pgbouncer.admin_users = [database_user]
        self.useFixture(self.pgbouncer)
        # Create a Database that uses pgbouncer.
        pgbouncer_uri = database_uri.copy()
        pgbouncer_uri.host = self.pgbouncer.host
        pgbouncer_uri.port = self.pgbouncer.port
        self.database = create_database(pgbouncer_uri)

    def test_terminated_backend(self):
        # The error raised when trying to use a connection through pgbouncer
        # that has been terminated at the server is considered a disconnection
        # error.
        connection = self.database.connect()
        terminate_all_backends(self.database)
        self.assertRaises(
            DisconnectionError, connection.execute,
            "SELECT current_database()")

    def test_pgbouncer_stopped(self):
        # The error raised from a connection that is no longer connected
        # because pgbouncer has been immediately shutdown (via SIGTERM; see
        # man 1 pgbouncer) is considered a disconnection error.
        connection = self.database.connect()
        self.pgbouncer.stop()
        self.assertRaises(
            DisconnectionError, connection.execute,
            "SELECT current_database()")


if has_fixtures:
    # Upgrade to full test case class with fixtures.
    from fixtures import TestWithFixtures
    class PostgresDisconnectionTestWithPGBouncer(
        PostgresDisconnectionTestWithPGBouncerBase,
        TestWithFixtures, TestHelper): pass


class PostgresTimeoutTracerTest(TimeoutTracerTestBase):

    tracer_class = PostgresTimeoutTracer

    def is_supported(self):
        return bool(os.environ.get("STORM_POSTGRES_URI"))

    def setUp(self):
        super(PostgresTimeoutTracerTest, self).setUp()
        self.database = create_database(os.environ["STORM_POSTGRES_URI"])
        self.connection = self.database.connect()
        install_tracer(self.tracer)
        self.tracer.get_remaining_time = lambda: self.remaining_time
        self.remaining_time = 10.5

    def test_set_statement_timeout(self):
        result = self.connection.execute("SHOW statement_timeout")
        self.assertEquals(result.get_one(), ("10500ms",))

    def test_connection_raw_execute_error(self):
        statement = "SELECT pg_sleep(0.5)"
        self.remaining_time = 0.001
        try:
            self.connection.execute(statement)
        except TimeoutError, e:
            self.assertEqual("SQL server cancelled statement", e.message)
            self.assertEqual(statement, e.statement)
            self.assertEqual((), e.params)
        else:
            self.fail("TimeoutError not raised")
