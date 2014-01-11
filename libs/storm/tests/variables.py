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
from decimal import Decimal
import cPickle as pickle
import gc
import weakref
try:
    import uuid
except ImportError:
    uuid = None

from storm.compat import json
from storm.exceptions import NoneError
from storm.variables import *
from storm.event import EventSystem
from storm.expr import Column, SQLToken
from storm.tz import tzutc, tzoffset
from storm import Undef

from tests.helper import TestHelper


class Marker(object):
    pass

marker = Marker()


class CustomVariable(Variable):

    def __init__(self, *args, **kwargs):
        self.gets = []
        self.sets = []
        Variable.__init__(self, *args, **kwargs)

    def parse_get(self, variable, to_db):
        self.gets.append((variable, to_db))
        return "g", variable

    def parse_set(self, variable, from_db):
        self.sets.append((variable, from_db))
        return "s", variable


class VariableTest(TestHelper):

    def test_constructor_value(self):
        variable = CustomVariable(marker)
        self.assertEquals(variable.sets, [(marker, False)])

    def test_constructor_value_from_db(self):
        variable = CustomVariable(marker, from_db=True)
        self.assertEquals(variable.sets, [(marker, True)])

    def test_constructor_value_factory(self):
        variable = CustomVariable(value_factory=lambda:marker)
        self.assertEquals(variable.sets, [(marker, False)])

    def test_constructor_value_factory_from_db(self):
        variable = CustomVariable(value_factory=lambda:marker, from_db=True)
        self.assertEquals(variable.sets, [(marker, True)])

    def test_constructor_column(self):
        variable = CustomVariable(column=marker)
        self.assertEquals(variable.column, marker)

    def test_constructor_event(self):
        variable = CustomVariable(event=marker)
        self.assertEquals(variable.event, marker)

    def test_get_default(self):
        variable = CustomVariable()
        self.assertEquals(variable.get(default=marker), marker)

    def test_set(self):
        variable = CustomVariable()
        variable.set(marker)
        self.assertEquals(variable.sets, [(marker, False)])
        variable.set(marker, from_db=True)
        self.assertEquals(variable.sets, [(marker, False), (marker, True)])

    def test_set_leak(self):
        """When a variable is checkpointed, the value must not leak."""
        variable = Variable()
        m = Marker()
        m_ref = weakref.ref(m)
        variable.set(m)
        variable.checkpoint()
        variable.set(LazyValue())
        del m
        gc.collect()
        self.assertIdentical(m_ref(), None)

    def test_get(self):
        variable = CustomVariable()
        variable.set(marker)
        self.assertEquals(variable.get(), ("g", ("s", marker)))
        self.assertEquals(variable.gets, [(("s", marker), False)])

        variable = CustomVariable()
        variable.set(marker)
        self.assertEquals(variable.get(to_db=True), ("g", ("s", marker)))
        self.assertEquals(variable.gets, [(("s", marker), True)])

    def test_is_defined(self):
        variable = CustomVariable()
        self.assertFalse(variable.is_defined())
        variable.set(marker)
        self.assertTrue(variable.is_defined())

    def test_set_get_none(self):
        variable = CustomVariable()
        variable.set(None)
        self.assertEquals(variable.get(marker), None)
        self.assertEquals(variable.sets, [])
        self.assertEquals(variable.gets, [])

    def test_set_none_with_allow_none(self):
        variable = CustomVariable(allow_none=False)
        self.assertRaises(NoneError, variable.set, None)

    def test_set_none_with_allow_none_and_column(self):
        column = Column("column_name")
        variable = CustomVariable(allow_none=False, column=column)
        try:
            variable.set(None)
        except NoneError, e:
            pass
        self.assertTrue("column_name" in str(e))

    def test_set_none_with_allow_none_and_column_with_table(self):
        column = Column("column_name", SQLToken("table_name"))
        variable = CustomVariable(allow_none=False, column=column)
        try:
            variable.set(None)
        except NoneError, e:
            pass
        self.assertTrue("table_name.column_name" in str(e))

    def test_set_with_validator(self):
        args = []
        def validator(obj, attr, value):
            args.append((obj, attr, value))
            return value
        variable = CustomVariable(validator=validator)
        variable.set(3)
        self.assertEquals(args, [(None, None, 3)])

    def test_set_with_validator_and_validator_arguments(self):
        args = []
        def validator(obj, attr, value):
            args.append((obj, attr, value))
            return value
        variable = CustomVariable(validator=validator,
                                  validator_object_factory=lambda: 1,
                                  validator_attribute=2)
        variable.set(3)
        self.assertEquals(args, [(1, 2, 3)])

    def test_set_with_validator_raising_error(self):
        args = []
        def validator(obj, attr, value):
            args.append((obj, attr, value))
            raise ZeroDivisionError()
        variable = CustomVariable(validator=validator)
        self.assertRaises(ZeroDivisionError, variable.set, marker)
        self.assertEquals(args, [(None, None, marker)])
        self.assertEquals(variable.get(), None)

    def test_set_with_validator_changing_value(self):
        args = []
        def validator(obj, attr, value):
            args.append((obj, attr, value))
            return 42
        variable = CustomVariable(validator=validator)
        variable.set(marker)
        self.assertEquals(args, [(None, None, marker)])
        self.assertEquals(variable.get(), ('g', ('s', 42)))

    def test_set_from_db_wont_call_validator(self):
        args = []
        def validator(obj, attr, value):
            args.append((obj, attr, value))
            return 42
        variable = CustomVariable(validator=validator)
        variable.set(marker, from_db=True)
        self.assertEquals(args, [])
        self.assertEquals(variable.get(), ('g', ('s', marker)))

    def test_event_changed(self):
        event = EventSystem(marker)

        changed_values = []
        def changed(owner, variable, old_value, new_value, fromdb):
            changed_values.append((owner, variable,
                                   old_value, new_value, fromdb))

        event.hook("changed", changed)

        variable = CustomVariable(event=event)
        variable.set("value1")
        variable.set("value2")
        variable.set("value3", from_db=True)
        variable.set(None, from_db=True)
        variable.set("value4")
        variable.delete()
        variable.delete()

        self.assertEquals(changed_values[0],
          (marker, variable, Undef, "value1", False))
        self.assertEquals(changed_values[1],
          (marker, variable, ("g", ("s", "value1")), "value2", False))
        self.assertEquals(changed_values[2],
          (marker, variable, ("g", ("s", "value2")), ("g", ("s", "value3")),
           True))
        self.assertEquals(changed_values[3],
          (marker, variable, ("g", ("s", "value3")), None, True))
        self.assertEquals(changed_values[4],
          (marker, variable, None, "value4", False))
        self.assertEquals(changed_values[5],
          (marker, variable, ("g", ("s", "value4")), Undef, False))
        self.assertEquals(len(changed_values), 6)

    def test_get_state(self):
        variable = CustomVariable(marker)
        self.assertEquals(variable.get_state(), (Undef, ("s", marker)))

    def test_set_state(self):
        lazy_value = object()
        variable = CustomVariable()
        variable.set_state((lazy_value, marker))
        self.assertEquals(variable.get(), ("g", marker))
        self.assertEquals(variable.get_lazy(), lazy_value)

    def test_checkpoint_and_has_changed(self):
        variable = CustomVariable()
        self.assertTrue(variable.has_changed())
        variable.set(marker)
        self.assertTrue(variable.has_changed())
        variable.checkpoint()
        self.assertFalse(variable.has_changed())
        variable.set(marker)
        self.assertFalse(variable.has_changed())
        variable.set((marker, marker))
        self.assertTrue(variable.has_changed())
        variable.checkpoint()
        self.assertFalse(variable.has_changed())
        variable.set((marker, marker))
        self.assertFalse(variable.has_changed())
        variable.set(marker)
        self.assertTrue(variable.has_changed())
        variable.set((marker, marker))
        self.assertFalse(variable.has_changed())

    def test_copy(self):
        variable = CustomVariable()
        variable.set(marker)
        variable_copy = variable.copy()
        variable_copy.gets = []
        self.assertTrue(variable is not variable_copy)
        self.assertVariablesEqual([variable], [variable_copy])

    def test_lazy_value_setting(self):
        variable = CustomVariable()
        variable.set(LazyValue())
        self.assertEquals(variable.sets, [])
        self.assertTrue(variable.has_changed())

    def test_lazy_value_getting(self):
        variable = CustomVariable()
        variable.set(LazyValue())
        self.assertEquals(variable.get(marker), marker)
        variable.set(1)
        variable.set(LazyValue())
        self.assertEquals(variable.get(marker), marker)
        self.assertFalse(variable.is_defined())

    def test_lazy_value_resolving(self):
        event = EventSystem(marker)

        resolve_values = []
        def resolve(owner, variable, value):
            resolve_values.append((owner, variable, value))



        lazy_value = LazyValue()
        variable = CustomVariable(lazy_value, event=event)

        event.hook("resolve-lazy-value", resolve)

        variable.get()

        self.assertEquals(resolve_values,
                          [(marker, variable, lazy_value)])

    def test_lazy_value_changed_event(self):
        event = EventSystem(marker)

        changed_values = []
        def changed(owner, variable, old_value, new_value, fromdb):
            changed_values.append((owner, variable,
                                   old_value, new_value, fromdb))

        event.hook("changed", changed)

        variable = CustomVariable(event=event)

        lazy_value = LazyValue()

        variable.set(lazy_value)

        self.assertEquals(changed_values,
                          [(marker, variable, Undef, lazy_value, False)])

    def test_lazy_value_setting_on_resolving(self):
        event = EventSystem(marker)

        def resolve(owner, variable, value):
            variable.set(marker)

        event.hook("resolve-lazy-value", resolve)

        lazy_value = LazyValue()
        variable = CustomVariable(lazy_value, event=event)

        self.assertEquals(variable.get(), ("g", ("s", marker)))

    def test_lazy_value_reset_after_changed(self):
        event = EventSystem(marker)

        resolve_called = []
        def resolve(owner, variable, value):
            resolve_called.append(True)

        event.hook("resolve-lazy-value", resolve)

        variable = CustomVariable(event=event)

        variable.set(LazyValue())
        variable.set(1)
        self.assertEquals(variable.get(), ("g", ("s", 1)))
        self.assertEquals(resolve_called, [])

    def test_get_lazy_value(self):
        lazy_value = LazyValue()
        variable = CustomVariable()
        self.assertEquals(variable.get_lazy(), None)
        self.assertEquals(variable.get_lazy(marker), marker)
        variable.set(lazy_value)
        self.assertEquals(variable.get_lazy(marker), lazy_value)


