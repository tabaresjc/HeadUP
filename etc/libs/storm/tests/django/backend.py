
# Copyright (c) 2008 Canonical
#
# Written by James Henstridge <jamesh@canonical.com>
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

import os

try:
    import django
    import transaction
except ImportError:
    have_django_and_transaction = False
else:
    have_django_and_transaction = True
    from django.conf import settings
    from storm.django import stores
    from storm.zope.zstorm import global_zstorm, StoreDataManager

import storm.database
from storm.exceptions import DisconnectionError

from tests.helper import TestHelper
from tests.databases.base import DatabaseDisconnectionMixin


def make_wrapper():
    from storm.django.backend import base
    if django.VERSION >= (1, 1):
        wrapper = base.DatabaseWrapper({
                'DATABASE_HOST': settings.DATABASE_HOST,
                'DATABASE_NAME': settings.DATABASE_NAME,
                'DATABASE_OPTIONS': settings.DATABASE_OPTIONS,
                'DATABASE_PASSWORD': settings.DATABASE_PASSWORD,
                'DATABASE_PORT': settings.DATABASE_PORT,
                'DATABASE_USER': settings.DATABASE_USER,
                'TIME_ZONE': settings.TIME_ZONE,
                'OPTIONS': {},
                })
    else:
        wrapper = base.DatabaseWrapper(**settings.DATABASE_OPTIONS)
    return wrapper


class DjangoBackendTests(object):

    def is_supported(self):
        return have_django_and_transaction and self.get_store_uri() is not None

    def setUp(self):
        super(DjangoBackendTests, self).setUp()
        settings.configure(STORM_STORES={})
        settings.MIDDLEWARE_CLASSES += (
            "storm.django.middleware.ZopeTransactionMiddleware",)

        settings.DATABASE_ENGINE = "storm.django.backend"
        settings.DATABASE_NAME = "django"
        settings.STORM_STORES["django"] = self.get_store_uri()
        stores.have_configured_stores = False
        self.create_tables()

    def tearDown(self):
        transaction.abort()
        self.drop_tables()
        if django.VERSION >= (1, 1):
            settings._wrapped = None
        else:
            settings._target = None
        global_zstorm._reset()
        stores.have_configured_stores = False
        transaction.manager.free(transaction.get())
        super(DjangoBackendTests, self).tearDown()

    def get_store_uri(self):
        raise NotImplementedError

    def get_wrapper_class(self):
        raise NotImplementedError

    def create_tables(self):
        raise NotImplementedError

    def drop_tables(self):
        raise NotImplementedError

    def test_create_wrapper(self):
        wrapper = make_wrapper()
        self.assertTrue(isinstance(wrapper, self.get_wrapper_class()))

        # The wrapper uses the same database connection as the store.
        store = stores.get_store("django")
        self.assertEqual(store._connection._raw_connection, wrapper.connection)

    def _isInTransaction(self, store):
        """Check if a Store is part of the current transaction."""
        for dm in transaction.get()._resources:
            if isinstance(dm, StoreDataManager) and dm._store is store:
                return True
        return False

    def assertInTransaction(self, store):
        """Check that the given store is joined to the transaction."""
        self.assertTrue(self._isInTransaction(store),
                        "%r should be joined to the transaction" % store)

    def test_using_wrapper_joins_transaction(self):
        wrapper = make_wrapper()
        cursor = wrapper.cursor()
        cursor.execute("SELECT 1")
        self.assertInTransaction(stores.get_store("django"))

    def test_commit(self):
        wrapper = make_wrapper()
        cursor = wrapper.cursor()
        cursor.execute("INSERT INTO django_test (title) VALUES ('foo')")
        wrapper._commit()

        cursor = wrapper.cursor()
        cursor.execute("SELECT title FROM django_test")
        result = cursor.fetchall()
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0][0], "foo")

    def test_rollback(self):
        wrapper = make_wrapper()
        cursor = wrapper.cursor()
        cursor.execute("INSERT INTO django_test (title) VALUES ('foo')")
        wrapper._rollback()

        cursor = wrapper.cursor()
        cursor.execute("SELECT title FROM django_test")
        result = cursor.fetchall()
        self.assertEqual(len(result), 0)

    def test_register_transaction(self):
        wrapper = make_wrapper()
        store = global_zstorm.get("django")
        # Watch for register-transaction calls.
        calls = []
        def register_transaction(owner):
            calls.append(owner)
        store._event.hook("register-transaction", register_transaction)

        cursor = wrapper.cursor()
        cursor.execute("SELECT 1")
        self.assertNotEqual(calls, [])

    def test_abort_transaction_on_failed_commit(self):
        _transaction = transaction.get()
        resource1 = self.mocker.mock()
        self.expect(resource1.prepare).throw(AttributeError).count(0)
        self.expect(resource1.tpc_begin(_transaction)).throw(DisconnectionError)
        self.expect(resource1.abort(_transaction)).count(2)
        self.expect(resource1.sortKey())
        self.mocker.replay()

        _transaction.join(resource1)
        wrapper = make_wrapper()
        cursor = wrapper.cursor()
        cursor.execute("INSERT INTO django_test (title) VALUES ('foo')")
        self.assertRaises(DisconnectionError, wrapper._commit)

        # Calling _get_connection on the wrapper after a failed commit should
        # work fine. Before the fix this would raise a
        # 'TransactionFailedError'.
        wrapper._get_connection()


