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

__all__ = [
    'has_transaction',
    'has_zope_component',
    'has_zope_security',
    'has_testresources',
    ]

try:
    import transaction
except ImportError:
    has_transaction = False
else:
    has_transaction = True

try:
    import zope.component
except ImportError:
    has_zope_component = False
else:
    has_zope_component = True

try:
    import zope.security
except ImportError:
    has_zope_security = False
else:
    has_zope_security = True

try:
    import testresources
except ImportError:
    has_testresources = False
else:
    has_testresources = True