class BoolVariableTest(TestHelper):

    def test_set_get(self):
        variable = BoolVariable()
        variable.set(1)
        self.assertTrue(variable.get() is True)
        variable.set(0)
        self.assertTrue(variable.get() is False)
        variable.set(1.1)
        self.assertTrue(variable.get() is True)
        variable.set(0.0)
        self.assertTrue(variable.get() is False)
        variable.set(Decimal(1))
        self.assertTrue(variable.get() is True)
        variable.set(Decimal(0))
        self.assertTrue(variable.get() is False)
        self.assertRaises(TypeError, variable.set, "string")


class IntVariableTest(TestHelper):

    def test_set_get(self):
        variable = IntVariable()
        variable.set(1)
        self.assertEquals(variable.get(), 1)
        variable.set(1.1)
        self.assertEquals(variable.get(), 1)
        variable.set(Decimal(2))
        self.assertEquals(variable.get(), 2)
        self.assertRaises(TypeError, variable.set, "1")


class FloatVariableTest(TestHelper):

    def test_set_get(self):
        variable = FloatVariable()
        variable.set(1.1)
        self.assertEquals(variable.get(), 1.1)
        variable.set(1)
        self.assertEquals(variable.get(), 1)
        self.assertEquals(type(variable.get()), float)
        variable.set(Decimal("1.1"))
        self.assertEquals(variable.get(), 1.1)
        self.assertRaises(TypeError, variable.set, "1")


