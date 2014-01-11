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

from storm.locals import StormError, Store, create_database
from storm.schema import Schema
from tests.mocker import MockerTestCase


class Package(object):

    def __init__(self, package_dir, name):
        self.name = name
        self._package_dir = package_dir

    def create_module(self, filename, contents):
        filename = os.path.join(self._package_dir, filename)
        file = open(filename, "w")
        file.write(contents)
        file.close()


class SchemaTest(MockerTestCase):

    def setUp(self):
        super(SchemaTest, self).setUp()
        self.database = create_database("sqlite:///%s" % self.makeFile())
        self.store = Store(self.database)

        self._package_dirs = set()
        self._package_names = set()
        self.package = self.create_package(self.makeDir(), "patch_package")
        import patch_package

        creates = ["CREATE TABLE person (id INTEGER, name TEXT)"]
        drops = ["DROP TABLE person"]
        deletes = ["DELETE FROM person"]

        self.schema = Schema(creates, drops, deletes, patch_package)

    def tearDown(self):
        for package_dir in self._package_dirs:
            sys.path.remove(package_dir)

        for name in list(sys.modules):
            if name in self._package_names:
                del sys.modules[name]
            elif filter(
                None,
                [name.startswith("%s." % x) for x in self._package_names]):
                del sys.modules[name]

        super(SchemaTest, self).tearDown()

    def create_package(self, base_dir, name, init_module=None):
        """Create a Python package.

        Packages created using this method will be removed from L{sys.path}
        and L{sys.modules} during L{tearDown}.

        @param package_dir: The directory in which to create the new package.
        @param name: The name of the package.
        @param init_module: Optionally, the text to include in the __init__.py
            file.
        @return: A L{Package} instance that can be used to create modules.
        """
        package_dir = os.path.join(base_dir, name)
        self._package_names.add(name)
        os.makedirs(package_dir)

        file = open(os.path.join(package_dir, "__init__.py"), "w")
        if init_module:
            file.write(init_module)
        file.close()
        sys.path.append(base_dir)
        self._package_dirs.add(base_dir)

        return Package(package_dir, name)

    def test_create(self):
        """
        L{Schema.create} can be used to create the tables of a L{Store}.
        """
        self.assertRaises(StormError,
                          self.store.execute, "SELECT * FROM person")
        self.schema.create(self.store)
        self.assertEquals(list(self.store.execute("SELECT * FROM person")), [])

    def test_create_with_autocommit_off(self):
        """
        L{Schema.autocommit} can be used to turn automatic commits off.
        """
        self.schema.autocommit(False)
        self.schema.create(self.store)
        self.store.rollback()
        self.assertRaises(StormError, self.store.execute,
                          "SELECT * FROM patch")

    def test_drop(self):
        """
        L{Schema.drop} can be used to drop the tables of a L{Store}.
        """
        self.schema.create(self.store)
        self.assertEquals(list(self.store.execute("SELECT * FROM person")), [])
        self.schema.drop(self.store)
        self.assertRaises(StormError,
                          self.store.execute, "SELECT * FROM person")

    def test_drop_with_missing_patch_table(self):
        """
        L{Schema.drop} works fine even if the user's supplied statements end up
        dropping the patch table that we created.
        """
        import patch_package
        schema = Schema([], ["DROP TABLE patch"], [], patch_package)
        schema.create(self.store)
        schema.drop(self.store)
        self.assertRaises(StormError,
                          self.store.execute, "SELECT * FROM patch")

    def test_delete(self):
        """
        L{Schema.delete} can be used to clear the tables of a L{Store}.
        """
        self.schema.create(self.store)
        self.store.execute("INSERT INTO person (id, name) VALUES (1, 'Jane')")
        self.assertEquals(list(self.store.execute("SELECT * FROM person")),
                          [(1, u"Jane")])
        self.schema.delete(self.store)
        self.assertEquals(list(self.store.execute("SELECT * FROM person")), [])

    def test_upgrade_creates_schema(self):
        """
        L{Schema.upgrade} creates a schema from scratch if no exist, and is
        effectively equivalent to L{Schema.create} in such case.
        """
        self.assertRaises(StormError,
                          self.store.execute, "SELECT * FROM person")
        self.schema.upgrade(self.store)
        self.assertEquals(list(self.store.execute("SELECT * FROM person")), [])

    def test_upgrade_marks_patches_applied(self):
        """
        L{Schema.upgrade} updates the patch table after applying the needed
        patches.
        """
        contents = """
def apply(store):
    store.execute('ALTER TABLE person ADD COLUMN phone TEXT')
"""
        self.package.create_module("patch_1.py", contents)
        statement = "SELECT * FROM patch"
        self.assertRaises(StormError, self.store.execute, statement)
        self.schema.upgrade(self.store)
        self.assertEquals(list(self.store.execute("SELECT * FROM patch")),
                          [(1,)])

    def test_upgrade_applies_patches(self):
        """
        L{Schema.upgrade} executes the needed patches, that typically modify
        the existing schema.
        """
        self.schema.create(self.store)
        contents = """
def apply(store):
    store.execute('ALTER TABLE person ADD COLUMN phone TEXT')
"""
        self.package.create_module("patch_1.py", contents)
        self.schema.upgrade(self.store)
        self.store.execute(
            "INSERT INTO person (id, name, phone) VALUES (1, 'Jane', '123')")
        self.assertEquals(list(self.store.execute("SELECT * FROM person")),
                          [(1, u"Jane", u"123")])
