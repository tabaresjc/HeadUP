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
import sys
import new
import gc

from storm.exceptions import ClosedError, DatabaseError, DisconnectionError
from storm.variables import Variable
import storm.database
from storm.database import *
from storm.tracer import install_tracer, remove_all_tracers, DebugTracer
from storm.uri import URI
from storm.expr import *

from tests.helper import TestHelper
from tests.mocker import ARGS


marker = object()


class RawConnection(object):

    closed = False

    def __init__(self, executed):
        self.executed = executed

    def cursor(self):
        return RawCursor(executed=self.executed)

    def commit(self):
        self.executed.append("COMMIT")

    def rollback(self):
        self.executed.append("ROLLBACK")

    def close(self):
        self.executed.append("CCLOSE")


class RawCursor(object):

    def __init__(self, arraysize=1, executed=None):
        self.arraysize = arraysize
        if executed is None:
            self.executed = []
        else:
            self.executed = executed

        self._fetchone_data = [("fetchone%d" % i,) for i in range(3)]
        self._fetchall_data = [("fetchall%d" % i,) for i in range(2)]
        self._fetchmany_data = [("fetchmany%d" % i,) for i in range(5)]

    def close(self):
        self.executed.append("RCLOSE")

    def execute(self, statement, params=marker):
        self.executed.append((statement, params))

    def fetchone(self):
        if self._fetchone_data:
            return self._fetchone_data.pop(0)
        return None

    def fetchall(self):
        result = self._fetchall_data
        self._fetchall_data = []
        return result

    def fetchmany(self):
        result = self._fetchmany_data[:self.arraysize]
        del self._fetchmany_data[:self.arraysize]
        return result


class FakeConnection(object):

    def _check_disconnect(self, _function, *args, **kwargs):
        return _function(*args, **kwargs)


class FakeTracer(object):

    def __init__(self, stream=None):
        self.seen = []

    def connection_raw_execute(self, connection, raw_cursor,
                               statement, params):
        self.seen.append(("EXECUTE", connection, type(raw_cursor),
                          statement, params))

    def connection_raw_execute_success(self, connection, raw_cursor,
                                       statement, params):
        self.seen.append(("SUCCESS", connection, type(raw_cursor),
                          statement, params))

    def connection_raw_execute_error(self, connection, raw_cursor,
                                     statement, params, error):
        self.seen.append(("ERROR", connection, type(raw_cursor),
                          statement, params, error))

    def connection_commit(self, connection, xid=None):
        self.seen.append(("COMMIT", connection, xid))

    def connection_rollback(self, connection, xid=None):
        self.seen.append(("ROLLBACK", connection, xid))


class DatabaseTest(TestHelper):

    def setUp(self):
        TestHelper.setUp(self)
        self.database = Database()

    def test_connect(self):
        self.assertRaises(NotImplementedError, self.database.connect)