class DecimalVariableTest(TestHelper):

    def test_set_get(self):
        variable = DecimalVariable()
        variable.set(Decimal("1.1"))
        self.assertEquals(variable.get(), Decimal("1.1"))
        variable.set(1)
        self.assertEquals(variable.get(), 1)
        self.assertEquals(type(variable.get()), Decimal)
        variable.set(Decimal("1.1"))
        self.assertEquals(variable.get(), Decimal("1.1"))
        self.assertRaises(TypeError, variable.set, "1")
        self.assertRaises(TypeError, variable.set, 1.1)

    def test_get_set_from_database(self):
        """Strings used to/from the database."""
        variable = DecimalVariable()
        variable.set("1.1", from_db=True)
        self.assertEquals(variable.get(), Decimal("1.1"))
        self.assertEquals(variable.get(to_db=True), "1.1")


class RawStrVariableTest(TestHelper):

    def test_set_get(self):
        variable = RawStrVariable()
        variable.set("str")
        self.assertEquals(variable.get(), "str")
        variable.set(buffer("buffer"))
        self.assertEquals(variable.get(), "buffer")
        self.assertRaises(TypeError, variable.set, u"unicode")


class UnicodeVariableTest(TestHelper):

    def test_set_get(self):
        variable = UnicodeVariable()
        variable.set(u"unicode")
        self.assertEquals(variable.get(), u"unicode")
        self.assertRaises(TypeError, variable.set, "str")


