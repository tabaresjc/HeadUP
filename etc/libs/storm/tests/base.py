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
import weakref
import gc

from storm.properties import Property, PropertyPublisherMeta
from storm.info import get_obj_info
from storm.base import *

from tests.helper import TestHelper


class BaseTest(TestHelper):

    def test_metaclass(self):
        class Class(Storm):
            __storm_table__ = "table_name"
            prop = Property(primary=True)
        self.assertEquals(type(Class), PropertyPublisherMeta)

    def test_class_is_collectable(self):
        class Class(Storm):
            __storm_table__ = "table_name"
            prop = Property(primary=True)
        obj = Class()
        get_obj_info(obj) # Build all wanted meta-information.
        obj_ref = weakref.ref(obj)
        del obj
        gc.collect()
        self.assertEquals(obj_ref(), None)