class ConnectionTest(TestHelper):

    def setUp(self):
        TestHelper.setUp(self)
        self.executed = []
        self.database = Database()
        self.raw_connection = RawConnection(self.executed)
        self.database.raw_connect = lambda: self.raw_connection
        self.connection = Connection(self.database)

    def tearDown(self):
        TestHelper.tearDown(self)
        remove_all_tracers()

    def test_execute(self):
        result = self.connection.execute("something")
        self.assertTrue(isinstance(result, Result))
        self.assertEquals(self.executed, [("something", marker)])

    def test_execute_params(self):
        result = self.connection.execute("something", (1,2,3))
        self.assertTrue(isinstance(result, Result))
        self.assertEquals(self.executed, [("something", (1,2,3))])

    def test_execute_noresult(self):
        result = self.connection.execute("something", noresult=True)
        self.assertEquals(result, None)
        self.assertEquals(self.executed, [("something", marker), "RCLOSE"])

    def test_execute_convert_param_style(self):
        class MyConnection(Connection):
            param_mark = "%s"
        connection = MyConnection(self.database)
        result = connection.execute("'?' ? '?' ? '?'")
        self.assertEquals(self.executed, [("'?' %s '?' %s '?'", marker)])

        # TODO: Unsupported for now.
        #result = connection.execute("$$?$$ ? $asd$'?$asd$ ? '?'")
        #self.assertEquals(self.executed,
        #                  [("'?' %s '?' %s '?'", marker),
        #                   ("$$?$$ %s $asd'?$asd$ %s '?'", marker)])

    def test_execute_select(self):
        select = Select([SQLToken("column1"), SQLToken("column2")],
                        tables=[SQLToken("table1"), SQLToken("table2")])
        result = self.connection.execute(select)
        self.assertTrue(isinstance(result, Result))
        self.assertEquals(self.executed,
                          [("SELECT column1, column2 FROM table1, table2",
                            marker)])

    def test_execute_select_and_params(self):
        select = Select(["column1", "column2"], tables=["table1", "table2"])
        self.assertRaises(ValueError, self.connection.execute,
                          select, ("something",))

    def test_execute_closed(self):
        self.connection.close()
        self.assertRaises(ClosedError, self.connection.execute, "SELECT 1")

    def test_raw_execute_tracing(self):
        self.assertMethodsMatch(FakeTracer, DebugTracer)
        tracer = FakeTracer()
        install_tracer(tracer)
        self.connection.execute("something")
        self.assertEquals(tracer.seen, [("EXECUTE", self.connection, RawCursor,
                                         "something", ()),
                                        ("SUCCESS", self.connection, RawCursor,
                                         "something", ())])

        del tracer.seen[:]
        self.connection.execute("something", (1, 2))
        self.assertEquals(tracer.seen, [("EXECUTE", self.connection, RawCursor,
                                         "something", (1, 2)),
                                        ("SUCCESS", self.connection, RawCursor,
                                         "something", (1, 2))])

    def test_raw_execute_error_tracing(self):
        cursor_mock = self.mocker.patch(RawCursor)
        cursor_mock.execute(ARGS)
        error = ZeroDivisionError()
        self.mocker.throw(error)
        self.mocker.replay()

        self.assertMethodsMatch(FakeTracer, DebugTracer)
        tracer = FakeTracer()
        install_tracer(tracer)
        self.assertRaises(ZeroDivisionError,
                          self.connection.execute, "something")
        self.assertEquals(tracer.seen, [("EXECUTE", self.connection, RawCursor,
                                         "something", ()),
                                        ("ERROR", self.connection, RawCursor,
                                         "something", (), error)])

    def test_raw_execute_setup_error_tracing(self):
        """
        When an exception is raised in the connection_raw_execute hook of a
        tracer, the connection_raw_execute_error hook is called.
        """
        cursor_mock = self.mocker.patch(FakeTracer)
        cursor_mock.connection_raw_execute(ARGS)
        error = ZeroDivisionError()
        self.mocker.throw(error)
        self.mocker.replay()

        tracer = FakeTracer()
        install_tracer(tracer)
        self.assertRaises(ZeroDivisionError,
                          self.connection.execute, "something")
        self.assertEquals(tracer.seen, [("ERROR", self.connection, RawCursor,
                                         "something", (), error)])

    def test_tracing_check_disconnect(self):
        tracer = FakeTracer()
        tracer_mock = self.mocker.patch(tracer)
        tracer_mock.connection_raw_execute(ARGS)
        self.mocker.throw(DatabaseError('connection closed'))
        self.mocker.replay()

        install_tracer(tracer_mock)
        self.connection.is_disconnection_error = (
            lambda exc, extra_disconnection_errors=():
                'connection closed' in str(exc))

        self.assertRaises(DisconnectionError,
                          self.connection.execute, "something")

    def test_tracing_success_check_disconnect(self):
        tracer = FakeTracer()
        tracer_mock = self.mocker.patch(tracer)
        tracer_mock.connection_raw_execute(ARGS)
        tracer_mock.connection_raw_execute_success(ARGS)
        self.mocker.throw(DatabaseError('connection closed'))
        self.mocker.replay()

        install_tracer(tracer_mock)
        self.connection.is_disconnection_error = (
            lambda exc, extra_disconnection_errors=():
                'connection closed' in str(exc))

        self.assertRaises(DisconnectionError,
                          self.connection.execute, "something")

    def test_tracing_error_check_disconnect(self):
        cursor_mock = self.mocker.patch(RawCursor)
        cursor_mock.execute(ARGS)
        error = ZeroDivisionError()
        self.mocker.throw(error)
        tracer = FakeTracer()
        tracer_mock = self.mocker.patch(tracer)
        tracer_mock.connection_raw_execute(ARGS)
        tracer_mock.connection_raw_execute_error(ARGS)
        self.mocker.throw(DatabaseError('connection closed'))
        self.mocker.replay()

        install_tracer(tracer_mock)
        self.connection.is_disconnection_error = (
            lambda exc, extra_disconnection_errors=():
                'connection closed' in str(exc))

        self.assertRaises(DisconnectionError,
                          self.connection.execute, "something")

    def test_commit(self):
        self.connection.commit()
        self.assertEquals(self.executed, ["COMMIT"])

    def test_commit_tracing(self):
        self.assertMethodsMatch(FakeTracer, DebugTracer)
        tracer = FakeTracer()
        install_tracer(tracer)
        self.connection.commit()
        self.assertEquals(tracer.seen, [("COMMIT", self.connection, None)])

    def test_rollback(self):
        self.connection.rollback()
        self.assertEquals(self.executed, ["ROLLBACK"])

    def test_rollback_tracing(self):
        self.assertMethodsMatch(FakeTracer, DebugTracer)
        tracer = FakeTracer()
        install_tracer(tracer)
        self.connection.rollback()
        self.assertEquals(tracer.seen, [("ROLLBACK", self.connection, None)])

    def test_close(self):
        self.connection.close()
        self.assertEquals(self.executed, ["CCLOSE"])

    def test_close_twice(self):
        self.connection.close()
        self.connection.close()
        self.assertEquals(self.executed, ["CCLOSE"])

    def test_close_deallocates_raw_connection(self):
        refs_before = len(gc.get_referrers(self.raw_connection))
        self.connection.close()
        refs_after = len(gc.get_referrers(self.raw_connection))
        self.assertEquals(refs_after, refs_before-1)

    def test_del_deallocates_raw_connection(self):
        refs_before = len(gc.get_referrers(self.raw_connection))
        self.connection.__del__()
        refs_after = len(gc.get_referrers(self.raw_connection))
        self.assertEquals(refs_after, refs_before-1)

    def test_wb_del_with_previously_deallocated_connection(self):
        self.connection._raw_connection = None
        self.connection.__del__()

    def test_get_insert_identity(self):
        result = self.connection.execute("INSERT")
        self.assertRaises(NotImplementedError,
                          result.get_insert_identity, None, None)

    def test_wb_ensure_connected_noop(self):
        """Check that _ensure_connected() is a no-op for STATE_CONNECTED."""
        self.assertEqual(self.connection._state, storm.database.STATE_CONNECTED)
        def connect():
            raise DatabaseError("_ensure_connected() tried to connect")
        self.database.raw_connect = connect
        self.connection._ensure_connected()

    def test_wb_ensure_connected_dead_connection(self):
        """Check that DisconnectionError is raised for STATE_DISCONNECTED."""
        self.connection._state = storm.database.STATE_DISCONNECTED
        self.assertRaises(DisconnectionError,
                          self.connection._ensure_connected)

    def test_wb_ensure_connected_reconnects(self):
        """Check that _ensure_connected() reconnects for STATE_RECONNECT."""
        self.connection._state = storm.database.STATE_RECONNECT
        self.connection._raw_connection = None

        self.connection._ensure_connected()
        self.assertNotEqual(self.connection._raw_connection, None)
        self.assertEqual(self.connection._state,
                         storm.database.STATE_CONNECTED)

    def test_wb_ensure_connected_connect_failure(self):
        """Check that the connection is flagged on reconnect failures."""
        self.connection._state = storm.database.STATE_RECONNECT
        self.connection._raw_connection = None
        def _fail_to_connect():
            raise DatabaseError("could not connect")
        self.database.raw_connect = _fail_to_connect

        self.assertRaises(DisconnectionError,
                          self.connection._ensure_connected)
        self.assertEqual(self.connection._state,
                         storm.database.STATE_DISCONNECTED)
        self.assertEqual(self.connection._raw_connection, None)

    def test_wb_check_disconnection(self):
        """Ensure that _check_disconnect() detects disconnections."""
        class FakeException(DatabaseError):
            """A fake database exception that indicates a disconnection."""
        self.connection.is_disconnection_error = (
            lambda exc, extra_disconnection_errors=():
                isinstance(exc, FakeException))

        self.assertEqual(self.connection._state,
                         storm.database.STATE_CONNECTED)
        # Error is converted to DisconnectionError:
        def raise_exception():
            raise FakeException
        self.assertRaises(DisconnectionError,
                          self.connection._check_disconnect, raise_exception)
        self.assertEqual(self.connection._state,
                         storm.database.STATE_DISCONNECTED)
        self.assertEqual(self.connection._raw_connection, None)

    def test_wb_check_disconnection_extra_errors(self):
        """Ensure that _check_disconnect() can check for additional
        exceptions."""
        class FakeException(DatabaseError):
            """A fake database exception that indicates a disconnection."""
        self.connection.is_disconnection_error = (
            lambda exc, extra_disconnection_errors=():
                isinstance(exc, extra_disconnection_errors))

        self.assertEqual(self.connection._state,
                         storm.database.STATE_CONNECTED)
        # Error is converted to DisconnectionError:
        def raise_exception():
            raise FakeException
        # Exception passes through as normal.
        self.assertRaises(FakeException,
                          self.connection._check_disconnect, raise_exception)
        self.assertEqual(self.connection._state,
                         storm.database.STATE_CONNECTED)
        # Exception treated as a disconnection when keyword argument passed.
        self.assertRaises(DisconnectionError,
                          self.connection._check_disconnect, raise_exception,
                          extra_disconnection_errors=FakeException)
        self.assertEqual(self.connection._state,
                         storm.database.STATE_DISCONNECTED)

    def test_wb_rollback_clears_disconnected_connection(self):
        """Check that rollback clears the DISCONNECTED state."""
        self.connection._state = storm.database.STATE_DISCONNECTED
        self.connection._raw_connection = None

        self.connection.rollback()
        self.assertEqual(self.executed, [])
        self.assertEqual(self.connection._state,
                         storm.database.STATE_RECONNECT)