class DateTimeVariableTest(TestHelper):

    def test_get_set(self):
        epoch = datetime.utcfromtimestamp(0)
        variable = DateTimeVariable()
        variable.set(0)
        self.assertEquals(variable.get(), epoch)
        variable.set(0.0)
        self.assertEquals(variable.get(), epoch)
        variable.set(0L)
        self.assertEquals(variable.get(), epoch)
        variable.set(epoch)
        self.assertEquals(variable.get(), epoch)
        self.assertRaises(TypeError, variable.set, marker)

    def test_get_set_from_database(self):
        datetime_str = "1977-05-04 12:34:56.78"
        datetime_uni = unicode(datetime_str)
        datetime_obj = datetime(1977, 5, 4, 12, 34, 56, 780000)

        variable = DateTimeVariable()

        variable.set(datetime_str, from_db=True)
        self.assertEquals(variable.get(), datetime_obj)
        variable.set(datetime_uni, from_db=True)
        self.assertEquals(variable.get(), datetime_obj)
        variable.set(datetime_obj, from_db=True)
        self.assertEquals(variable.get(), datetime_obj)

        datetime_str = "1977-05-04 12:34:56"
        datetime_uni = unicode(datetime_str)
        datetime_obj = datetime(1977, 5, 4, 12, 34, 56)

        variable.set(datetime_str, from_db=True)
        self.assertEquals(variable.get(), datetime_obj)
        variable.set(datetime_uni, from_db=True)
        self.assertEquals(variable.get(), datetime_obj)
        variable.set(datetime_obj, from_db=True)
        self.assertEquals(variable.get(), datetime_obj)

        self.assertRaises(TypeError, variable.set, 0, from_db=True)
        self.assertRaises(TypeError, variable.set, marker, from_db=True)
        self.assertRaises(ValueError, variable.set, "foobar", from_db=True)
        self.assertRaises(ValueError, variable.set, "foo bar", from_db=True)

    def test_get_set_with_tzinfo(self):
        datetime_str = "1977-05-04 12:34:56.78"
        datetime_obj = datetime(1977, 5, 4, 12, 34, 56, 780000, tzinfo=tzutc())

        variable = DateTimeVariable(tzinfo=tzutc())

        # Naive timezone, from_db=True.
        variable.set(datetime_str, from_db=True)
        self.assertEquals(variable.get(), datetime_obj)
        variable.set(datetime_obj, from_db=True)
        self.assertEquals(variable.get(), datetime_obj)

        # Naive timezone, from_db=False (doesn't work).
        datetime_obj = datetime(1977, 5, 4, 12, 34, 56, 780000)
        self.assertRaises(ValueError, variable.set, datetime_obj)

        # Different timezone, from_db=False.
        datetime_obj = datetime(1977, 5, 4, 12, 34, 56, 780000,
                                tzinfo=tzoffset("1h", 3600))
        variable.set(datetime_obj, from_db=False)
        converted_obj = variable.get()
        self.assertEquals(converted_obj, datetime_obj)
        self.assertEquals(type(converted_obj.tzinfo), tzutc)

        # Different timezone, from_db=True.
        datetime_obj = datetime(1977, 5, 4, 12, 34, 56, 780000,
                                tzinfo=tzoffset("1h", 3600))
        variable.set(datetime_obj, from_db=True)
        converted_obj = variable.get()
        self.assertEquals(converted_obj, datetime_obj)
        self.assertEquals(type(converted_obj.tzinfo), tzutc)


