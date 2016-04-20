#
# Copyright (c) 2011 Canonical
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
    'find_tests',
    'has_fixtures',
    'has_psycopg',
    'has_subunit',
    ]

import doctest
import os
import unittest

try:
    import fixtures
    fixtures  # Silence lint.
except ImportError:
    has_fixtures = False
else:
    has_fixtures = True


try:
    import psycopg2
    psycopg2  # Silence lint.
except ImportError:
    has_psycopg = False
else:
    has_psycopg = True


try:
    import subunit
    subunit  # Silence lint.
except ImportError:
    has_subunit = False
else:
    has_subunit = True


def find_tests(testpaths=()):
    """Find all test paths, or test paths contained in the provided sequence.

    @param testpaths: If provided, only tests in the given sequence will
                      be considered.  If not provided, all tests are
                      considered.
    @return: a test suite containing the requested tests.
    """
    suite = unittest.TestSuite()
    topdir = os.path.abspath(
        os.path.join(os.path.dirname(__file__), os.pardir))
    testdir = os.path.dirname(__file__)
    testpaths = set(testpaths)
    for root, dirnames, filenames in os.walk(testdir):
        for filename in filenames:
            filepath = os.path.join(root, filename)
            relpath = filepath[len(topdir)+1:]

            if (filename == "__init__.py" or filename.endswith(".pyc") or
                relpath == os.path.join("tests", "conftest.py")):
                # Skip non-tests.
                continue

            if testpaths:
                # Skip any tests not in testpaths.
                for testpath in testpaths:
                    if relpath.startswith(testpath):
                        break
                else:
                    continue

            if filename.endswith(".py"):
                modpath = relpath.replace(os.path.sep, ".")[:-3]
                module = __import__(modpath, None, None, [""])
                suite.addTest(
                    unittest.defaultTestLoader.loadTestsFromModule(module))
            elif filename.endswith(".txt"):
                load_test = True
                if relpath == os.path.join("tests", "zope", "README.txt"):
                    # Special case the inclusion of the Zope-dependent
                    # ZStorm doctest.
                    import tests.zope as ztest
                    load_test = (
                        ztest.has_transaction and
                        ztest.has_zope_component and
                        ztest.has_zope_security)
                if load_test:
                    parent_path = os.path.dirname(relpath).replace(
                        os.path.sep, ".")
                    parent_module = __import__(parent_path, None, None, [""])
                    suite.addTest(doctest.DocFileSuite(
                            os.path.basename(relpath),
                            module_relative=True,
                            package=parent_module,
                            optionflags=doctest.ELLIPSIS))

    return suite