class ResultTest(TestHelper):

    def setUp(self):
        TestHelper.setUp(self)
        self.executed = []
        self.raw_cursor = RawCursor(executed=self.executed)
        self.result = Result(FakeConnection(), self.raw_cursor)

    def test_get_one(self):
        self.assertEquals(self.result.get_one(), ("fetchone0",))
        self.assertEquals(self.result.get_one(), ("fetchone1",))
        self.assertEquals(self.result.get_one(), ("fetchone2",))
        self.assertEquals(self.result.get_one(), None)

    def test_get_all(self):
        self.assertEquals(self.result.get_all(),
                          [("fetchall0",), ("fetchall1",)])
        self.assertEquals(self.result.get_all(), [])

    def test_iter(self):
        result = Result(FakeConnection(), RawCursor(2))
        self.assertEquals([item for item in result],
                          [("fetchmany0",), ("fetchmany1",), ("fetchmany2",),
                           ("fetchmany3",), ("fetchmany4",)])

    def test_set_variable(self):
        variable = Variable()
        self.result.set_variable(variable, marker)
        self.assertEquals(variable.get(), marker)

    def test_close(self):
        self.result.close()
        self.assertEquals(self.executed, ["RCLOSE"])

    def test_close_twice(self):
        self.result.close()
        self.result.close()
        self.assertEquals(self.executed, ["RCLOSE"])

    def test_close_deallocates_raw_cursor(self):
        refs_before = len(gc.get_referrers(self.raw_cursor))
        self.result.close()
        refs_after = len(gc.get_referrers(self.raw_cursor))
        self.assertEquals(refs_after, refs_before-1)

    def test_del_deallocates_raw_cursor(self):
        refs_before = len(gc.get_referrers(self.raw_cursor))
        self.result.__del__()
        refs_after = len(gc.get_referrers(self.raw_cursor))
        self.assertEquals(refs_after, refs_before-1)

    def test_wb_del_with_previously_deallocated_cursor(self):
        self.result._raw_cursor = None
        self.result.__del__()

    def test_set_arraysize(self):
        """When the arraysize is 1, change it to a better value."""
        raw_cursor = RawCursor()
        self.assertEquals(raw_cursor.arraysize, 1)
        result = Result(FakeConnection(), raw_cursor)
        self.assertEquals(raw_cursor.arraysize, 10)

    def test_preserve_arraysize(self):
        """When the arraysize is not 1, preserve it."""
        raw_cursor = RawCursor(arraysize=123)
        result = Result(FakeConnection(), raw_cursor)
        self.assertEquals(raw_cursor.arraysize, 123)