class DateVariableTest(TestHelper):

    def test_get_set(self):
        epoch = datetime.utcfromtimestamp(0)
        epoch_date = epoch.date()

        variable = DateVariable()

        variable.set(epoch)
        self.assertEquals(variable.get(), epoch_date)
        variable.set(epoch_date)
        self.assertEquals(variable.get(), epoch_date)

        self.assertRaises(TypeError, variable.set, marker)

    def test_get_set_from_database(self):
        date_str = "1977-05-04"
        date_uni = unicode(date_str)
        date_obj = date(1977, 5, 4)
        datetime_obj = datetime(1977, 5, 4, 0, 0, 0)

        variable = DateVariable()

        variable.set(date_str, from_db=True)
        self.assertEquals(variable.get(), date_obj)
        variable.set(date_uni, from_db=True)
        self.assertEquals(variable.get(), date_obj)
        variable.set(date_obj, from_db=True)
        self.assertEquals(variable.get(), date_obj)
        variable.set(datetime_obj, from_db=True)
        self.assertEquals(variable.get(), date_obj)

        self.assertRaises(TypeError, variable.set, 0, from_db=True)
        self.assertRaises(TypeError, variable.set, marker, from_db=True)
        self.assertRaises(ValueError, variable.set, "foobar", from_db=True)

    def test_set_with_datetime(self):
        datetime_str = "1977-05-04 12:34:56.78"
        date_obj = date(1977, 5, 4)
        variable = DateVariable()
        variable.set(datetime_str, from_db=True)
        self.assertEquals(variable.get(), date_obj)


class TimeVariableTest(TestHelper):

    def test_get_set(self):
        epoch = datetime.utcfromtimestamp(0)
        epoch_time = epoch.time()

        variable = TimeVariable()

        variable.set(epoch)
        self.assertEquals(variable.get(), epoch_time)
        variable.set(epoch_time)
        self.assertEquals(variable.get(), epoch_time)

        self.assertRaises(TypeError, variable.set, marker)

    def test_get_set_from_database(self):
        time_str = "12:34:56.78"
        time_uni = unicode(time_str)
        time_obj = time(12, 34, 56, 780000)

        variable = TimeVariable()

        variable.set(time_str, from_db=True)
        self.assertEquals(variable.get(), time_obj)
        variable.set(time_uni, from_db=True)
        self.assertEquals(variable.get(), time_obj)
        variable.set(time_obj, from_db=True)
        self.assertEquals(variable.get(), time_obj)

        time_str = "12:34:56"
        time_uni = unicode(time_str)
        time_obj = time(12, 34, 56)

        variable.set(time_str, from_db=True)
        self.assertEquals(variable.get(), time_obj)
        variable.set(time_uni, from_db=True)
        self.assertEquals(variable.get(), time_obj)
        variable.set(time_obj, from_db=True)
        self.assertEquals(variable.get(), time_obj)

        self.assertRaises(TypeError, variable.set, 0, from_db=True)
        self.assertRaises(TypeError, variable.set, marker, from_db=True)
        self.assertRaises(ValueError, variable.set, "foobar", from_db=True)

    def test_set_with_datetime(self):
        datetime_str = "1977-05-04 12:34:56.78"
        time_obj = time(12, 34, 56, 780000)
        variable = TimeVariable()
        variable.set(datetime_str, from_db=True)
        self.assertEquals(variable.get(), time_obj)

    def test_microsecond_error(self):
        time_str = "15:14:18.598678"
        time_obj = time(15, 14, 18, 598678)
        variable = TimeVariable()
        variable.set(time_str, from_db=True)
        self.assertEquals(variable.get(), time_obj)

    def test_microsecond_error_less_digits(self):
        time_str = "15:14:18.5986"
        time_obj = time(15, 14, 18, 598600)
        variable = TimeVariable()
        variable.set(time_str, from_db=True)
        self.assertEquals(variable.get(), time_obj)

    def test_microsecond_error_more_digits(self):
        time_str = "15:14:18.5986789"
        time_obj = time(15, 14, 18, 598678)
        variable = TimeVariable()
        variable.set(time_str, from_db=True)
        self.assertEquals(variable.get(), time_obj)


