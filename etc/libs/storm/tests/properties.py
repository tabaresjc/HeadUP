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
from datetime import datetime, date, time, timedelta
from decimal import Decimal as decimal
import gc
try:
    import uuid
except ImportError:
    uuid = None

from storm.compat import json
from storm.exceptions import NoneError, PropertyPathError
from storm.properties import PropertyPublisherMeta
from storm.properties import *
from storm.variables import *
from storm.info import get_obj_info
from storm.expr import Column, Select, compile, State, SQLRaw

from tests.info import Wrapper
from tests.helper import TestHelper


class CustomVariable(Variable):
    pass

class Custom(SimpleProperty):
    variable_class = CustomVariable


class PropertyTest(TestHelper):

    def setUp(self):
        TestHelper.setUp(self)
        class Class(object):
            __storm_table__ = "mytable"
            prop1 = Custom("column1", primary=True)
            prop2 = Custom()
            prop3 = Custom("column3", default=50, allow_none=False)
        class SubClass(Class):
            __storm_table__ = "mysubtable"
        self.Class = Class
        self.SubClass = SubClass

    def test_column(self):
        self.assertTrue(isinstance(self.Class.prop1, Column))

    def test_cls(self):
        self.assertEquals(self.Class.prop1.cls, self.Class)
        self.assertEquals(self.Class.prop2.cls, self.Class)
        self.assertEquals(self.SubClass.prop1.cls, self.SubClass)
        self.assertEquals(self.SubClass.prop2.cls, self.SubClass)
        self.assertEquals(self.Class.prop1.cls, self.Class)
        self.assertEquals(self.Class.prop2.cls, self.Class)

    def test_cls_reverse(self):
        self.assertEquals(self.SubClass.prop1.cls, self.SubClass)
        self.assertEquals(self.SubClass.prop2.cls, self.SubClass)
        self.assertEquals(self.Class.prop1.cls, self.Class)
        self.assertEquals(self.Class.prop2.cls, self.Class)
        self.assertEquals(self.SubClass.prop1.cls, self.SubClass)
        self.assertEquals(self.SubClass.prop2.cls, self.SubClass)

    def test_name(self):
        self.assertEquals(self.Class.prop1.name, "column1")

    def test_auto_name(self):
        self.assertEquals(self.Class.prop2.name, "prop2")

    def test_auto_table(self):
        self.assertEquals(self.Class.prop1.table, self.Class)
        self.assertEquals(self.Class.prop2.table, self.Class)

    def test_auto_table_subclass(self):
        self.assertEquals(self.Class.prop1.table, self.Class)
        self.assertEquals(self.Class.prop2.table, self.Class)
        self.assertEquals(self.SubClass.prop1.table, self.SubClass)
        self.assertEquals(self.SubClass.prop2.table, self.SubClass)

    def test_auto_table_subclass_reverse_initialization(self):
        self.assertEquals(self.SubClass.prop1.table, self.SubClass)
        self.assertEquals(self.SubClass.prop2.table, self.SubClass)
        self.assertEquals(self.Class.prop1.table, self.Class)
        self.assertEquals(self.Class.prop2.table, self.Class)

    def test_variable_factory(self):
        variable = self.Class.prop1.variable_factory()
        self.assertTrue(isinstance(variable, CustomVariable))
        self.assertFalse(variable.is_defined())

        variable = self.Class.prop3.variable_factory()
        self.assertTrue(isinstance(variable, CustomVariable))
        self.assertTrue(variable.is_defined())

    def test_variable_factory_validator_attribute(self):
        # Should work even if we make things harder by reusing properties.
        prop = Custom()
        class Class1(object):
            __storm_table__ = "table1"
            prop1 = prop
        class Class2(object):
            __storm_table__ = "table2"
            prop2 = prop
        args = []
        def validator(obj, attr, value):
            args.append((obj, attr, value))
        variable1 = Class1.prop1.variable_factory(validator=validator)
        variable2 = Class2.prop2.variable_factory(validator=validator)
        variable1.set(1)
        variable2.set(2)
        self.assertEquals(args, [(None, "prop1", 1), (None, "prop2", 2)])

    def test_default(self):
        obj = self.SubClass()
        self.assertEquals(obj.prop1, None)
        self.assertEquals(obj.prop2, None)
        self.assertEquals(obj.prop3, 50)

    def test_set_get(self):
        obj = self.Class()
        obj.prop1 = 10
        obj.prop2 = 20
        obj.prop3 = 30
        self.assertEquals(obj.prop1, 10)
        self.assertEquals(obj.prop2, 20)
        self.assertEquals(obj.prop3, 30)

    def test_set_get_none(self):
        obj = self.Class()
        obj.prop1 = None
        obj.prop2 = None
        self.assertEquals(obj.prop1, None)
        self.assertEquals(obj.prop2, None)
        self.assertRaises(NoneError, setattr, obj, "prop3", None)

    def test_set_with_validator(self):
        args = []
        def validator(obj, attr, value):
            args[:] = obj, attr, value
            return 42

        class Class(object):
            __storm_table__ = "mytable"
            prop = Custom("column", primary=True, validator=validator)

        obj = Class()
        obj.prop = 21

        self.assertEquals(args, [obj, "prop", 21])
        self.assertEquals(obj.prop, 42)

    def test_set_get_subclass(self):
        obj = self.SubClass()
        obj.prop1 = 10
        obj.prop2 = 20
        obj.prop3 = 30
        self.assertEquals(obj.prop1, 10)
        self.assertEquals(obj.prop2, 20)
        self.assertEquals(obj.prop3, 30)

    def test_set_get_explicitly(self):
        obj = self.Class()
        prop1 = self.Class.prop1
        prop2 = self.Class.prop2
        prop3 = self.Class.prop3
        prop1.__set__(obj, 10)
        prop2.__set__(obj, 20)
        prop3.__set__(obj, 30)
        self.assertEquals(prop1.__get__(obj), 10)
        self.assertEquals(prop2.__get__(obj), 20)
        self.assertEquals(prop3.__get__(obj), 30)

    def test_set_get_subclass_explicitly(self):
        obj = self.SubClass()
        prop1 = self.Class.prop1
        prop2 = self.Class.prop2
        prop3 = self.Class.prop3
        prop1.__set__(obj, 10)
        prop2.__set__(obj, 20)
        prop3.__set__(obj, 30)
        self.assertEquals(prop1.__get__(obj), 10)
        self.assertEquals(prop2.__get__(obj), 20)
        self.assertEquals(prop3.__get__(obj), 30)

    def test_delete(self):
        obj = self.Class()
        obj.prop1 = 10
        obj.prop2 = 20
        obj.prop3 = 30
        del obj.prop1
        del obj.prop2
        del obj.prop3
        self.assertEquals(obj.prop1, None)
        self.assertEquals(obj.prop2, None)
        self.assertEquals(obj.prop3, None)

    def test_delete_subclass(self):
        obj = self.SubClass()
        obj.prop1 = 10
        obj.prop2 = 20
        obj.prop3 = 30
        del obj.prop1
        del obj.prop2
        del obj.prop3
        self.assertEquals(obj.prop1, None)
        self.assertEquals(obj.prop2, None)
        self.assertEquals(obj.prop3, None)

    def test_delete_explicitly(self):
        obj = self.Class()
        obj.prop1 = 10
        obj.prop2 = 20
        obj.prop3 = 30
        self.Class.prop1.__delete__(obj)
        self.Class.prop2.__delete__(obj)
        self.Class.prop3.__delete__(obj)
        self.assertEquals(obj.prop1, None)
        self.assertEquals(obj.prop2, None)
        self.assertEquals(obj.prop3, None)

    def test_delete_subclass_explicitly(self):
        obj = self.SubClass()
        obj.prop1 = 10
        obj.prop2 = 20
        obj.prop3 = 30
        self.Class.prop1.__delete__(obj)
        self.Class.prop2.__delete__(obj)
        self.Class.prop3.__delete__(obj)
        self.assertEquals(obj.prop1, None)
        self.assertEquals(obj.prop2, None)
        self.assertEquals(obj.prop3, None)

    def test_comparable_expr(self):
        prop1 = self.Class.prop1
        prop2 = self.Class.prop2
        prop3 = self.Class.prop3
        expr = Select(SQLRaw("*"), (prop1 == "value1") &
                                   (prop2 == "value2") &
                                   (prop3 == "value3"))
        state = State()
        statement = compile(expr, state)
        self.assertEquals(statement, "SELECT * FROM mytable WHERE "
                                     "mytable.column1 = ? AND "
                                     "mytable.prop2 = ? AND "
                                     "mytable.column3 = ?")

        self.assertVariablesEqual(
            state.parameters,
            [CustomVariable("value1"),
             CustomVariable("value2"),
             CustomVariable("value3")])

    def test_comparable_expr_subclass(self):
        prop1 = self.SubClass.prop1
        prop2 = self.SubClass.prop2
        prop3 = self.SubClass.prop3
        expr = Select(SQLRaw("*"), (prop1 == "value1") &
                                   (prop2 == "value2") &
                                   (prop3 == "value3"))
        state = State()
        statement = compile(expr, state)
        self.assertEquals(statement, "SELECT * FROM mysubtable WHERE "
                                     "mysubtable.column1 = ? AND "
                                     "mysubtable.prop2 = ? AND "
                                     "mysubtable.column3 = ?")
        self.assertVariablesEqual(
            state.parameters,
            [CustomVariable("value1"),
             CustomVariable("value2"),
             CustomVariable("value3")])

    def test_set_get_delete_with_wrapper(self):
        obj = self.Class()
        get_obj_info(obj) # Ensure the obj_info exists for obj.
        self.Class.prop1.__set__(Wrapper(obj), 10)
        self.assertEquals(self.Class.prop1.__get__(Wrapper(obj)), 10)
        self.Class.prop1.__delete__(Wrapper(obj))
        self.assertEquals(self.Class.prop1.__get__(Wrapper(obj)), None)

    def test_reuse_of_instance(self):
        """Properties are dynamically bound to the class where they're used.

        It basically means that the property may be instantiated
        independently from the class itself, and reused in any number of
        classes.  It's not something we should announce as granted, but
        right now it works, and we should try not to break it.
        """
        prop = Custom()
        class Class1(object):
            __storm_table__ = "table1"
            prop1 = prop
        class Class2(object):
            __storm_table__ = "table2"
            prop2 = prop
        self.assertEquals(Class1.prop1.name, "prop1")
        self.assertEquals(Class1.prop1.table, Class1)
        self.assertEquals(Class2.prop2.name, "prop2")
        self.assertEquals(Class2.prop2.table, Class2)


