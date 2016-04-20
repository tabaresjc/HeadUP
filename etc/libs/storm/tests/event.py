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
from storm.event import EventSystem

from tests.helper import TestHelper


class Marker(object):
    pass

marker = Marker()


class EventTest(TestHelper):

    def setUp(self):
        TestHelper.setUp(self)
        self.event = EventSystem(marker)

    def test_hook_unhook_emit(self):
        called1 = []
        called2 = []
        def callback1(owner, arg1, arg2):
            called1.append((owner, arg1, arg2))
        def callback2(owner, arg1, arg2, data1, data2):
            called2.append((owner, arg1, arg2, data1, data2))

        self.event.hook("one", callback1)
        self.event.hook("one", callback1)
        self.event.hook("one", callback2, 10, 20)
        self.event.hook("two", callback2, 10, 20)
        self.event.hook("two", callback2, 10, 20)
        self.event.hook("two", callback2, 30, 40)
        self.event.hook("three", callback1)

        self.event.emit("one", 1, 2)
        self.event.emit("two", 3, 4)
        self.event.unhook("two", callback2, 10, 20)
        self.event.emit("two", 3, 4)
        self.event.emit("three", 5, 6)

        self.assertEquals(sorted(called1), [
                          (marker, 1, 2),
                          (marker, 5, 6),
                         ])
        self.assertEquals(sorted(called2), [
                          (marker, 1, 2, 10, 20),
                          (marker, 3, 4, 10, 20),
                          (marker, 3, 4, 30, 40),
                          (marker, 3, 4, 30, 40),
                         ])

    def test_unhook_by_returning_false(self):
        called = []
        def callback(owner):
            called.append(owner)
            return len(called) < 2

        self.event.hook("event", callback)

        self.event.emit("event")
        self.event.emit("event")
        self.event.emit("event")
        self.event.emit("event")

        self.assertEquals(called, [marker, marker])

    def test_weak_reference(self):
        marker = Marker()

        called = []
        def callback(owner):
            called.append(owner)

        self.event = EventSystem(marker)

        self.event.hook("event", callback)
        self.event.emit("event")

        self.assertEquals(called, [marker])
        del called[:]

        del marker
        self.event.emit("event")
        self.assertEquals(called, [])
