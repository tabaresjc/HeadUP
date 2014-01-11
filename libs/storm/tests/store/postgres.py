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
import gc

from storm.database import create_database
from storm.properties import Enum, Int, List
from storm.info import get_obj_info

from tests.store.base import StoreTest, EmptyResultSetTest, Foo
from tests.helper import TestHelper


class Lst1(object):
    __storm_table__ = "lst1"
    id = Int(primary=True)
    ints = List(type=Int())

class LstEnum(object):
    __storm_table__ = "lst1"
    id = Int(primary=True)
    ints = List(type=Enum(map={"one": 1, "two": 2, "three": 3}))

class Lst2(object):
    __storm_table__ = "lst2"
    id = Int(primary=True)
    ints = List(type=List(type=Int()))

class FooWithSchema(Foo):
    __storm_table__ = "public.foo"


class PostgresStoreTest(TestHelper, StoreTest):

    def setUp(self):
        TestHelper.setUp(self)
        StoreTest.setUp(self)

    def tearDown(self):
        TestHelper.tearDown(self)
        StoreTest.tearDown(self)

    def is_supported(self):
        return bool(os.environ.get("STORM_POSTGRES_URI"))

    def create_database(self):
        self.database = create_database(os.environ["STORM_POSTGRES_URI"])

    def create_tables(self):
        connection = self.connection
        connection.execute("CREATE TABLE foo "
                           "(id SERIAL PRIMARY KEY,"
                           " title VARCHAR DEFAULT 'Default Title')")
        # Prevent dynamically created Foos from having conflicting ids.
        connection.execute("SELECT setval('foo_id_seq', 1000)")
        connection.execute("CREATE TABLE bar "
                           "(id SERIAL PRIMARY KEY,"
                           " foo_id INTEGER, title VARCHAR)")
        connection.execute("CREATE TABLE bin "
                           "(id SERIAL PRIMARY KEY, bin BYTEA, foo_id INTEGER)")
        connection.execute("CREATE TABLE link "
                           "(foo_id INTEGER, bar_id INTEGER,"
                           " PRIMARY KEY (foo_id, bar_id))")
        connection.execute("CREATE TABLE money "
                           "(id SERIAL PRIMARY KEY, value NUMERIC(6,4))")
        connection.execute("CREATE TABLE selfref "
                           "(id SERIAL PRIMARY KEY, title VARCHAR,"
                           " selfref_id INTEGER REFERENCES selfref(id))")
        connection.execute("CREATE TABLE lst1 "
                           "(id SERIAL PRIMARY KEY, ints INTEGER[])")
        connection.execute("CREATE TABLE lst2 "
                           "(id SERIAL PRIMARY KEY, ints INTEGER[][])")
        connection.execute("CREATE TABLE foovalue "
                           "(id SERIAL PRIMARY KEY, foo_id INTEGER,"
                           " value1 INTEGER, value2 INTEGER)")
        connection.execute("CREATE TABLE unique_id "
                           "(id UUID PRIMARY KEY)")
        connection.commit()

    def drop_tables(self):
        StoreTest.drop_tables(self)
        for table in ["lst1", "lst2"]:
            try:
                self.connection.execute("DROP TABLE %s" % table)
                self.connection.commit()
            except:
                self.connection.rollback()

    def test_list_variable(self):

        lst = Lst1()
        lst.id = 1
        lst.ints = [1,2,3,4]

        self.store.add(lst)

        result = self.store.execute("SELECT ints FROM lst1 WHERE id=1")
        self.assertEquals(result.get_one(), ([1,2,3,4],))

        del lst
        gc.collect()

        lst = self.store.find(Lst1, Lst1.ints == [1,2,3,4]).one()
        self.assertTrue(lst)

        lst.ints.append(5)

        result = self.store.execute("SELECT ints FROM lst1 WHERE id=1")
        self.assertEquals(result.get_one(), ([1,2,3,4,5],))

    def test_list_enum_variable(self):

        lst = LstEnum()
        lst.id = 1
        lst.ints = ["one", "two"]
        self.store.add(lst)

        result = self.store.execute("SELECT ints FROM lst1 WHERE id=1")
        self.assertEquals(result.get_one(), ([1,2],))

        del lst
        gc.collect()

        lst = self.store.find(LstEnum, LstEnum.ints == ["one", "two"]).one()
        self.assertTrue(lst)

        lst.ints.append("three")

        result = self.store.execute("SELECT ints FROM lst1 WHERE id=1")
        self.assertEquals(result.get_one(), ([1,2,3],))

    def test_list_variable_nested(self):

        lst = Lst2()
        lst.id = 1
        lst.ints = [[1, 2], [3, 4]]

        self.store.add(lst)

        result = self.store.execute("SELECT ints FROM lst2 WHERE id=1")
        self.assertEquals(result.get_one(), ([[1,2],[3,4]],))

        del lst
        gc.collect()

        lst = self.store.find(Lst2, Lst2.ints == [[1,2],[3,4]]).one()
        self.assertTrue(lst)

        lst.ints.append([5, 6])

        result = self.store.execute("SELECT ints FROM lst2 WHERE id=1")
        self.assertEquals(result.get_one(), ([[1,2],[3,4],[5,6]],))

    def test_add_find_with_schema(self):
        foo = FooWithSchema()
        foo.title = u"Title"
        self.store.add(foo)
        self.store.flush()
        # We use find() here to actually exercise the backend code.
        # get() would just pick the object from the cache.
        self.assertEquals(self.store.find(FooWithSchema, id=foo.id).one(), foo)

    def test_wb_currval_based_identity(self):
        """
        Ensure that the currval()-based identity retrieval continues
        to work, even if we're currently running on a 8.2+ database.
        """
        self.database._version = 80109
        foo1 = self.store.add(Foo())
        self.store.flush()
        foo2 = self.store.add(Foo())
        self.store.flush()
        self.assertEquals(foo2.id-foo1.id, 1)

    def test_list_unnecessary_update(self):
        """
        Flushing an object with a list variable doesn't create an unnecessary
        UPDATE statement.
        """
        self.store.execute("INSERT INTO lst1 VALUES (1, '{}')", noresult=True)

        lst = self.store.find(Lst1, id=1).one()
        self.assertTrue(lst)
        self.store.invalidate()

        lst2 = self.store.find(Lst1, id=1).one()
        self.assertTrue(lst2)
        obj_info = get_obj_info(lst2)
        events = []
        obj_info.event.hook("changed", lambda *args: events.append(args))
        self.store.flush()
        self.assertEquals(events, [])


class PostgresEmptyResultSetTest(TestHelper, EmptyResultSetTest):

    def setUp(self):
        TestHelper.setUp(self)
        EmptyResultSetTest.setUp(self)

    def tearDown(self):
        TestHelper.tearDown(self)
        EmptyResultSetTest.tearDown(self)

    def is_supported(self):
        return bool(os.environ.get("STORM_POSTGRES_URI"))

    def create_database(self):
        self.database = create_database(os.environ["STORM_POSTGRES_URI"])

    def create_tables(self):
        self.connection.execute("CREATE TABLE foo "
                                "(id SERIAL PRIMARY KEY,"
                                " title VARCHAR DEFAULT 'Default Title')")
        self.connection.commit()