class PropertyKindsTest(TestHelper):

    def setup(self, property, *args, **kwargs):
        prop2_kwargs = kwargs.pop("prop2_kwargs", {})
        kwargs["primary"] = True
        class Class(object):
            __storm_table__ = "mytable"
            prop1 = property("column1", *args, **kwargs)
            prop2 = property(**prop2_kwargs)
        class SubClass(Class):
            pass
        self.Class = Class
        self.SubClass = SubClass
        self.obj = SubClass()
        self.obj_info = get_obj_info(self.obj)
        self.column1 = self.SubClass.prop1
        self.column2 = self.SubClass.prop2
        self.variable1 = self.obj_info.variables[self.column1]
        self.variable2 = self.obj_info.variables[self.column2]

    def test_bool(self):
        self.setup(Bool, default=True, allow_none=False)

        self.assertTrue(isinstance(self.column1, Column))
        self.assertTrue(isinstance(self.column2, Column))
        self.assertEquals(self.column1.name, "column1")
        self.assertEquals(self.column1.table, self.SubClass)
        self.assertEquals(self.column2.name, "prop2")
        self.assertEquals(self.column2.table, self.SubClass)
        self.assertTrue(isinstance(self.variable1, BoolVariable))
        self.assertTrue(isinstance(self.variable2, BoolVariable))

        self.assertEquals(self.obj.prop1, True)
        self.assertRaises(NoneError, setattr, self.obj, "prop1", None)
        self.obj.prop2 = None
        self.assertEquals(self.obj.prop2, None)

        self.obj.prop1 = 1
        self.assertTrue(self.obj.prop1 is True)
        self.obj.prop1 = 0
        self.assertTrue(self.obj.prop1 is False)

    def test_int(self):
        self.setup(Int, default=50, allow_none=False)

        self.assertTrue(isinstance(self.column1, Column))
        self.assertTrue(isinstance(self.column2, Column))
        self.assertEquals(self.column1.name, "column1")
        self.assertEquals(self.column1.table, self.SubClass)
        self.assertEquals(self.column2.name, "prop2")
        self.assertEquals(self.column2.table, self.SubClass)
        self.assertTrue(isinstance(self.variable1, IntVariable))
        self.assertTrue(isinstance(self.variable2, IntVariable))

        self.assertEquals(self.obj.prop1, 50)
        self.assertRaises(NoneError, setattr, self.obj, "prop1", None)
        self.obj.prop2 = None
        self.assertEquals(self.obj.prop2, None)

        self.obj.prop1 = False
        self.assertEquals(self.obj.prop1, 0)
        self.obj.prop1 = True
        self.assertEquals(self.obj.prop1, 1)

    def test_float(self):
        self.setup(Float, default=50.5, allow_none=False)

        self.assertTrue(isinstance(self.column1, Column))
        self.assertTrue(isinstance(self.column2, Column))
        self.assertEquals(self.column1.name, "column1")
        self.assertEquals(self.column1.table, self.SubClass)
        self.assertEquals(self.column2.name, "prop2")
        self.assertEquals(self.column2.table, self.SubClass)
        self.assertTrue(isinstance(self.variable1, FloatVariable))
        self.assertTrue(isinstance(self.variable2, FloatVariable))

        self.assertEquals(self.obj.prop1, 50.5)
        self.assertRaises(NoneError, setattr, self.obj, "prop1", None)
        self.obj.prop2 = None
        self.assertEquals(self.obj.prop2, None)

        self.obj.prop1 = 1
        self.assertTrue(isinstance(self.obj.prop1, float))

    def test_decimal(self):
        self.setup(Decimal, default=decimal("50.5"), allow_none=False)

        self.assertTrue(isinstance(self.column1, Column))
        self.assertTrue(isinstance(self.column2, Column))
        self.assertEquals(self.column1.name, "column1")
        self.assertEquals(self.column1.table, self.SubClass)
        self.assertEquals(self.column2.name, "prop2")
        self.assertEquals(self.column2.table, self.SubClass)
        self.assertTrue(isinstance(self.variable1, DecimalVariable))
        self.assertTrue(isinstance(self.variable2, DecimalVariable))

        self.assertEquals(self.obj.prop1, decimal("50.5"))
        self.assertRaises(NoneError, setattr, self.obj, "prop1", None)
        self.obj.prop2 = None
        self.assertEquals(self.obj.prop2, None)

        self.obj.prop1 = 1
        self.assertTrue(isinstance(self.obj.prop1, decimal))

    def test_str(self):
        self.setup(RawStr, default="def", allow_none=False)

        self.assertTrue(isinstance(self.column1, Column))
        self.assertTrue(isinstance(self.column2, Column))
        self.assertEquals(self.column1.name, "column1")
        self.assertEquals(self.column1.table, self.SubClass)
        self.assertEquals(self.column2.name, "prop2")
        self.assertEquals(self.column2.table, self.SubClass)
        self.assertTrue(isinstance(self.variable1, RawStrVariable))
        self.assertTrue(isinstance(self.variable2, RawStrVariable))

        self.assertEquals(self.obj.prop1, "def")
        self.assertRaises(NoneError, setattr, self.obj, "prop1", None)
        self.obj.prop2 = None
        self.assertEquals(self.obj.prop2, None)

        self.assertRaises(TypeError, setattr, self.obj, "prop1", u"unicode")

    def test_unicode(self):
        self.setup(Unicode, default=u"def", allow_none=False)

        self.assertTrue(isinstance(self.column1, Column))
        self.assertTrue(isinstance(self.column2, Column))
        self.assertEquals(self.column1.name, "column1")
        self.assertEquals(self.column1.table, self.SubClass)
        self.assertEquals(self.column2.name, "prop2")
        self.assertEquals(self.column2.table, self.SubClass)
        self.assertTrue(isinstance(self.variable1, UnicodeVariable))
        self.assertTrue(isinstance(self.variable2, UnicodeVariable))

        self.assertEquals(self.obj.prop1, u"def")
        self.assertRaises(NoneError, setattr, self.obj, "prop1", None)
        self.obj.prop2 = None
        self.assertEquals(self.obj.prop2, None)

        self.assertRaises(TypeError, setattr, self.obj, "prop1", "str")

    def test_datetime(self):
        self.setup(DateTime, default=0, allow_none=False)

        self.assertTrue(isinstance(self.column1, Column))
        self.assertTrue(isinstance(self.column2, Column))
        self.assertEquals(self.column1.name, "column1")
        self.assertEquals(self.column1.table, self.SubClass)
        self.assertEquals(self.column2.name, "prop2")
        self.assertEquals(self.column2.table, self.SubClass)
        self.assertTrue(isinstance(self.variable1, DateTimeVariable))
        self.assertTrue(isinstance(self.variable2, DateTimeVariable))

        self.assertEquals(self.obj.prop1, datetime.utcfromtimestamp(0))
        self.assertRaises(NoneError, setattr, self.obj, "prop1", None)
        self.obj.prop2 = None
        self.assertEquals(self.obj.prop2, None)

        self.obj.prop1 = 0.0
        self.assertEquals(self.obj.prop1, datetime.utcfromtimestamp(0))
        self.obj.prop1 = datetime(2006, 1, 1, 12, 34)
        self.assertEquals(self.obj.prop1, datetime(2006, 1, 1, 12, 34))

        self.assertRaises(TypeError, setattr, self.obj, "prop1", object())

    def test_date(self):
        self.setup(Date, default=date(2006, 1, 1), allow_none=False)

        self.assertTrue(isinstance(self.column1, Column))
        self.assertTrue(isinstance(self.column2, Column))
        self.assertEquals(self.column1.name, "column1")
        self.assertEquals(self.column1.table, self.SubClass)
        self.assertEquals(self.column2.name, "prop2")
        self.assertEquals(self.column2.table, self.SubClass)
        self.assertTrue(isinstance(self.variable1, DateVariable))
        self.assertTrue(isinstance(self.variable2, DateVariable))

        self.assertEquals(self.obj.prop1, date(2006, 1, 1))
        self.assertRaises(NoneError, setattr, self.obj, "prop1", None)
        self.obj.prop2 = None
        self.assertEquals(self.obj.prop2, None)

        self.obj.prop1 = datetime(2006, 1, 1, 12, 34, 56)
        self.assertEquals(self.obj.prop1, date(2006, 1, 1))
        self.obj.prop1 = date(2006, 1, 1)
        self.assertEquals(self.obj.prop1, date(2006, 1, 1))

        self.assertRaises(TypeError, setattr, self.obj, "prop1", object())

    def test_time(self):
        self.setup(Time, default=time(12, 34), allow_none=False)

        self.assertTrue(isinstance(self.column1, Column))
        self.assertTrue(isinstance(self.column2, Column))
        self.assertEquals(self.column1.name, "column1")
        self.assertEquals(self.column1.table, self.SubClass)
        self.assertEquals(self.column2.name, "prop2")
        self.assertEquals(self.column2.table, self.SubClass)
        self.assertTrue(isinstance(self.variable1, TimeVariable))
        self.assertTrue(isinstance(self.variable2, TimeVariable))

        self.assertEquals(self.obj.prop1, time(12, 34))
        self.assertRaises(NoneError, setattr, self.obj, "prop1", None)
        self.obj.prop2 = None
        self.assertEquals(self.obj.prop2, None)

        self.obj.prop1 = datetime(2006, 1, 1, 12, 34, 56)
        self.assertEquals(self.obj.prop1, time(12, 34, 56))
        self.obj.prop1 = time(12, 34, 56)
        self.assertEquals(self.obj.prop1, time(12, 34, 56))

        self.assertRaises(TypeError, setattr, self.obj, "prop1", object())

    def test_timedelta(self):
        self.setup(TimeDelta,
                   default=timedelta(days=1, seconds=2, microseconds=3),
                   allow_none=False)

        self.assertTrue(isinstance(self.column1, Column))
        self.assertTrue(isinstance(self.column2, Column))
        self.assertEquals(self.column1.name, "column1")
        self.assertEquals(self.column1.table, self.SubClass)
        self.assertEquals(self.column2.name, "prop2")
        self.assertEquals(self.column2.table, self.SubClass)
        self.assertTrue(isinstance(self.variable1, TimeDeltaVariable))
        self.assertTrue(isinstance(self.variable2, TimeDeltaVariable))

        self.assertEquals(self.obj.prop1,
                          timedelta(days=1, seconds=2, microseconds=3))
        self.assertRaises(NoneError, setattr, self.obj, "prop1", None)
        self.obj.prop2 = None
        self.assertEquals(self.obj.prop2, None)

        self.obj.prop1 = timedelta(days=42, seconds=42, microseconds=42)
        self.assertEquals(self.obj.prop1,
                          timedelta(days=42, seconds=42, microseconds=42))

        self.assertRaises(TypeError, setattr, self.obj, "prop1", object())

    def test_uuid(self):
        # Skip test if uuid module is not available.
        if uuid is None:
            return

        value1 = uuid.UUID("{0609f76b-878f-4546-baf5-c1b135e8de72}")
        value2 = uuid.UUID("{c9703f9d-0abb-47d7-a793-8f90f1b98d5e}")
        self.setup(UUID, default=value1, allow_none=False)

        self.assertTrue(isinstance(self.column1, Column))
        self.assertTrue(isinstance(self.column2, Column))
        self.assertEquals(self.column1.name, "column1")
        self.assertEquals(self.column1.table, self.SubClass)
        self.assertEquals(self.column2.name, "prop2")
        self.assertEquals(self.column2.table, self.SubClass)
        self.assertTrue(isinstance(self.variable1, UUIDVariable))
        self.assertTrue(isinstance(self.variable2, UUIDVariable))

        self.assertEquals(self.obj.prop1, value1)
        self.assertRaises(NoneError, setattr, self.obj, "prop1", None)
        self.obj.prop2 = None
        self.assertEquals(self.obj.prop2, None)

        self.obj.prop1 = value1
        self.assertEquals(self.obj.prop1, value1)
        self.obj.prop1 = value2
        self.assertEquals(self.obj.prop1, value2)

        self.assertRaises(TypeError, setattr, self.obj, "prop1",
                          "{0609f76b-878f-4546-baf5-c1b135e8de72}")

    def test_enum(self):
        self.setup(Enum, map={"foo": 1, "bar": 2},
                   default="foo", allow_none=False,
                   prop2_kwargs=dict(map={"foo": 1, "bar": 2}))

        self.assertTrue(isinstance(self.column1, Column))
        self.assertTrue(isinstance(self.column2, Column))
        self.assertEquals(self.column1.name, "column1")
        self.assertEquals(self.column1.table, self.SubClass)
        self.assertEquals(self.column2.name, "prop2")
        self.assertEquals(self.column2.table, self.SubClass)
        self.assertTrue(isinstance(self.variable1, EnumVariable))
        self.assertTrue(isinstance(self.variable2, EnumVariable))

        self.assertEquals(self.obj.prop1, "foo")
        self.assertRaises(NoneError, setattr, self.obj, "prop1", None)
        self.obj.prop2 = None
        self.assertEquals(self.obj.prop2, None)

        self.obj.prop1 = "foo"
        self.assertEquals(self.obj.prop1, "foo")
        self.obj.prop1 = "bar"
        self.assertEquals(self.obj.prop1, "bar")

        self.assertRaises(ValueError, setattr, self.obj, "prop1", "baz")
        self.assertRaises(ValueError, setattr, self.obj, "prop1", 1)

    def test_enum_with_set_map(self):
        self.setup(Enum, map={"foo": 1, "bar": 2},
                   set_map={"fooics": 1, "barics": 2},
                   default="fooics", allow_none=False,
                   prop2_kwargs=dict(map={"foo": 1, "bar": 2}))

        self.assertTrue(isinstance(self.column1, Column))
        self.assertTrue(isinstance(self.column2, Column))
        self.assertEquals(self.column1.name, "column1")
        self.assertEquals(self.column1.table, self.SubClass)
        self.assertEquals(self.column2.name, "prop2")
        self.assertEquals(self.column2.table, self.SubClass)
        self.assertTrue(isinstance(self.variable1, EnumVariable))
        self.assertTrue(isinstance(self.variable2, EnumVariable))

        self.assertEquals(self.obj.prop1, "foo")
        self.assertRaises(NoneError, setattr, self.obj, "prop1", None)
        self.obj.prop2 = None
        self.assertEquals(self.obj.prop2, None)

        self.obj.prop1 = "fooics"
        self.assertEquals(self.obj.prop1, "foo")
        self.obj.prop1 = "barics"
        self.assertEquals(self.obj.prop1, "bar")

        self.assertRaises(ValueError, setattr, self.obj, "prop1", "foo")
        self.assertRaises(ValueError, setattr, self.obj, "prop1", 1)

    def test_pickle(self):
        self.setup(Pickle, default_factory=dict, allow_none=False)

        self.assertTrue(isinstance(self.column1, Column))
        self.assertTrue(isinstance(self.column2, Column))
        self.assertEquals(self.column1.name, "column1")
        self.assertEquals(self.column1.table, self.SubClass)
        self.assertEquals(self.column2.name, "prop2")
        self.assertEquals(self.column2.table, self.SubClass)
        self.assertTrue(isinstance(self.variable1, PickleVariable))
        self.assertTrue(isinstance(self.variable2, PickleVariable))

        self.assertEquals(self.obj.prop1, {})
        self.assertRaises(NoneError, setattr, self.obj, "prop1", None)
        self.obj.prop2 = None
        self.assertEquals(self.obj.prop2, None)

        self.obj.prop1 = []
        self.assertEquals(self.obj.prop1, [])
        self.obj.prop1.append("a")
        self.assertEquals(self.obj.prop1, ["a"])

    def test_pickle_events(self):
        self.setup(Pickle, default_factory=list, allow_none=False)

        changes = []
        def changed(owner, variable, old_value, new_value, fromdb):
            changes.append((variable, old_value, new_value, fromdb))

        # Can't checkpoint Undef.
        self.obj.prop2 = []

        self.obj_info.checkpoint()
        self.obj_info.event.emit("start-tracking-changes", self.obj_info.event)
        self.obj_info.event.hook("changed", changed)

        self.assertEquals(self.obj.prop1, [])
        self.assertEquals(changes, [])
        self.obj.prop1.append("a")
        self.assertEquals(changes, [])

        # Check "flush" event. Notice that the other variable wasn't
        # listed, since it wasn't changed.
        self.obj_info.event.emit("flush")
        self.assertEquals(changes, [(self.variable1, None, ["a"], False)])

        del changes[:]

        # Check "object-deleted" event. Notice that the other variable
        # wasn't listed again, since it wasn't changed.
        del self.obj
        self.assertEquals(changes, [(self.variable1, None, ["a"], False)])

    def test_json(self):
        # Skip test if json support is not available.
        if json is None:
            return

        self.setup(JSON, default_factory=dict, allow_none=False)

        self.assertTrue(isinstance(self.column1, Column))
        self.assertTrue(isinstance(self.column2, Column))
        self.assertEquals(self.column1.name, "column1")
        self.assertEquals(self.column1.table, self.SubClass)
        self.assertEquals(self.column2.name, "prop2")
        self.assertEquals(self.column2.table, self.SubClass)
        self.assertTrue(isinstance(self.variable1, JSONVariable))
        self.assertTrue(isinstance(self.variable2, JSONVariable))

        self.assertEquals(self.obj.prop1, {})
        self.assertRaises(NoneError, setattr, self.obj, "prop1", None)
        self.obj.prop2 = None
        self.assertEquals(self.obj.prop2, None)

        self.obj.prop1 = []
        self.assertEquals(self.obj.prop1, [])
        self.obj.prop1.append("a")
        self.assertEquals(self.obj.prop1, ["a"])

    def test_json_events(self):
        # Skip test if json support is not available.
        if json is None:
            return

        self.setup(JSON, default_factory=list, allow_none=False)

        changes = []
        def changed(owner, variable, old_value, new_value, fromdb):
            changes.append((variable, old_value, new_value, fromdb))

        # Can't checkpoint Undef.
        self.obj.prop2 = []

        self.obj_info.checkpoint()
        self.obj_info.event.emit("start-tracking-changes", self.obj_info.event)
        self.obj_info.event.hook("changed", changed)

        self.assertEquals(self.obj.prop1, [])
        self.assertEquals(changes, [])
        self.obj.prop1.append("a")
        self.assertEquals(changes, [])

        # Check "flush" event. Notice that the other variable wasn't
        # listed, since it wasn't changed.
        self.obj_info.event.emit("flush")
        self.assertEquals(changes, [(self.variable1, None, ["a"], False)])

        del changes[:]

        # Check "object-deleted" event. Notice that the other variable
        # wasn't listed again, since it wasn't changed.
        del self.obj
        self.assertEquals(changes, [(self.variable1, None, ["a"], False)])

    def test_list(self):
        self.setup(List, default_factory=list, allow_none=False)

        self.assertTrue(isinstance(self.column1, Column))
        self.assertTrue(isinstance(self.column2, Column))
        self.assertEquals(self.column1.name, "column1")
        self.assertEquals(self.column1.table, self.SubClass)
        self.assertEquals(self.column2.name, "prop2")
        self.assertEquals(self.column2.table, self.SubClass)
        self.assertTrue(isinstance(self.variable1, ListVariable))
        self.assertTrue(isinstance(self.variable2, ListVariable))

        self.assertEquals(self.obj.prop1, [])
        self.assertRaises(NoneError, setattr, self.obj, "prop1", None)
        self.obj.prop2 = None
        self.assertEquals(self.obj.prop2, None)

        self.obj.prop1 = ["a"]
        self.assertEquals(self.obj.prop1, ["a"])
        self.obj.prop1.append("b")
        self.assertEquals(self.obj.prop1, ["a", "b"])

    def test_list_events(self):
        self.setup(List, default_factory=list, allow_none=False)

        changes = []
        def changed(owner, variable, old_value, new_value, fromdb):
            changes.append((variable, old_value, new_value, fromdb))

        self.obj_info.checkpoint()
        self.obj_info.event.emit("start-tracking-changes", self.obj_info.event)
        self.obj_info.event.hook("changed", changed)

        self.assertEquals(self.obj.prop1, [])
        self.assertEquals(changes, [])
        self.obj.prop1.append("a")
        self.assertEquals(changes, [])

        # Check "flush" event. Notice that the other variable wasn't
        # listed, since it wasn't changed.
        self.obj_info.event.emit("flush")
        self.assertEquals(changes, [(self.variable1, None, ["a"], False)])

        del changes[:]

        # Check "object-deleted" event. Notice that the other variable
        # wasn't listed again, since it wasn't changed.
        del self.obj
        self.assertEquals(changes, [(self.variable1, None, ["a"], False)])

    def test_variable_factory_arguments(self):
        class Class(object):
            __storm_table__ = "test"
            id = Int(primary=True)

        validator_args = []
        def validator(obj, attr, value):
            validator_args[:] = obj, attr, value
            return value

        for func, cls, value in [
                               (Bool, BoolVariable, True),
                               (Int, IntVariable, 1),
                               (Float, FloatVariable, 1.1),
                               (RawStr, RawStrVariable, "str"),
                               (Unicode, UnicodeVariable, u"unicode"),
                               (DateTime, DateTimeVariable, datetime.now()),
                               (Date, DateVariable, date.today()),
                               (Time, TimeVariable, datetime.now().time()),
                               (Pickle, PickleVariable, {}),
                                     ]:

            # Test no default and allow_none=True.
            Class.prop = func(name="name")
            column = Class.prop.__get__(None, Class)
            self.assertEquals(column.name, "name")
            self.assertEquals(column.table, Class)

            variable = column.variable_factory()
            self.assertTrue(isinstance(variable, cls))
            self.assertEquals(variable.get(), None)
            variable.set(None)
            self.assertEquals(variable.get(), None)

            # Test default and allow_none=False.
            Class.prop = func(name="name", default=value, allow_none=False)
            column = Class.prop.__get__(None, Class)
            self.assertEquals(column.name, "name")
            self.assertEquals(column.table, Class)

            variable = column.variable_factory()
            self.assertTrue(isinstance(variable, cls))
            self.assertRaises(NoneError, variable.set, None)
            self.assertEquals(variable.get(), value)

            # Test default_factory.
            Class.prop = func(name="name", default_factory=lambda:value)
            column = Class.prop.__get__(None, Class)
            self.assertEquals(column.name, "name")
            self.assertEquals(column.table, Class)

            variable = column.variable_factory()
            self.assertTrue(isinstance(variable, cls))
            self.assertEquals(variable.get(), value)

            # Test validator.
            Class.prop = func(name="name", validator=validator, default=value)
            column = Class.prop.__get__(None, Class)
            self.assertEquals(column.name, "name")
            self.assertEquals(column.table, Class)

            del validator_args[:]
            variable = column.variable_factory()
            self.assertTrue(isinstance(variable, cls))
            # Validator is not called on instantiation.
            self.assertEquals(validator_args, [])
            # But is when setting the variable.
            variable.set(value)
            self.assertEquals(validator_args, [None, "prop", value])


