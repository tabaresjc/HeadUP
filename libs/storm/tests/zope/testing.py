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
import os
import sys

from tests.helper import TestHelper
from tests.zope import has_transaction, has_zope_component, has_testresources

from storm.locals import create_database, Store, Unicode, Int
from storm.exceptions import IntegrityError
from storm.testing import CaptureTracer

if has_transaction and has_zope_component and has_testresources:
    from zope.component import provideUtility, getUtility
    from storm.zope.zstorm import ZStorm, global_zstorm
    from storm.zope.interfaces import IZStorm
    from storm.zope.schema import ZSchema
    from storm.zope.testing import ZStormResourceManager


PATCH = """
def apply(store):
    store.execute('ALTER TABLE test ADD COLUMN bar INT')
"""


class ZStormResourceManagerTest(TestHelper):

    def is_supported(self):
        return has_transaction and has_zope_component and has_testresources

    def setUp(self):
        super(ZStormResourceManagerTest, self).setUp()
        package_dir = self.makeDir()
        sys.path.append(package_dir)
        self.patch_dir = os.path.join(package_dir, "patch_package")
        os.mkdir(self.patch_dir)
        self.makeFile(path=os.path.join(self.patch_dir, "__init__.py"),
                      content="")
        self.makeFile(path=os.path.join(self.patch_dir, "patch_1.py"),
                      content=PATCH)
        import patch_package
        create = ["CREATE TABLE test (foo TEXT UNIQUE, bar INT)"]
        drop = ["DROP TABLE test"]
        delete = ["DELETE FROM test"]
        uri = "sqlite:///%s" % self.makeFile()
        schema = ZSchema(create, drop, delete, patch_package)
        self.databases = [{"name": "test", "uri": uri, "schema": schema}]
        self.resource = ZStormResourceManager(self.databases)
        self.store = Store(create_database(uri))

    def tearDown(self):
        global_zstorm._reset()
        del sys.modules["patch_package"]
        if "patch_1" in sys.modules:
            del sys.modules["patch_1"]
        super(ZStormResourceManagerTest, self).tearDown()

    def test_make(self):
        """
        L{ZStormResourceManager.make} returns a L{ZStorm} resource that can be
        used to get the registered L{Store}s.
        """
        zstorm = self.resource.make([])
        store = zstorm.get("test")
        self.assertEqual([], list(store.execute("SELECT foo, bar FROM test")))

    def test_make_lazy(self):
        """
        L{ZStormResourceManager.make} does not create all stores upfront, but
        only when they're actually used, likewise L{ZStorm.get}.
        """
        zstorm = self.resource.make([])
        self.assertEqual([], list(zstorm.iterstores()))
        store = zstorm.get("test")
        self.assertEqual([("test", store)], list(zstorm.iterstores()))

    def test_make_upgrade(self):
        """
        L{ZStormResourceManager.make} upgrades the schema if needed.
        """
        self.store.execute("CREATE TABLE patch "
                           "(version INTEGER NOT NULL PRIMARY KEY)")
        self.store.execute("CREATE TABLE test (foo TEXT)")
        self.store.commit()
        zstorm = self.resource.make([])
        store = zstorm.get("test")
        self.assertEqual([], list(store.execute("SELECT bar FROM test")))

    def test_make_upgrade_unknown_patch(self):
        """
        L{ZStormResourceManager.make} resets the schema if an unknown patch
        is found
        """
        self.store.execute("CREATE TABLE patch "
                           "(version INTEGER NOT NULL PRIMARY KEY)")
        self.store.execute("INSERT INTO patch VALUES (2)")
        self.store.execute("CREATE TABLE test (foo TEXT, egg BOOL)")
        self.store.commit()
        zstorm = self.resource.make([])
        store = zstorm.get("test")
        self.assertEqual([], list(store.execute("SELECT foo, bar FROM test")))
        self.assertEqual([(1,)],
                         list(store.execute("SELECT version FROM patch")))

    def test_make_delete(self):
        """
        L{ZStormResourceManager.make} deletes the data from all tables to make
        sure that tests run against a clean database.
        """
        self.store.execute("CREATE TABLE patch "
                           "(version INTEGER NOT NULL PRIMARY KEY)")
        self.store.execute("CREATE TABLE test (foo TEXT)")
        self.store.execute("INSERT INTO test (foo) VALUES ('data')")
        self.store.commit()
        zstorm = self.resource.make([])
        store = zstorm.get("test")
        self.assertEqual([], list(store.execute("SELECT foo FROM test")))

    def test_make_commits_transaction_once(self):
        """
        L{ZStormResourceManager.make} commits schema changes only once
        across all stores, after all patch and delete statements have
        been executed.
        """
        database2 = {"name": "test2",
                     "uri": "sqlite:///%s" % self.makeFile(),
                     "schema": self.databases[0]["schema"]}
        self.databases.append(database2)
        other_store = Store(create_database(database2["uri"]))
        for store in [self.store, other_store]:
            store.execute("CREATE TABLE patch "
                          "(version INTEGER NOT NULL PRIMARY KEY)")
            store.execute("CREATE TABLE test (foo TEXT)")
            store.execute("INSERT INTO test (foo) VALUES ('data')")
            store.commit()

        with CaptureTracer() as tracer:
            zstorm = self.resource.make([])

        self.assertEqual(["COMMIT", "COMMIT"], tracer.queries[-2:])
        store1 = zstorm.get("test")
        store2 = zstorm.get("test2")
        self.assertEqual([], list(store1.execute("SELECT foo FROM test")))
        self.assertEqual([], list(store2.execute("SELECT foo FROM test")))

    def test_make_zstorm_overwritten(self):
        """
        L{ZStormResourceManager.make} registers its own ZStorm again if a test
        has registered a new ZStorm utility overwriting the resource one.
        """
        zstorm = self.resource.make([])
        provideUtility(ZStorm())
        self.resource.make([])
        self.assertIs(zstorm, getUtility(IZStorm))

    def test_clean_flush(self):
        """
        L{ZStormResourceManager.clean} tries to flush the stores to make sure
        that they are all in a consistent state.
        """
        class Test(object):
            __storm_table__ = "test"
            foo = Unicode()
            bar = Int(primary=True)

            def __init__(self, foo, bar):
                self.foo = foo
                self.bar = bar

        zstorm = self.resource.make([])
        store = zstorm.get("test")
        store.add(Test(u"data", 1))
        store.add(Test(u"data", 2))
        self.assertRaises(IntegrityError, self.resource.clean, zstorm)

    def test_clean_delete(self):
        """
        L{ZStormResourceManager.clean} cleans the database tables from the data
        created by the tests.
        """
        zstorm = self.resource.make([])
        store = zstorm.get("test")
        store.execute("INSERT INTO test (foo, bar) VALUES ('data', 123)")
        store.commit()
        self.resource.clean(zstorm)
        self.assertEqual([], list(self.store.execute("SELECT * FROM test")))

    def test_clean_with_force_delete(self):
        """
        If L{ZStormResourceManager.force_delete} is C{True}, L{Schema.delete}
        is always invoked upon test cleanup.
        """
        zstorm = self.resource.make([])
        zstorm.get("test")  # Force the creation of the store
        self.store.execute("INSERT INTO test (foo, bar) VALUES ('data', 123)")
        self.store.commit()
        self.resource.force_delete = True
        self.resource.clean(zstorm)
        self.assertEqual([], list(self.store.execute("SELECT * FROM test")))

    def test_wb_clean_clears_alive_cache_before_abort(self):
        """
        L{ZStormResourceManager.clean} clears the alive cache before
        aborting the transaction.
        """
        class Test(object):
            __storm_table__ = "test"
            bar = Int(primary=True)

            def __init__(self, bar):
                self.bar = bar

        zstorm = self.resource.make([])
        store = zstorm.get("test")
        store.add(Test(1))
        store.add(Test(2))
        real_invalidate = store.invalidate

        def invalidate_proxy():
            self.assertEqual(0, len(store._alive.values()))
            real_invalidate()
        store.invalidate = invalidate_proxy

        self.resource.clean(zstorm)

    def test_schema_uri(self):
        """
        It's possible to specify an alternate URI for applying the schema
        and cleaning up tables after a test.
        """
        schema_uri = "sqlite:///%s" % self.makeFile()
        self.databases[0]["schema-uri"] = schema_uri
        zstorm = self.resource.make([])
        store = zstorm.get("test")
        schema_store = Store(create_database(schema_uri))

        # The schema was applied using the alternate schema URI
        statement = "SELECT name FROM sqlite_master WHERE name='patch'"
        self.assertEqual([], list(store.execute(statement)))
        self.assertEqual([("patch",)], list(schema_store.execute(statement)))

        # The cleanup is performed with the alternate schema URI
        store.commit()
        schema_store.execute("INSERT INTO test (foo) VALUES ('data')")
        schema_store.commit()
        self.resource.clean(zstorm)
        self.assertEqual([], list(schema_store.execute("SELECT * FROM test")))

    def test_schema_uri_with_schema_stamp_dir(self):
        """
        If a schema stamp directory is set, and the stamp indicates there's no
        need to update the schema, the resource clean up code will still
        connect as schema user if it needs to run the schema delete statements
        because of a commit.
        """
        self.resource.schema_stamp_dir = self.makeFile()
        self.databases[0]["schema-uri"] = self.databases[0]["uri"]
        self.resource.make([])

        # Simulate a second test run that initializes the zstorm resource
        # from scratch, using the same schema stamp directory
        resource2 = ZStormResourceManager(self.databases)
        resource2.schema_stamp_dir = self.resource.schema_stamp_dir
        zstorm = resource2.make([])
        store = zstorm.get("test")
        store.execute("INSERT INTO test (foo) VALUES ('data')")
        store.commit()  # Committing will force a schema.delete() run
        resource2.clean(zstorm)
        self.assertEqual([], list(store.execute("SELECT * FROM test")))

    def test_no_schema(self):
        """
        A particular database may have no schema associated.
        """
        self.databases[0]["schema"] = None
        zstorm = self.resource.make([])
        store = zstorm.get("test")
        self.assertEqual([],
                         list(store.execute("SELECT * FROM sqlite_master")))

    def test_no_schema_clean(self):
        """
        A particular database may have no schema associated. If it's committed
        during tests, it will just be skipped when cleaning up tables.
        """
        self.databases[0]["schema"] = None
        zstorm = self.resource.make([])
        store = zstorm.get("test")
        store.commit()

        with CaptureTracer() as tracer:
            self.resource.clean(zstorm)

        self.assertEqual([], tracer.queries)

    def test_deprecated_database_format(self):
        """
        The old deprecated format of the 'database' constructor parameter is
        still supported.
        """
        import patch_package
        uri = "sqlite:///%s" % self.makeFile()
        schema = ZSchema([], [], [], patch_package)
        resource = ZStormResourceManager({"test": (uri, schema)})
        zstorm = resource.make([])
        store = zstorm.get("test")
        self.assertIsNot(None, store)

    def test_use_global_zstorm(self):
        """
        If the C{use_global_zstorm} attribute is C{True} then the global
        L{ZStorm} will be used.
        """
        self.resource.use_global_zstorm = True
        zstorm = self.resource.make([])
        self.assertIs(global_zstorm, zstorm)

    def test_provide_utility_before_patches(self):
        """
        The L{IZStorm} utility is provided before patches are applied, in order
        to let them get it if they need.
        """
        content = ("from zope.component import getUtility\n"
                   "from storm.zope.interfaces import IZStorm\n"
                   "def apply(store):\n"
                   "    getUtility(IZStorm)\n")
        self.makeFile(path=os.path.join(self.patch_dir, "patch_2.py"),
                      content=content)
        self.store.execute("CREATE TABLE patch "
                           "(version INTEGER NOT NULL PRIMARY KEY)")
        self.store.execute("CREATE TABLE test (foo TEXT)")
        self.store.commit()
        zstorm = self.resource.make([])
        store = zstorm.get("test")
        self.assertEqual([(1,), (2,)],
                         sorted(store.execute("SELECT version FROM patch")))

    def test_create_schema_stamp_dir(self):
        """
        If a schema stamp directory is set, it's created automatically if it
        doesn't exist yet.
        """
        self.resource.schema_stamp_dir = self.makeFile()
        self.resource.make([])
        self.assertTrue(os.path.exists(self.resource.schema_stamp_dir))

    def test_use_schema_stamp(self):
        """
        If a schema stamp directory is set, then it's used to decide whether
        to upgrade the schema or not. In case the patch directory hasn't been
        changed since the last known upgrade, no schema upgrade is run.
        """
        self.resource.schema_stamp_dir = self.makeFile()

        self.resource.make([])

        # Simulate a second test run that initializes the zstorm resource
        # from scratch, using the same schema stamp directory
        resource2 = ZStormResourceManager(self.databases)
        resource2.schema_stamp_dir = self.resource.schema_stamp_dir

        with CaptureTracer() as tracer:
            resource2.make([])

        self.assertEqual([], tracer.queries)

    def test_use_schema_stamp_out_of_date(self):
        """
        If a schema stamp directory is set, then it's used to decide whether
        to upgrade the schema or not. In case the patch directory has changed
        a schema upgrade is run.
        """
        self.resource.schema_stamp_dir = self.makeFile()
        self.resource.make([])

        # Simulate a second test run that initializes the zstorm resource
        # from scratch, using the same schema stamp directory
        resource2 = ZStormResourceManager(self.databases)
        resource2.schema_stamp_dir = self.resource.schema_stamp_dir

        self.makeFile(path=os.path.join(self.patch_dir, "patch_2.py"),
                      content="def apply(store): pass")

        class FakeStat(object):
            st_mtime = os.stat(self.patch_dir).st_mtime + 1

        stat_mock = self.mocker.replace(os.stat)
        stat_mock(self.patch_dir)
        self.mocker.result(FakeStat())
        self.mocker.replay()

        resource2.make([])
        result = self.store.execute("SELECT version FROM patch")
        self.assertEqual([(1,), (2,)], sorted(result.get_all()))