class TimeDeltaVariableTest(TestHelper):

    def test_get_set(self):
        delta = timedelta(days=42)

        variable = TimeDeltaVariable()

        variable.set(delta)
        self.assertEquals(variable.get(), delta)

        self.assertRaises(TypeError, variable.set, marker)

    def test_get_set_from_database(self):
        delta_str = "42 days 12:34:56.78"
        delta_uni = unicode(delta_str)
        delta_obj = timedelta(days=42, hours=12, minutes=34,
                              seconds=56, microseconds=780000)

        variable = TimeDeltaVariable()

        variable.set(delta_str, from_db=True)
        self.assertEquals(variable.get(), delta_obj)
        variable.set(delta_uni, from_db=True)
        self.assertEquals(variable.get(), delta_obj)
        variable.set(delta_obj, from_db=True)
        self.assertEquals(variable.get(), delta_obj)

        delta_str = "1 day, 12:34:56"
        delta_uni = unicode(delta_str)
        delta_obj = timedelta(days=1, hours=12, minutes=34, seconds=56)

        variable.set(delta_str, from_db=True)
        self.assertEquals(variable.get(), delta_obj)
        variable.set(delta_uni, from_db=True)
        self.assertEquals(variable.get(), delta_obj)
        variable.set(delta_obj, from_db=True)
        self.assertEquals(variable.get(), delta_obj)

        self.assertRaises(TypeError, variable.set, 0, from_db=True)
        self.assertRaises(TypeError, variable.set, marker, from_db=True)
        self.assertRaises(ValueError, variable.set, "foobar", from_db=True)

        # Intervals of months or years can not be converted to a
        # Python timedelta, so a ValueError exception is raised:
        self.assertRaises(ValueError, variable.set, "42 months", from_db=True)
        self.assertRaises(ValueError, variable.set, "42 years", from_db=True)


class ParseIntervalTest(TestHelper):

    def check(self, interval, td):
        self.assertEquals(TimeDeltaVariable(interval, from_db=True).get(), td)

    def test_zero(self):
        self.check("0:00:00", timedelta(0))

    def test_one_microsecond(self):
        self.check("0:00:00.000001", timedelta(0, 0, 1))

    def test_twelve_centiseconds(self):
        self.check("0:00:00.120000", timedelta(0, 0, 120000))

    def test_one_second(self):
        self.check("0:00:01", timedelta(0, 1))

    def test_twelve_seconds(self):
        self.check("0:00:12", timedelta(0, 12))

    def test_one_minute(self):
        self.check("0:01:00", timedelta(0, 60))

    def test_twelve_minutes(self):
        self.check("0:12:00", timedelta(0, 12*60))

    def test_one_hour(self):
        self.check("1:00:00", timedelta(0, 60*60))

    def test_twelve_hours(self):
        self.check("12:00:00", timedelta(0, 12*60*60))

    def test_one_day(self):
        self.check("1 day, 0:00:00", timedelta(1))

    def test_twelve_days(self):
        self.check("12 days, 0:00:00", timedelta(12))

    def test_twelve_twelve_twelve_twelve_twelve(self):
        self.check("12 days, 12:12:12.120000",
                   timedelta(12, 12*60*60 + 12*60 + 12, 120000))

    def test_minus_twelve_centiseconds(self):
        self.check("-1 day, 23:59:59.880000", timedelta(0, 0, -120000))

    def test_minus_twelve_days(self):
        self.check("-12 days, 0:00:00", timedelta(-12))

    def test_minus_twelve_hours(self):
        self.check("-12:00:00", timedelta(hours=-12))

    def test_one_day_and_a_half(self):
        self.check("1.5 days", timedelta(days=1, hours=12))

    def test_seconds_without_unit(self):
        self.check("1h123", timedelta(hours=1, seconds=123))

    def test_d_h_m_s_ms(self):
        self.check("1d1h1m1s1ms", timedelta(days=1, hours=1, minutes=1,
                                            seconds=1, microseconds=1000))

    def test_days_without_unit(self):
        self.check("-12 1:02 3s", timedelta(days=-12, hours=1, minutes=2,
                                            seconds=3))

    def test_unsupported_unit(self):
        try:
            self.check("1 month", None)
        except ValueError, e:
            self.assertEquals(str(e), "Unsupported interval unit 'month' "
                                      "in interval '1 month'")
        else:
            self.fail("ValueError not raised")

    def test_missing_value(self):
        try:
            self.check("day", None)
        except ValueError, e:
            self.assertEquals(str(e), "Expected an interval value rather than "
                                      "'day' in interval 'day'")
        else:
            self.fail("ValueError not raised")


