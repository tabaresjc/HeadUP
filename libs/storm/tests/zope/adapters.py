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
from tests.helper import TestHelper
from tests.zope import has_zope_component


if has_zope_component:
    from zope.interface import implements
    from zope.component import getGlobalSiteManager

    from storm.store import EmptyResultSet
    from storm.zope.adapters import sqlobject_result_set_to_storm_result_set
    from storm.zope.interfaces import IResultSet, ISQLObjectResultSet

    class TestSQLObjectResultSet(object):
        implements(ISQLObjectResultSet)
        _result_set = EmptyResultSet()


class AdaptersTest(TestHelper):

    def is_supported(self):
        return has_zope_component

    def setUp(self):
        getGlobalSiteManager().registerAdapter(
            sqlobject_result_set_to_storm_result_set)

    def tearDown(self):
        getGlobalSiteManager().unregisterAdapter(
            sqlobject_result_set_to_storm_result_set)

    def test_adapt_sqlobject_to_storm(self):
        so_result_set = TestSQLObjectResultSet()
        self.assertTrue(
            ISQLObjectResultSet.providedBy(so_result_set))
        result_set = IResultSet(so_result_set)
        self.assertTrue(
            IResultSet.providedBy(result_set))