class PropertyRegistryTest(TestHelper):

    def setUp(self):
        TestHelper.setUp(self)

        class Class(object):
            __storm_table__ = "mytable"
            prop1 = Property("column1", primary=True)
            prop2 = Property()

        class SubClass(Class):
            __storm_table__ = "mysubtable"

        self.Class = Class
        self.SubClass = SubClass
        self.AnotherClass = type("Class", (Class,), {})

        self.registry = PropertyRegistry()

    def test_get_empty(self):
        self.assertRaises(PropertyPathError, self.registry.get, "unexistent")

    def test_get(self):
        self.registry.add_class(self.Class)
        prop1 = self.registry.get("prop1")
        prop2 = self.registry.get("prop2")
        self.assertTrue(prop1 is self.Class.prop1)
        self.assertTrue(prop2 is self.Class.prop2)

    def test_get_with_class_name(self):
        self.registry.add_class(self.Class)
        prop1 = self.registry.get("Class.prop1")
        prop2 = self.registry.get("Class.prop2")
        self.assertTrue(prop1 is self.Class.prop1)
        self.assertTrue(prop2 is self.Class.prop2)

    def test_get_with_two_classes(self):
        self.registry.add_class(self.Class)
        self.registry.add_class(self.SubClass)
        prop1 = self.registry.get("Class.prop1")
        prop2 = self.registry.get("Class.prop2")
        self.assertTrue(prop1 is self.Class.prop1)
        self.assertTrue(prop2 is self.Class.prop2)
        prop1 = self.registry.get("SubClass.prop1")
        prop2 = self.registry.get("SubClass.prop2")
        self.assertTrue(prop1 is self.SubClass.prop1)
        self.assertTrue(prop2 is self.SubClass.prop2)

    def test_get_ambiguous(self):
        self.AnotherClass.__module__ += ".foo"
        self.registry.add_class(self.Class)
        self.registry.add_class(self.SubClass)
        self.registry.add_class(self.AnotherClass)
        self.assertRaises(PropertyPathError, self.registry.get, "Class.prop1")
        self.assertRaises(PropertyPathError, self.registry.get, "Class.prop2")
        prop1 = self.registry.get("SubClass.prop1")
        prop2 = self.registry.get("SubClass.prop2")
        self.assertTrue(prop1 is self.SubClass.prop1)
        self.assertTrue(prop2 is self.SubClass.prop2)

    def test_get_ambiguous_but_different_path(self):
        self.AnotherClass.__module__ += ".foo"
        self.registry.add_class(self.Class)
        self.registry.add_class(self.SubClass)
        self.registry.add_class(self.AnotherClass)
        prop1 = self.registry.get("properties.Class.prop1")
        prop2 = self.registry.get("properties.Class.prop2")
        self.assertTrue(prop1 is self.Class.prop1)
        self.assertTrue(prop2 is self.Class.prop2)
        prop1 = self.registry.get("SubClass.prop1")
        prop2 = self.registry.get("SubClass.prop2")
        self.assertTrue(prop1 is self.SubClass.prop1)
        self.assertTrue(prop2 is self.SubClass.prop2)
        prop1 = self.registry.get("foo.Class.prop1")
        prop2 = self.registry.get("foo.Class.prop2")
        self.assertTrue(prop1 is self.AnotherClass.prop1)
        self.assertTrue(prop2 is self.AnotherClass.prop2)

    def test_get_ambiguous_but_different_path_with_namespace(self):
        self.AnotherClass.__module__ += ".foo"
        self.registry.add_class(self.Class)
        self.registry.add_class(self.SubClass)
        self.registry.add_class(self.AnotherClass)
        prop1 = self.registry.get("Class.prop1", "tests.properties")
        prop2 = self.registry.get("Class.prop2", "tests.properties.bar")
        self.assertTrue(prop1 is self.Class.prop1)
        self.assertTrue(prop2 is self.Class.prop2)
        prop1 = self.registry.get("Class.prop1", "tests.properties.foo")
        prop2 = self.registry.get("Class.prop2", "tests.properties.foo.bar")
        self.assertTrue(prop1 is self.AnotherClass.prop1)
        self.assertTrue(prop2 is self.AnotherClass.prop2)

    def test_class_is_collectable(self):
        self.AnotherClass.__module__ += ".foo"
        self.registry.add_class(self.Class)
        self.registry.add_class(self.AnotherClass)
        del self.AnotherClass
        gc.collect()
        prop1 = self.registry.get("prop1")
        prop2 = self.registry.get("prop2")
        self.assertTrue(prop1 is self.Class.prop1)
        self.assertTrue(prop2 is self.Class.prop2)

    def test_add_property(self):
        self.registry.add_property(self.Class, self.Class.prop1, "custom_name")
        prop1 = self.registry.get("Class.custom_name")
        self.assertEquals(prop1, self.Class.prop1)
        self.assertRaises(PropertyPathError, self.registry.get, "Class.prop1")


class PropertyPublisherMetaTest(TestHelper):

    def setUp(self):
        TestHelper.setUp(self)

        class Base(object):
            __metaclass__ = PropertyPublisherMeta

        class Class(Base):
            __storm_table__ = "mytable"
            prop1 = Property("column1", primary=True)
            prop2 = Property()

        class SubClass(Class):
            __storm_table__ = "mysubtable"

        self.Class = Class
        self.SubClass = SubClass

        class Class(Class):
            __module__ += ".foo"
            prop3 = Property("column3")

        self.AnotherClass = Class

        self.registry = Base._storm_property_registry

    def test_get_empty(self):
        self.assertRaises(PropertyPathError, self.registry.get, "unexistent")

    def test_get_subclass(self):
        prop1 = self.registry.get("SubClass.prop1")
        prop2 = self.registry.get("SubClass.prop2")
        self.assertTrue(prop1 is self.SubClass.prop1)
        self.assertTrue(prop2 is self.SubClass.prop2)

    def test_get_ambiguous(self):
        self.assertRaises(PropertyPathError, self.registry.get, "Class.prop1")
        self.assertRaises(PropertyPathError, self.registry.get, "Class.prop2")