class UUIDVariableTest(TestHelper):

    def is_supported(self):
        return uuid is not None

    def test_get_set(self):
        value = uuid.UUID("{0609f76b-878f-4546-baf5-c1b135e8de72}")

        variable = UUIDVariable()

        variable.set(value)
        self.assertEquals(variable.get(), value)
        self.assertEquals(
            variable.get(to_db=True), "0609f76b-878f-4546-baf5-c1b135e8de72")

        self.assertRaises(TypeError, variable.set, marker)
        self.assertRaises(TypeError, variable.set,
                          "0609f76b-878f-4546-baf5-c1b135e8de72")
        self.assertRaises(TypeError, variable.set,
                          u"0609f76b-878f-4546-baf5-c1b135e8de72")

    def test_get_set_from_database(self):
        value = uuid.UUID("{0609f76b-878f-4546-baf5-c1b135e8de72}")

        variable = UUIDVariable()

        # Strings and UUID objects are accepted from the database.
        variable.set(value, from_db=True)
        self.assertEquals(variable.get(), value)
        variable.set("0609f76b-878f-4546-baf5-c1b135e8de72", from_db=True)
        self.assertEquals(variable.get(), value)
        variable.set(u"0609f76b-878f-4546-baf5-c1b135e8de72", from_db=True)
        self.assertEquals(variable.get(), value)

        # Some other representations for UUID values.
        variable.set("{0609f76b-878f-4546-baf5-c1b135e8de72}", from_db=True)
        self.assertEquals(variable.get(), value)
        variable.set("0609f76b878f4546baf5c1b135e8de72", from_db=True)
        self.assertEquals(variable.get(), value)


class EncodedValueVariableTestMixin(object):

    encoding = None
    variable_type = None

    def test_get_set(self):
        d = {"a": 1}
        d_dump = self.encode(d)

        variable = self.variable_type()

        variable.set(d)
        self.assertEquals(variable.get(), d)
        self.assertEquals(variable.get(to_db=True), d_dump)

        variable.set(d_dump, from_db=True)
        self.assertEquals(variable.get(), d)
        self.assertEquals(variable.get(to_db=True), d_dump)

        self.assertEquals(variable.get_state(), (Undef, d_dump))

        variable.set(marker)
        variable.set_state((Undef, d_dump))
        self.assertEquals(variable.get(), d)

        variable.get()["b"] = 2
        self.assertEquals(variable.get(), {"a": 1, "b": 2})

    def test_pickle_events(self):
        event = EventSystem(marker)

        variable = self.variable_type(event=event, value_factory=list)

        changes = []
        def changed(owner, variable, old_value, new_value, fromdb):
            changes.append((variable, old_value, new_value, fromdb))

        event.emit("start-tracking-changes", event)
        event.hook("changed", changed)

        variable.checkpoint()

        event.emit("flush")

        self.assertEquals(changes, [])

        lst = variable.get()

        self.assertEquals(lst, [])
        self.assertEquals(changes, [])

        lst.append("a")

        self.assertEquals(changes, [])

        event.emit("flush")

        self.assertEquals(changes, [(variable, None, ["a"], False)])

        del changes[:]

        event.emit("object-deleted")
        self.assertEquals(changes, [(variable, None, ["a"], False)])