class DjangoBackendDisconnectionTests(DatabaseDisconnectionMixin):

    def is_supported(self):
        if not have_django_and_transaction:
            return False
        return DatabaseDisconnectionMixin.is_supported(self)

    def setUp(self):
        super(DjangoBackendDisconnectionTests, self).setUp()
        settings.configure(STORM_STORES={})

        settings.DATABASE_ENGINE = "storm.django.backend"
        settings.DATABASE_NAME = "django"
        settings.STORM_STORES["django"] = str(self.proxy_uri)
        stores.have_configured_stores = False

    def tearDown(self):
        transaction.abort()
        if django.VERSION >= (1, 1):
            settings._wrapped = None
        else:
            settings._target = None
        global_zstorm._reset()
        stores.have_configured_stores = False
        transaction.manager.free(transaction.get())
        super(DjangoBackendDisconnectionTests, self).tearDown()

    def test_wb_disconnect(self):
        wrapper = make_wrapper()
        store = global_zstorm.get("django")
        cursor = wrapper.cursor()
        cursor.execute("SELECT 'about to reset connection'")
        wrapper._rollback()
        cursor = wrapper.cursor()
        self.proxy.restart()
        self.assertRaises(DisconnectionError, cursor.execute, "SELECT 1")
        self.assertEqual(
            store._connection._state, storm.database.STATE_DISCONNECTED)
        wrapper._rollback()

        self.assertEqual(
            store._connection._state, storm.database.STATE_RECONNECT)
        cursor = wrapper.cursor()
        cursor.execute("SELECT 1")

    def test_wb_transaction_registration(self):
        wrapper = make_wrapper()
        store = global_zstorm.get("django")
        # Watch for register-transaction calls.
        calls = []
        def register_transaction(owner):
            calls.append(owner)
        store._event.hook("register-transaction", register_transaction)

        # Simulate a disconnection, and put the connection into a
        # state where it would attempt to reconnect.
        store._connection._raw_connection = None
        store._connection._state = storm.database.STATE_RECONNECT
        self.proxy.stop()

        self.assertRaises(DisconnectionError, wrapper.cursor)
        # The connection is in the disconnected state, and has been
        # registered with any listening transaction manager.
        self.assertNotEqual(calls, [])
        self.assertEqual(
            store._connection._state, storm.database.STATE_DISCONNECTED)

        wrapper._rollback()
        del calls[:]

        # Now reconnect:
        self.proxy.start()
        cursor = wrapper.cursor()
        cursor.execute("SELECT 1")
        # The connection is up, and has been registered with any
        # listening transaction manager.
        self.assertNotEqual(calls, [])
        self.assertEqual(
            store._connection._state, storm.database.STATE_CONNECTED)


class PostgresDjangoBackendTests(DjangoBackendTests, TestHelper):

    def get_store_uri(self):
        return os.environ.get("STORM_POSTGRES_URI")

    def get_wrapper_class(self):
        from storm.django.backend import base
        return base.PostgresStormDatabaseWrapper

    def create_tables(self):
        store = stores.get_store("django")
        store.execute("CREATE TABLE django_test ("
                      "  id SERIAL PRIMARY KEY,"
                      "  title TEXT)")
        transaction.commit()

    def drop_tables(self):
        store = stores.get_store("django")
        store.execute("DROP TABLE django_test")
        transaction.commit()


class MySQLDjangoBackendTests(DjangoBackendTests, TestHelper):

    def get_store_uri(self):
        return os.environ.get("STORM_MYSQL_URI")

    def get_wrapper_class(self):
        from storm.django.backend import base
        return base.MySQLStormDatabaseWrapper

    def create_tables(self):
        store = stores.get_store("django")
        store.execute("CREATE TABLE django_test ("
                      "  id INT AUTO_INCREMENT PRIMARY KEY,"
                      "  title TEXT) ENGINE=InnoDB")
        transaction.commit()

    def drop_tables(self):
        store = stores.get_store("django")
        store.execute("DROP TABLE django_test")
        transaction.commit()

class PostgresDjangoBackendDisconnectionTests(
    DjangoBackendDisconnectionTests, TestHelper):

    environment_variable = "STORM_POSTGRES_URI"
    host_environment_variable = "STORM_POSTGRES_HOST_URI"
    default_port = 5432


class MySQLDjangoBackendDisconnectionTests(
    DjangoBackendDisconnectionTests, TestHelper):

    environment_variable = "STORM_MYSQL_URI"
    host_environment_variable = "STORM_MYSQL_HOST_URI"
    default_port = 3306