class CreateDatabaseTest(TestHelper):

    def setUp(self):
        TestHelper.setUp(self)
        self.db_module = new.module("db_module")
        self.uri = None
        def create_from_uri(uri):
            self.uri = uri
            return "RESULT"
        self.db_module.create_from_uri = create_from_uri
        sys.modules["storm.databases.db_module"] = self.db_module

    def tearDown(self):
        del sys.modules["storm.databases.db_module"]
        TestHelper.tearDown(self)

    def test_create_database_with_str(self):
        create_database("db_module:db")
        self.assertTrue(self.uri)
        self.assertEquals(self.uri.scheme, "db_module")
        self.assertEquals(self.uri.database, "db")

    def test_create_database_with_unicode(self):
        create_database(u"db_module:db")
        self.assertTrue(self.uri)
        self.assertEquals(self.uri.scheme, "db_module")
        self.assertEquals(self.uri.database, "db")

    def test_create_database_with_uri(self):
        uri = URI("db_module:db")
        create_database(uri)
        self.assertTrue(self.uri is uri)


class RegisterSchemeTest(TestHelper):

    uri = None

    def tearDown(self):
        if 'factory' in storm.database._database_schemes:
            del storm.database._database_schemes['factory']
        TestHelper.tearDown(self)

    def test_register_scheme(self):
        def factory(uri):
            self.uri = uri
            return "FACTORY RESULT"
        register_scheme('factory', factory)
        self.assertEqual(storm.database._database_schemes['factory'], factory)
        # Check that we can create databases that use this scheme ...
        result = create_database('factory:foobar')
        self.assertEqual(result, "FACTORY RESULT")
        self.assertTrue(self.uri)
        self.assertEqual(self.uri.scheme, 'factory')
        self.assertEqual(self.uri.database, 'foobar')