class PickleVariableTest(EncodedValueVariableTestMixin, TestHelper):

    encode = staticmethod(lambda data: pickle.dumps(data, -1))
    variable_type = PickleVariable


class JSONVariableTest(EncodedValueVariableTestMixin, TestHelper):

    encode = staticmethod(lambda data: json.dumps(data).decode("utf-8"))
    variable_type = JSONVariable

    def is_supported(self):
        return json is not None

    def test_unicode_from_db_required(self):
        # JSONVariable._loads() complains loudly if it does not receive a
        # unicode string because it has no way of knowing its encoding.
        variable = self.variable_type()
        self.assertRaises(TypeError, variable.set, '"abc"', from_db=True)

    def test_unicode_to_db(self):
        # JSONVariable._dumps() works around unicode/str handling issues in
        # simplejson/json.
        variable = self.variable_type()
        variable.set({u"a": 1})
        self.assertTrue(isinstance(variable.get(to_db=True), unicode))


class ListVariableTest(TestHelper):

    def test_get_set(self):
        # Enumeration variables are used as items so that database
        # side and python side values can be distinguished.
        get_map = {1: "a", 2: "b", 3: "c"}
        set_map = {"a": 1, "b": 2, "c": 3}
        item_factory = VariableFactory(
            EnumVariable, get_map=get_map, set_map=set_map)

        l = ["a", "b"]
        l_dump = pickle.dumps(l, -1)
        l_vars = [item_factory(value=x) for x in l]

        variable = ListVariable(item_factory)

        variable.set(l)
        self.assertEquals(variable.get(), l)
        self.assertVariablesEqual(variable.get(to_db=True), l_vars)

        variable.set([1, 2], from_db=True)
        self.assertEquals(variable.get(), l)
        self.assertVariablesEqual(variable.get(to_db=True), l_vars)

        self.assertEquals(variable.get_state(), (Undef, l_dump))

        variable.set([])
        variable.set_state((Undef, l_dump))
        self.assertEquals(variable.get(), l)

        variable.get().append("c")
        self.assertEquals(variable.get(), ["a", "b", "c"])

    def test_list_events(self):
        event = EventSystem(marker)

        variable = ListVariable(RawStrVariable, event=event,
                                value_factory=list)

        changes = []
        def changed(owner, variable, old_value, new_value, fromdb):
            changes.append((variable, old_value, new_value, fromdb))

        event.emit("start-tracking-changes", event)
        event.hook("changed", changed)

        variable.checkpoint()

        event.emit("flush")

        self.assertEquals(changes, [])

        lst = variable.get()

        self.assertEquals(lst, [])
        self.assertEquals(changes, [])

        lst.append("a")

        self.assertEquals(changes, [])

        event.emit("flush")

        self.assertEquals(changes, [(variable, None, ["a"], False)])

        del changes[:]

        event.emit("object-deleted")
        self.assertEquals(changes, [(variable, None, ["a"], False)])


class EnumVariableTest(TestHelper):

    def test_set_get(self):
        variable = EnumVariable({1: "foo", 2: "bar"}, {"foo": 1, "bar": 2})
        variable.set("foo")
        self.assertEquals(variable.get(), "foo")
        self.assertEquals(variable.get(to_db=True), 1)
        variable.set(2, from_db=True)
        self.assertEquals(variable.get(), "bar")
        self.assertEquals(variable.get(to_db=True), 2)
        self.assertRaises(ValueError, variable.set, "foobar")
        self.assertRaises(ValueError, variable.set, 2)

    def test_in_map(self):
        variable = EnumVariable({1: "foo", 2: "bar"}, {"one": 1, "two": 2})
        variable.set("one")
        self.assertEquals(variable.get(), "foo")
        self.assertEquals(variable.get(to_db=True), 1)
        variable.set(2, from_db=True)
        self.assertEquals(variable.get(), "bar")
        self.assertEquals(variable.get(to_db=True), 2)
        self.assertRaises(ValueError, variable.set, "foo")
        self.assertRaises(ValueError, variable.set, 2)
