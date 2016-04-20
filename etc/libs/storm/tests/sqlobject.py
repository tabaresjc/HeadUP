#
# Copyright (c) 2006-2010 Canonical
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
import datetime
import operator

from storm.database import create_database
from storm.exceptions import NoneError
from storm.sqlobject import *
from storm.store import Store
from storm.tz import tzutc

from tests.helper import TestHelper


class SQLObjectTest(TestHelper):

    def setUp(self):
        TestHelper.setUp(self)

        # Allow classes with the same name in different tests to resolve
        # property path strings properly.
        SQLObjectBase._storm_property_registry.clear()

        self.store = Store(create_database("sqlite:"))
        class SQLObject(SQLObjectBase):
            @staticmethod
            def _get_store():
                return self.store

        self.SQLObject = SQLObject

        self.store.execute("CREATE TABLE person "
                           "(id INTEGER PRIMARY KEY, name TEXT, age INTEGER,"
                           " ts TIMESTAMP, delta INTERVAL,"
                           " address_id INTEGER)")
        self.store.execute("INSERT INTO person VALUES "
                           "(1, 'John Joe', 20, '2007-02-05 19:53:15',"
                           " '1 day, 12:34:56', 1)")
        self.store.execute("INSERT INTO person VALUES "
                           "(2, 'John Doe', 20, '2007-02-05 20:53:15',"
                           " '42 days 12:34:56.78', 2)")

        self.store.execute("CREATE TABLE address "
                           "(id INTEGER PRIMARY KEY, city TEXT)")
        self.store.execute("INSERT INTO address VALUES (1, 'Curitiba')")
        self.store.execute("INSERT INTO address VALUES (2, 'Sao Carlos')")

        self.store.execute("CREATE TABLE phone "
                           "(id INTEGER PRIMARY KEY, person_id INTEGER,"
                           "number TEXT)")
        self.store.execute("INSERT INTO phone VALUES (1, 2, '1234-5678')")
        self.store.execute("INSERT INTO phone VALUES (2, 1, '8765-4321')")
        self.store.execute("INSERT INTO phone VALUES (3, 2, '8765-5678')")

        self.store.execute("CREATE TABLE person_phone "
                           "(id INTEGER PRIMARY KEY, person_id INTEGER, "
                           "phone_id INTEGER)")
        self.store.execute("INSERT INTO person_phone VALUES (1, 2, 1)")
        self.store.execute("INSERT INTO person_phone VALUES (2, 2, 2)")
        self.store.execute("INSERT INTO person_phone VALUES (3, 1, 1)")

        class Person(self.SQLObject):
            _defaultOrder = "-Person.name"
            name = StringCol()
            age = IntCol()
            ts = UtcDateTimeCol()

        self.Person = Person

    def test_get(self):
        person = self.Person.get(2)
        self.assertTrue(person)
        self.assertEquals(person.name, "John Doe")

    def test_get_not_found(self):
        self.assertRaises(SQLObjectNotFound, self.Person.get, 1000)

    def test_get_typecast(self):
        person = self.Person.get("2")
        self.assertTrue(person)
        self.assertEquals(person.name, "John Doe")

    def test_destroySelf(self):
        person = self.Person.get(2)
        person.destroySelf()
        self.assertRaises(SQLObjectNotFound, self.Person.get, 2)

    def test_delete(self):
        self.Person.delete(2)
        self.assertRaises(SQLObjectNotFound, self.Person.get, 2)

    def test_custom_table_name(self):
        class MyPerson(self.Person):
            _table = "person"

        person = MyPerson.get(2)

        self.assertTrue(person)
        self.assertEquals(person.name, "John Doe")

    def test_custom_id_name(self):
        class MyPerson(self.SQLObject):
            _defaultOrder = "-Person.name"
            _table = "person"
            _idName = "name"
            _idType = unicode
            age = IntCol()
            ts = UtcDateTimeCol()

        person = MyPerson.get("John Doe")

        self.assertTrue(person)
        self.assertEquals(person.id, "John Doe")

    def test_create(self):
        person = self.Person(name="John Joe")

        self.assertTrue(Store.of(person) is self.store)
        self.assertEquals(type(person.id), int)
        self.assertEquals(person.name, "John Joe")

    def test_SO_creating(self):
        test = self
        class Person(self.Person):
            def set(self, **args):
                test.assertEquals(self._SO_creating, True)
                test.assertEquals(args, {"name": "John Joe"})

        person = Person(name="John Joe")
        self.assertEquals(person._SO_creating, False)

    def test_object_not_added_if__create_fails(self):
        objects = []
        class Person(self.Person):
            def _create(self, id, **kwargs):
                objects.append(self)
                raise RuntimeError
        self.assertRaises(RuntimeError, Person, name="John Joe")
        self.assertEquals(len(objects), 1)
        person = objects[0]
        self.assertEquals(Store.of(person), None)

    def test_init_hook(self):
        called = []
        class Person(self.Person):
            def _init(self, *args, **kwargs):
                called.append(True)

        person = Person(name="John Joe")
        self.assertEquals(called, [True])
        Person.get(2)
        self.assertEquals(called, [True, True])

    def test_alternateID(self):
        class Person(self.SQLObject):
            name = StringCol(alternateID=True)
        person = Person.byName("John Doe")
        self.assertTrue(person)
        self.assertEquals(person.name, "John Doe")

    def test_alternateMethodName(self):
        class Person(self.SQLObject):
            name = StringCol(alternateMethodName="byFoo")

        person = Person.byFoo("John Doe")
        self.assertTrue(person)
        self.assertEquals(person.name, "John Doe")

        self.assertRaises(SQLObjectNotFound, Person.byFoo, "John None")

    def test_select(self):
        result = self.Person.select("name = 'John Joe'")
        self.assertEquals(result[0].name, "John Joe")

    def test_select_sqlbuilder(self):
        result = self.Person.select(self.Person.q.name == "John Joe")
        self.assertEqual(result[0].name, "John Joe")

    def test_select_orderBy(self):
        result = self.Person.select("name LIKE 'John%'", orderBy=("name","id"))
        self.assertEquals(result[0].name, "John Doe")

    def test_select_orderBy_expr(self):
        result = self.Person.select("name LIKE 'John%'",
                                    orderBy=self.Person.name)
        self.assertEquals(result[0].name, "John Doe")

    def test_select_all(self):
        result = self.Person.select()
        self.assertEquals(result[0].name, "John Joe")

    def test_select_empty_string(self):
        result = self.Person.select('')
        self.assertEquals(result[0].name, "John Joe")

    def test_select_limit(self):
        result = self.Person.select(limit=1)
        self.assertEquals(len(list(result)), 1)

    def test_select_negative_offset(self):
        result = self.Person.select(orderBy="name")
        self.assertEquals(result[-1].name, "John Joe")

    def test_select_slice_negative_offset(self):
        result = self.Person.select(orderBy="name")[-1:]
        self.assertEquals(result[0].name, "John Joe")

    def test_select_distinct(self):
        result = self.Person.select("person.name = 'John Joe'",
                                    clauseTables=["phone"], distinct=True)
        self.assertEquals(len(list(result)), 1)

    def test_select_selectAlso(self):
        # Since John Doe has two phone numbers, this would return him
        # twice without the distinct=True bit.
        result = self.Person.select(
            "person.id = phone.person_id",
            clauseTables=["phone"],
            selectAlso="LOWER(name) AS lower_name",
            orderBy="lower_name",
            distinct=True)
        people = list(result)
        self.assertEquals(len(people), 2)
        self.assertEquals(people[0].name, "John Doe")
        self.assertEquals(people[1].name, "John Joe")

    def test_select_selectAlso_with_prejoin(self):
        class Person(self.Person):
            address = ForeignKey(foreignKey="Address", dbName="address_id",
                                 notNull=True)

        class Address(self.SQLObject):
            city = StringCol()

        result = Person.select(
            prejoins=["address"],
            selectAlso="LOWER(person.name) AS lower_name",
            orderBy="lower_name")
        people = list(result)
        self.assertEquals(len(people), 2)
        self.assertEquals([(person.name, person.address.city)
                           for person in people],
                          [("John Doe", "Sao Carlos"),
                           ("John Joe", "Curitiba")])

    def test_select_clauseTables_simple(self):
        result = self.Person.select("name = 'John Joe'", ["person"])
        self.assertEquals(result[0].name, "John Joe")

    def test_select_clauseTables_implicit_join(self):
        result = self.Person.select("person.name = 'John Joe' and "
                                    "phone.person_id = person.id",
                                    ["person", "phone"])
        self.assertEquals(result[0].name, "John Joe")

    def test_select_clauseTables_no_cls_table(self):
        result = self.Person.select("person.name = 'John Joe' and "
                                    "phone.person_id = person.id",
                                    ["phone"])
        self.assertEquals(result[0].name, "John Joe")

    def test_selectBy(self):
        result = self.Person.selectBy(name="John Joe")
        self.assertEquals(result[0].name, "John Joe")

    def test_selectBy_orderBy(self):
        result = self.Person.selectBy(age=20, orderBy="name")
        self.assertEquals(result[0].name, "John Doe")

        result = self.Person.selectBy(age=20, orderBy="-name")
        self.assertEquals(result[0].name, "John Joe")

    def test_selectOne(self):
        person = self.Person.selectOne("name = 'John Joe'")

        self.assertTrue(person)
        self.assertEquals(person.name, "John Joe")

        nobody = self.Person.selectOne("name = 'John None'")

        self.assertEquals(nobody, None)

        # SQLBuilder style expression:
        person = self.Person.selectOne(self.Person.q.name == "John Joe")

        self.assertNotEqual(person, None)
        self.assertEqual(person.name, "John Joe")

    def test_selectOne_multiple_results(self):
        self.assertRaises(SQLObjectMoreThanOneResultError,
                          self.Person.selectOne)

    def test_selectOne_clauseTables(self):
        person = self.Person.selectOne("person.name = 'John Joe' and "
                                       "phone.person_id = person.id",
                                       ["phone"])
        self.assertEquals(person.name, "John Joe")

    def test_selectOneBy(self):
        person = self.Person.selectOneBy(name="John Joe")

        self.assertTrue(person)
        self.assertEquals(person.name, "John Joe")

        nobody = self.Person.selectOneBy(name="John None")

        self.assertEquals(nobody, None)

    def test_selectOneBy_multiple_results(self):
        self.assertRaises(SQLObjectMoreThanOneResultError,
                          self.Person.selectOneBy)

    def test_selectFirst(self):
        person = self.Person.selectFirst("name LIKE 'John%'", orderBy="name")

        self.assertTrue(person)
        self.assertEquals(person.name, "John Doe")

        person = self.Person.selectFirst("name LIKE 'John%'", orderBy="-name")

        self.assertTrue(person)
        self.assertEquals(person.name, "John Joe")

        nobody = self.Person.selectFirst("name = 'John None'", orderBy="name")

        self.assertEquals(nobody, None)

        # SQLBuilder style expression:
        person = self.Person.selectFirst(LIKE(self.Person.q.name, "John%"),
                                         orderBy="name")
        self.assertNotEqual(person, None)
        self.assertEqual(person.name, "John Doe")

    def test_selectFirst_default_order(self):
        person = self.Person.selectFirst("name LIKE 'John%'")

        self.assertTrue(person)
        self.assertEquals(person.name, "John Joe")

    def test_selectFirst_default_order_list(self):
        class Person(self.Person):
            _defaultOrder = ["name"]

        person = Person.selectFirst("name LIKE 'John%'")

        self.assertTrue(person)
        self.assertEquals(person.name, "John Doe")

    def test_selectFirst_default_order_expr(self):
        class Person(self.Person):
            _defaultOrder = [SQLConstant("name")]

        person = Person.selectFirst("name LIKE 'John%'")

        self.assertTrue(person)
        self.assertEquals(person.name, "John Doe")

    def test_selectFirst_default_order_fully_qualified(self):
        class Person(self.Person):
            _defaultOrder = ["person.name"]

        person = Person.selectFirst("name LIKE 'John%'")

        self.assertTrue(person)
        self.assertEquals(person.name, "John Doe")

    def test_selectFirstBy(self):
        person = self.Person.selectFirstBy(age=20, orderBy="name")

        self.assertTrue(person)
        self.assertEquals(person.name, "John Doe")

        person = self.Person.selectFirstBy(age=20, orderBy="-name")

        self.assertTrue(person)
        self.assertEquals(person.name, "John Joe")

        nobody = self.Person.selectFirstBy(age=1000, orderBy="name")

        self.assertEquals(nobody, None)

    def test_selectFirstBy_default_order(self):
        person = self.Person.selectFirstBy(age=20)

        self.assertTrue(person)
        self.assertEquals(person.name, "John Joe")

    def test_syncUpdate(self):
        """syncUpdate() flushes pending changes to the database."""
        person = self.Person.get(id=1)
        person.name = "John Smith"
        person.syncUpdate()
        name = self.store.execute(
            "SELECT name FROM person WHERE id = 1").get_one()[0]
        self.assertEquals(name, "John Smith")

    def test_sync(self):
        """sync() flushes pending changes and invalidates the cache."""
        person = self.Person.get(id=1)
        person.name = "John Smith"
        person.sync()
        name = self.store.execute(
            "SELECT name FROM person WHERE id = 1").get_one()[0]
        self.assertEquals(name, "John Smith")
        # Now make a change behind Storm's back and show that sync()
        # makes the new value from the database visible.
        self.store.execute("UPDATE person SET name = 'Jane Smith' "
                           "WHERE id = 1", noresult=True)
        person.sync()
        self.assertEquals(person.name, "Jane Smith")

    def test_col_name(self):
        class Person(self.SQLObject):
            foo = StringCol(dbName="name")
        person = Person.get(2)
        self.assertEquals(person.foo, "John Doe")

        class Person(self.SQLObject):
            foo = StringCol("name")
        person = Person.get(2)
        self.assertEquals(person.foo, "John Doe")

    def test_col_default(self):
        class Person(self.SQLObject):
            name = StringCol(default="Johny")
        person = Person()
        self.assertEquals(person.name, "Johny")

    def test_col_default_factory(self):
        class Person(self.SQLObject):
            name = StringCol(default=lambda: "Johny")
        person = Person()
        self.assertEquals(person.name, "Johny")

    def test_col_not_null(self):
        class Person(self.SQLObject):
            name = StringCol(notNull=True)
        person = Person.get(2)
        self.assertRaises(NoneError, setattr, person, "name", None)

    def test_col_storm_validator(self):
        calls = []
        def validator(obj, attr, value):
            calls.append((obj, attr, value))
            return value
        class Person(self.SQLObject):
            name = StringCol(storm_validator=validator)
        person = Person.get(2)
        person.name = u'foo'
        self.assertEquals(calls, [(person, 'name', u'foo')])

    def test_string_col(self):
        class Person(self.SQLObject):
            name = StringCol()
        person = Person.get(2)
        self.assertEquals(person.name, "John Doe")

    def test_int_col(self):
        class Person(self.SQLObject):
            age = IntCol()
        person = Person.get(2)
        self.assertEquals(person.age, 20)

    def test_bool_col(self):
        class Person(self.SQLObject):
            age = BoolCol()
        person = Person.get(2)
        self.assertEquals(person.age, True)

    def test_float_col(self):
        class Person(self.SQLObject):
            age = FloatCol()
        person = Person.get(2)
        self.assertTrue(abs(person.age - 20.0) < 1e-6)

    def test_utcdatetime_col(self):
        class Person(self.SQLObject):
            ts = UtcDateTimeCol()
        person = Person.get(2)
        self.assertEquals(person.ts,
                          datetime.datetime(2007, 2, 5, 20, 53, 15,
                                            tzinfo=tzutc()))
    def test_date_col(self):
        class Person(self.SQLObject):
            ts = DateCol()
        person = Person.get(2)
        self.assertEquals(person.ts, datetime.date(2007, 2, 5))

    def test_interval_col(self):
        class Person(self.SQLObject):
            delta = IntervalCol()
        person = Person.get(2)
        self.assertEquals(person.delta, datetime.timedelta(42, 45296, 780000))

    def test_foreign_key(self):
        class Person(self.Person):
            address = ForeignKey(foreignKey="Address", dbName="address_id",
                                 notNull=True)

        class Address(self.SQLObject):
            city = StringCol()

        person = Person.get(2)

        self.assertEquals(person.addressID, 2)
        self.assertEquals(person.address.city, "Sao Carlos")

    def test_foreign_key_no_dbname(self):
        self.store.execute("CREATE TABLE another_person "
                           "(id INTEGER PRIMARY KEY, name TEXT, age INTEGER,"
                           " ts TIMESTAMP, address INTEGER)")
        self.store.execute("INSERT INTO another_person VALUES "
                           "(2, 'John Doe', 20, '2007-02-05 20:53:15', 2)")

        class AnotherPerson(self.Person):
            address = ForeignKey(foreignKey="Address", notNull=True)

        class Address(self.SQLObject):
            city = StringCol()

        person = AnotherPerson.get(2)

        self.assertEquals(person.addressID, 2)
        self.assertEquals(person.address.city, "Sao Carlos")

    def test_foreign_key_orderBy(self):
        class Person(self.Person):
            _defaultOrder = "address"
            address = ForeignKey(foreignKey="Address", dbName="address_id",
                                 notNull=True)

        class Address(self.SQLObject):
            city = StringCol()

        person = Person.selectFirst()
        self.assertEquals(person.addressID, 1)

    def test_foreign_key_storm_validator(self):
        calls = []
        def validator(obj, attr, value):
            calls.append((obj, attr, value))
            return value

        class Person(self.SQLObject):
            address = ForeignKey(foreignKey="Address", dbName="address_id",
                                 storm_validator=validator)

        class Address(self.SQLObject):
            city = StringCol()

        person = Person.get(2)
        address = Address.get(1)
        person.address = address
        self.assertEquals(calls, [(person, 'addressID', 1)])

    def test_multiple_join(self):
        class AnotherPerson(self.Person):
            _table = "person"
            phones = SQLMultipleJoin("Phone", joinColumn="person")

        class Phone(self.SQLObject):
            person = ForeignKey("AnotherPerson", dbName="person_id")
            number = StringCol()

        person = AnotherPerson.get(2)

        # Make sure that the result is wrapped.
        result = person.phones.orderBy("-number")

        self.assertEquals([phone.number for phone in result],
                          ["8765-5678", "1234-5678"])

        # Test add/remove methods.
        number = Phone.selectOneBy(number="1234-5678")
        person.removePhone(number)
        self.assertEquals(sorted(phone.number for phone in person.phones),
                          ["8765-5678"])
        person.addPhone(number)
        self.assertEquals(sorted(phone.number for phone in person.phones),
                          ["1234-5678", "8765-5678"])

    def test_multiple_join_prejoins(self):
        self.store.execute("ALTER TABLE phone ADD COLUMN address_id INT")
        self.store.execute("UPDATE phone SET address_id = 1")
        self.store.execute("UPDATE phone SET address_id = 2 WHERE id = 3")

        class AnotherPerson(self.Person):
            _table = "person"
            phones = SQLMultipleJoin("Phone", joinColumn="person",
                                     orderBy="number", prejoins=["address"])

        class Phone(self.SQLObject):
            person = ForeignKey("AnotherPerson", dbName="person_id")
            address = ForeignKey("Address", dbName="address_id")
            number = StringCol()

        class Address(self.SQLObject):
            city = StringCol()

        person = AnotherPerson.get(2)
        [phone1, phone2] = person.phones

        # Delete addresses behind Storm's back to show that the
        # addresses have been loaded.
        self.store.execute("DELETE FROM address")
        self.assertEquals(phone1.number, "1234-5678")
        self.assertEquals(phone1.address.city, "Curitiba")
        self.assertEquals(phone2.number, "8765-5678")
        self.assertEquals(phone2.address.city, "Sao Carlos")

    def test_related_join(self):
        class AnotherPerson(self.Person):
            _table = "person"
            phones = SQLRelatedJoin("Phone", otherColumn="phone_id",
                                    intermediateTable="PersonPhone",
                                    joinColumn="person_id", orderBy="id")

        class PersonPhone(self.Person):
            person_id = IntCol()
            phone_id = IntCol()

        class Phone(self.SQLObject):
            number = StringCol()

        person = AnotherPerson.get(2)

        self.assertEquals([phone.number for phone in person.phones],
                          ["1234-5678", "8765-4321"])

        # Make sure that the result is wrapped.
        result = person.phones.orderBy("-number")

        self.assertEquals([phone.number for phone in result],
                          ["8765-4321", "1234-5678"])

        # Test add/remove methods.
        number = Phone.selectOneBy(number="1234-5678")
        person.removePhone(number)
        self.assertEquals(sorted(phone.number for phone in person.phones),
                          ["8765-4321"])
        person.addPhone(number)
        self.assertEquals(sorted(phone.number for phone in person.phones),
                          ["1234-5678", "8765-4321"])

    def test_related_join_prejoins(self):
        self.store.execute("ALTER TABLE phone ADD COLUMN address_id INT")
        self.store.execute("UPDATE phone SET address_id = 1")
        self.store.execute("UPDATE phone SET address_id = 2 WHERE id = 2")

        class AnotherPerson(self.Person):
            _table = "person"
            phones = SQLRelatedJoin("Phone", otherColumn="phone_id",
                                    intermediateTable="PersonPhone",
                                    joinColumn="person_id", orderBy="id",
                                    prejoins=["address"])

        class PersonPhone(self.Person):
            person_id = IntCol()
            phone_id = IntCol()

        class Phone(self.SQLObject):
            number = StringCol()
            address = ForeignKey("Address", dbName="address_id")

        class Address(self.SQLObject):
            city = StringCol()

        person = AnotherPerson.get(2)
        [phone1, phone2] = person.phones

        # Delete addresses behind Storm's back to show that the
        # addresses have been loaded.
        self.store.execute("DELETE FROM address")
        self.assertEquals(phone1.number, "1234-5678")
        self.assertEquals(phone1.address.city, "Curitiba")
        self.assertEquals(phone2.number, "8765-4321")
        self.assertEquals(phone2.address.city, "Sao Carlos")

    def test_single_join(self):
        self.store.execute("CREATE TABLE office "
                           "(id INTEGER PRIMARY KEY, phone_id INTEGER,"
                           "name TEXT)")
        self.store.execute("INSERT INTO office VALUES (1, 1, 'An office')")

        class Phone(self.SQLObject):
            office = SingleJoin("Office", joinColumn="phoneID")

        class Office(self.SQLObject):
            phone = ForeignKey(foreignKey="Phone", dbName="phone_id",
                               notNull=True)
            name = StringCol()

        office = Office.get(1)
        self.assertEqual(office.name, "An office")

        phone = Phone.get(1)
        self.assertEqual(phone.office, office)

        # The single join returns None for a phone with no office
        phone = Phone.get(2)
        self.assertEqual(phone.office, None)

    def test_result_set_orderBy(self):
        result = self.Person.select()

        result = result.orderBy("-name")
        self.assertEquals([person.name for person in result],
                          ["John Joe", "John Doe"])

        result = result.orderBy("name")
        self.assertEquals([person.name for person in result],
                          ["John Doe", "John Joe"])

    def test_result_set_orderBy_fully_qualified(self):
        result = self.Person.select()

        result = result.orderBy("-person.name")
        self.assertEquals([person.name for person in result],
                          ["John Joe", "John Doe"])

        result = result.orderBy("person.name")
        self.assertEquals([person.name for person in result],
                          ["John Doe", "John Joe"])

    def test_result_set_count(self):
        result = self.Person.select()
        self.assertEquals(result.count(), 2)

    def test_result_set_count_limit(self):
        result = self.Person.select(limit=1)
        self.assertEquals(len(list(result)), 1)
        self.assertEquals(result.count(), 1)

    def test_result_set_count_sliced(self):
        result = self.Person.select()
        sliced_result = result[1:]
        self.assertEquals(len(list(sliced_result)), 1)
        self.assertEquals(sliced_result.count(), 1)

    def test_result_set_count_sliced_empty(self):
        result = self.Person.select()
        sliced_result = result[1:1]
        self.assertEquals(len(list(sliced_result)), 0)
        self.assertEquals(sliced_result.count(), 0)

    def test_result_set_count_sliced_empty_zero(self):
        result = self.Person.select()
        sliced_result = result[0:0]
        self.assertEquals(len(list(sliced_result)), 0)
        self.assertEquals(sliced_result.count(), 0)

    def test_result_set_count_sliced_none(self):
        result = self.Person.select()
        sliced_result = result[None:None]
        self.assertEquals(len(list(sliced_result)), 2)
        self.assertEquals(sliced_result.count(), 2)

    def test_result_set_count_sliced_start_none(self):
        result = self.Person.select()
        sliced_result = result[None:1]
        self.assertEquals(len(list(sliced_result)), 1)
        self.assertEquals(sliced_result.count(), 1)

    def test_result_set_count_sliced_end_none(self):
        result = self.Person.select()
        sliced_result = result[1:None]
        self.assertEquals(len(list(sliced_result)), 1)
        self.assertEquals(sliced_result.count(), 1)

    def test_result_set_count_distinct(self):
        result = self.Person.select(
            "person.id = phone.person_id",
            clauseTables=["phone"],
            distinct=True)
        self.assertEquals(result.count(), 2)

    def test_result_set_count_union_distinct(self):
        result1 = self.Person.select("person.id = 1", distinct=True)
        result2 = self.Person.select("person.id = 2", distinct=True)
        self.assertEquals(result1.union(result2).count(), 2)

    def test_result_set_count_with_joins(self):
        result = self.Person.select(
            "person.address_id = address.id",
            clauseTables=["address"])
        self.assertEquals(result.count(), 2)

    def test_result_set__getitem__(self):
        result = self.Person.select()
        self.assertEquals(result[0].name, "John Joe")

    def test_result_set__iter__(self):
        result = self.Person.select()
        self.assertEquals(list(result.__iter__())[0].name, "John Joe")

    def test_result_set__nonzero__(self):
        """
        L{SQLObjectResultSet.__nonzero__} returns C{True} if the result set
        contains results.  If it contains no results, C{False} is
        returned.
        """
        result = self.Person.select()
        self.assertEquals(result.__nonzero__(), True)
        result = self.Person.select(self.Person.q.name == "No Person")
        self.assertEquals(result.__nonzero__(), False)

    def test_result_set_is_empty(self):
        """
        L{SQLObjectResultSet.is_empty} returns C{True} if the result set
        doesn't contain any results.  If it does contain results, C{False} is
        returned.
        """
        result = self.Person.select()
        self.assertEquals(result.is_empty(), False)
        result = self.Person.select(self.Person.q.name == "No Person")
        self.assertEquals(result.is_empty(), True)

    def test_result_set_distinct(self):
        result = self.Person.select("person.name = 'John Joe'",
                                    clauseTables=["phone"])
        self.assertEquals(len(list(result.distinct())), 1)

    def test_result_set_limit(self):
        result = self.Person.select()
        self.assertEquals(len(list(result.limit(1))), 1)

    def test_result_set_union(self):
        result1 = self.Person.selectBy(id=1)
        result2 = self.Person.selectBy(id=2)
        result3 = result1.union(result2, orderBy="name")
        self.assertEquals([person.name for person in result3],
                          ["John Doe", "John Joe"])

    def test_result_set_union_all(self):
        result1 = self.Person.selectBy(id=1)
        result2 = result1.union(result1, unionAll=True)
        self.assertEquals([person.name for person in result2],
                          ["John Joe", "John Joe"])

    def test_result_set_except_(self):
        person = self.Person(id=3, name="John Moe")
        result1 = self.Person.select()
        result2 = self.Person.selectBy(id=2)
        result3 = result1.except_(result2, orderBy="name")
        self.assertEquals([person.name for person in result3],
                          ["John Joe", "John Moe"])

    def test_result_set_intersect(self):
        person = self.Person(id=3, name="John Moe")
        result1 = self.Person.select()
        result2 = self.Person.select(self.Person.id.is_in((2, 3)))
        result3 = result1.intersect(result2, orderBy="name")
        self.assertEquals([person.name for person in result3],
                          ["John Doe", "John Moe"])

    def test_result_set_prejoin(self):
        self.store.execute("ALTER TABLE person ADD COLUMN phone_id INTEGER")
        self.store.execute("UPDATE person SET phone_id=1 WHERE name='John Doe'")

        class Person(self.Person):
            address = ForeignKey(foreignKey="Address", dbName="address_id")
            phone = ForeignKey(foreignKey="Phone", dbName="phone_id")

        class Address(self.SQLObject):
            city = StringCol()

        class Phone(self.SQLObject):
            number = StringCol()

        result = Person.select("person.name = 'John Doe'")
        result = result.prejoin(["address", "phone"])

        people = list(result)

        # Remove rows behind its back.
        self.store.execute("DELETE FROM address")
        self.store.execute("DELETE FROM phone")

        # They were prefetched, so it should work even then.
        self.assertEquals([person.address.city for person in people],
                          ["Sao Carlos"])
        self.assertEquals([person.phone.number for person in people],
                          ["1234-5678"])

    def test_result_set_prejoin_getitem(self):
        """Ensure that detuplelizing is used on getitem."""

        class Person(self.Person):
            address = ForeignKey(foreignKey="Address", dbName="address_id")

        class Address(self.SQLObject):
            city = StringCol()

        result = Person.select("person.name = 'John Doe'", prejoins=["address"])
        person = result[0]

        # Remove the row behind its back.
        self.store.execute("DELETE FROM address")

        # They were prefetched, so it should work even then.
        self.assertEquals(person.address.city, "Sao Carlos")

    def test_result_set_prejoin_one(self):
        """Ensure that detuplelizing is used on selectOne()."""

        class Person(self.Person):
            address = ForeignKey(foreignKey="Address", dbName="address_id")

        class Address(self.SQLObject):
            city = StringCol()

        person = Person.selectOne("person.name = 'John Doe'",
                                  prejoins=["address"])

        # Remove the row behind its back.
        self.store.execute("DELETE FROM address")

        # They were prefetched, so it should work even then.
        self.assertEquals(person.address.city, "Sao Carlos")

    def test_result_set_prejoin_first(self):
        """Ensure that detuplelizing is used on selectFirst()."""

        class Person(self.Person):
            address = ForeignKey(foreignKey="Address", dbName="address_id")

        class Address(self.SQLObject):
            city = StringCol()

        person = Person.selectFirst("person.name = 'John Doe'",
                                    prejoins=["address"], orderBy="name")

        # Remove the row behind Storm's back.
        self.store.execute("DELETE FROM address")

        # They were prefetched, so it should work even then.
        self.assertEquals(person.address.city, "Sao Carlos")

    def test_result_set_prejoin_by(self):
        """Ensure that prejoins work with selectBy() queries."""

        class Person(self.Person):
            address = ForeignKey(foreignKey="Address", dbName="address_id")

        class Address(self.SQLObject):
            city = StringCol()

        result = Person.selectBy(name="John Doe").prejoin(["address"])
        person = result[0]

        # Remove the row behind Storm's back.
        self.store.execute("DELETE FROM address")

        # They were prefetched, so it should work even then.
        self.assertEquals(person.address.city, "Sao Carlos")

    def test_result_set_prejoin_related(self):
        """Dotted prejoins are used to prejoin through another table."""
        class Phone(self.SQLObject):
            person = ForeignKey(foreignKey="AnotherPerson", dbName="person_id")
            number = StringCol()

        class AnotherPerson(self.Person):
            _table = "person"
            address = ForeignKey(foreignKey="Address", dbName="address_id")

        class Address(self.SQLObject):
            city = StringCol()

        phone = Phone.selectOne("phone.number = '1234-5678'",
                                prejoins=["person.address"])

        # Remove the rows behind Storm's back.
        self.store.execute("DELETE FROM address")
        self.store.execute("DELETE FROM person")

        # They were prefetched, so it should work even then.
        self.assertEquals(phone.person.name, "John Doe")
        self.assertEquals(phone.person.address.city, "Sao Carlos")

    def test_result_set_prejoin_table_twice(self):
        """A single table can be prejoined multiple times."""
        self.store.execute("CREATE TABLE lease "
                           "(id INTEGER PRIMARY KEY,"
                           " landlord_id INTEGER, tenant_id INTEGER)")
        self.store.execute("INSERT INTO lease VALUES (1, 1, 2)")

        class Address(self.SQLObject):
            city = StringCol()

        class AnotherPerson(self.Person):
            _table = "person"
            address = ForeignKey(foreignKey="Address", dbName="address_id")

        class Lease(self.SQLObject):
            landlord = ForeignKey(foreignKey="AnotherPerson",
                                  dbName="landlord_id")
            tenant = ForeignKey(foreignKey="AnotherPerson",
                                dbName="tenant_id")

        lease = Lease.select(prejoins=["landlord", "landlord.address",
                                       "tenant", "tenant.address"])[0]

        # Remove the person rows behind Storm's back.
        self.store.execute("DELETE FROM address")
        self.store.execute("DELETE FROM person")

        self.assertEquals(lease.landlord.name, "John Joe")
        self.assertEquals(lease.landlord.address.city, "Curitiba")
        self.assertEquals(lease.tenant.name, "John Doe")
        self.assertEquals(lease.tenant.address.city, "Sao Carlos")

    def test_result_set_prejoin_count(self):
        """Prejoins do not affect the result of aggregates like COUNT()."""
        class Person(self.Person):
            address = ForeignKey(foreignKey="Address", dbName="address_id")

        class Address(self.SQLObject):
            city = StringCol()

        result = Person.select("name = 'John Doe'", prejoins=["address"])
        self.assertEquals(result.count(), 1)

    def test_result_set_prejoin_mismatch_union(self):
        """Prejoins do not cause UNION incompatibilities. """
        class Person(self.Person):
            address = ForeignKey(foreignKey="Address", dbName="address_id")

        class Address(self.SQLObject):
            city = StringCol()

        # The prejoin should not prevent the union from working.  At
        # the moment this is done by unconditionally stripping the
        # prejoins (which is what our SQLObject patch did), but could
        # be smarter.
        result1 = Person.select("name = 'John Doe'", prejoins=["address"])
        result2 = Person.select("name = 'John Joe'")
        result = result1.union(result2)
        names = sorted(person.name for person in result)
        self.assertEquals(names, ["John Doe", "John Joe"])

    def test_result_set_prejoin_mismatch_except(self):
        """Prejoins do not cause EXCEPT incompatibilities. """
        class Person(self.Person):
            address = ForeignKey(foreignKey="Address", dbName="address_id")

        class Address(self.SQLObject):
            city = StringCol()

        # The prejoin should not prevent the union from working.  At
        # the moment this is done by unconditionally stripping the
        # prejoins (which is what our SQLObject patch did), but could
        # be smarter.
        result1 = Person.select("name = 'John Doe'", prejoins=["address"])
        result2 = Person.select("name = 'John Joe'")
        result = result1.except_(result2)
        names = sorted(person.name for person in result)
        self.assertEquals(names, ["John Doe"])

    def test_result_set_prejoin_mismatch_intersect(self):
        """Prejoins do not cause INTERSECT incompatibilities. """
        class Person(self.Person):
            address = ForeignKey(foreignKey="Address", dbName="address_id")

        class Address(self.SQLObject):
            city = StringCol()

        # The prejoin should not prevent the union from working.  At
        # the moment this is done by unconditionally stripping the
        # prejoins (which is what our SQLObject patch did), but could
        # be smarter.
        result1 = Person.select("name = 'John Doe'", prejoins=["address"])
        result2 = Person.select("name = 'John Doe'")
        result = result1.intersect(result2)
        names = sorted(person.name for person in result)
        self.assertEquals(names, ["John Doe"])

    def test_result_set_prejoinClauseTables(self):
        self.store.execute("ALTER TABLE person ADD COLUMN phone_id INTEGER")
        self.store.execute("UPDATE person SET phone_id=1 WHERE name='John Doe'")

        class Person(self.Person):
            address = ForeignKey(foreignKey="AddressClass", dbName="address_id")
            phone = ForeignKey(foreignKey="PhoneClass", dbName="phone_id")

        # Name the class so that it doesn't match the table name, to ensure
        # that the prejoin is actually using table names, rather than class
        # names.
        class AddressClass(self.SQLObject):
            _table = "address"
            city = StringCol()

        class PhoneClass(self.SQLObject):
            _table = "phone"
            number = StringCol()

        result = Person.select("person.name = 'John Doe' and "
                               "person.phone_id = phone.id and "
                               "person.address_id = address.id",
                               clauseTables=["address", "phone"])
        result = result.prejoinClauseTables(["address", "phone"])

        people = list(result)

        # Remove rows behind its back.
        self.store.execute("DELETE FROM address")
        self.store.execute("DELETE FROM phone")

        # They were prefetched, so it should work even then.
        self.assertEquals([person.address.city for person in people],
                          ["Sao Carlos"])
        self.assertEquals([person.phone.number for person in people],
                          ["1234-5678"])

    def test_result_set_sum_string(self):
        result = self.Person.select()
        self.assertEquals(result.sum('age'), 40)

    def test_result_set_sum_expr(self):
        result = self.Person.select()
        self.assertEquals(result.sum(self.Person.q.age), 40)

    def test_result_set_contains(self):
        john = self.Person.selectOneBy(name="John Doe")
        self.assertTrue(john in self.Person.select())
        self.assertFalse(john in self.Person.selectBy(name="John Joe"))
        self.assertFalse(john in self.Person.select(
                "Person.name = 'John Joe'"))

    def test_result_set_contains_does_not_use_iter(self):
        """Calling 'item in result_set' does not iterate over the set. """
        def no_iter(self):
            raise RuntimeError
        real_iter = SQLObjectResultSet.__iter__
        SQLObjectResultSet.__iter__ = no_iter
        try:
            john = self.Person.selectOneBy(name="John Doe")
            self.assertTrue(john in self.Person.select())
        finally:
            SQLObjectResultSet.__iter__ = real_iter

    def test_result_set_contains_wrong_type(self):
        class Address(self.SQLObject):
            city = StringCol()

        address = Address.get(1)
        result_set = self.Person.select()
        self.assertRaises(TypeError, operator.contains, result_set, address)

    def test_result_set_contains_with_prejoins(self):
        class Person(self.Person):
            address = ForeignKey(foreignKey="Address", dbName="address_id")

        class Address(self.SQLObject):
            city = StringCol()

        john = Person.selectOneBy(name="John Doe")
        result_set = Person.select("name = 'John Doe'", prejoins=["address"])
        self.assertTrue(john in result_set)

    def test_table_dot_q(self):
        # Table.q.fieldname is a syntax used in SQLObject for
        # sqlbuilder expressions.  Storm can use the main properties
        # for this, so the Table.q syntax just returns those
        # properties:
        class Person(self.SQLObject):
            _idName = "name"
            _idType = unicode
            address = ForeignKey(foreignKey="Phone", dbName="address_id",
                                 notNull=True)

        self.assertEquals(id(Person.q.id), id(Person.id))
        self.assertEquals(id(Person.q.address), id(Person.address))
        self.assertEquals(id(Person.q.addressID), id(Person.addressID))

        person = Person.get("John Joe")

        self.assertEquals(id(person.q.id), id(Person.id))
        self.assertEquals(id(person.q.address), id(Person.address))
        self.assertEquals(id(person.q.addressID), id(Person.addressID))

    def test_set(self):
        class Person(self.Person):
            def set(self, **kw):
                kw["id"] += 1
                super(Person, self).set(**kw)
        person = Person(id=3, name="John Moe")
        self.assertEquals(person.id, 4)
        self.assertEquals(person.name, "John Moe")

    def test_CONTAINSSTRING(self):
        expr = CONTAINSSTRING(self.Person.q.name, "Do")
        result = self.Person.select(expr)
        self.assertEquals([person.name for person in result],
                          ["John Doe"])

        person.name = "Funny !%_ Name"

        expr = NOT(CONTAINSSTRING(self.Person.q.name, "!%_"))
        result = self.Person.select(expr)
        self.assertEquals([person.name for person in result],
                          ["John Joe"])

