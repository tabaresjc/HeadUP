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

import transaction

from testresources import TestResourceManager
from zope.component import provideUtility, getUtility

from storm.schema.patch import UnknownPatchError
from storm.zope.zstorm import ZStorm, global_zstorm
from storm.zope.interfaces import IZStorm


class ZStormResourceManager(TestResourceManager):
    """Provide a L{ZStorm} resource to be used in test cases.

    The constructor is passed the details of the L{Store}s to be registered
    in the provided L{ZStore} resource. Then the C{make} and C{clean} methods
    make sure that such L{Store}s are properly setup and cleaned for each test.

    @param databases: A C{list} of C{dict}s holding the following keys:
        - 'name', the name of the store to be registered.
        - 'uri', the database URI to use to create the store.
        - 'schema', optionally, the L{Schema} for the tables in the store, if
          not given no schema will be applied.
        - 'schema-uri', optionally an alternate URI to use for applying the
          schema, if not given it defaults to 'uri'.

    @ivar force_delete: If C{True} for running L{Schema.delete} on a L{Store}
        even if no commit was performed by the test. Useful when running a test
        in a subprocess that might commit behind our back.
    @ivar use_global_zstorm: If C{True} then the C{global_zstorm} object from
        C{storm.zope.zstorm} will be used, instead of creating a new one. This
        is useful for code loading the zcml directives of C{storm.zope}.
    @ivar schema_stamp_dir: Optionally, a path to a directory that will be used
        to save timestamps of the schema's patch packages, so schema upgrades
        will be performed only when needed. This is just an optimisation to let
        the resource setup a bit faster.
    """
    force_delete = False
    use_global_zstorm = False
    schema_stamp_dir = None

    def __init__(self, databases):
        super(ZStormResourceManager, self).__init__()
        self._databases = databases
        self._zstorm = None
        self._schema_zstorm = None
        self._commits = {}
        self._schemas = {}

    def make(self, dependencies):
        """Create a L{ZStorm} resource to be used by tests.

        @return: A L{ZStorm} object that will be shared among all tests using
            this resource manager.
        """
        if self._zstorm is None:

            if self.use_global_zstorm:
                self._zstorm = global_zstorm
            else:
                self._zstorm = ZStorm()
            self._schema_zstorm = ZStorm()

            databases = self._databases

            # Adapt the old databases format to the new one, for backward
            # compatibility. This should be eventually dropped.
            if isinstance(databases, dict):
                databases = [{"name": name, "uri": uri, "schema": schema}
                             for name, (uri, schema) in databases.iteritems()]

            # Provide the global IZStorm utility before applying patches, so
            # patch code can get the ztorm object if needed (e.g. looking up
            # other stores).
            provideUtility(self._zstorm)

            self._set_create_hook()

            for database in databases:
                name = database["name"]
                uri = database["uri"]
                schema = database.get("schema")
                schema_uri = database.get("schema-uri", uri)
                self._zstorm.set_default_uri(name, uri)
                if schema is not None:
                    # The configuration for this database does not include a
                    # schema definition, so we just setup the store (the user
                    # code should apply the schema elsewhere, if any)
                    self._schemas[name] = schema
                    self._schema_zstorm.set_default_uri(name, schema_uri)
                    self._ensure_schema(name, schema)

            # Commit all schema changes across all stores
            transaction.commit()

        elif getUtility(IZStorm) is not self._zstorm:
            # This probably means that the test code has overwritten our
            # utility, let's re-register it.
            provideUtility(self._zstorm)

        return self._zstorm

    def _set_create_hook(self):
        """
        Set a hook in ZStorm.create, so we can lazily set commit proxies.
        """
        self._zstorm.__real_create__ = self._zstorm.create

        def create_hook(name, uri=None):
            store = self._zstorm.__real_create__(name, uri=uri)
            if self._schemas.get(name) is not None:
                # Only set commit proxies for databases that have a schema
                # that we can use for cleanup
                self._set_commit_proxy(store)
            return store

        self._zstorm.create = create_hook

    def _set_commit_proxy(self, store):
        """Set a commit proxy to keep track of commits and clean up the tables.

        @param store: The L{Store} to set the commit proxy on. Any commit on
            this store will result in the associated tables to be cleaned upon
            tear down.
        """
        store.__real_commit__ = store.commit

        def commit_proxy():
            self._commits[store] = True
            store.__real_commit__()

        store.commit = commit_proxy

    def _ensure_schema(self, name, schema):
        """Ensure that the schema for the given database is up-to-date.

        As an optimisation, if the C{schema_stamp_dir} attribute is set, then
        this method performs a fast check based on the patch directory
        timestamp rather than the database patch table, so connections and
        upgrade queries can be skipped if there's no need.

        @param name: The name of the database to check.
        @param schema: The schema to be ensured.
        """
        # If a schema stamp directory is set, then figure out whether there's
        # need to upgrade the schema by looking at timestamps.
        if self.schema_stamp_dir is not None:
            schema_mtime = self._get_schema_mtime(schema)
            schema_stamp_mtime = self._get_schema_stamp_mtime(name)

            # The modification time of the schema's patch directory matches our
            # timestamp, so the schema is already up-to-date
            if schema_mtime == schema_stamp_mtime:
                return

            # Save the modification time of the schema's patch directory so in
            # subsequent runs we'll know if we're already up-to-date
            self._set_schema_stamp_mtime(name, schema_mtime)

        schema_store = self._schema_zstorm.get(name)
        # Disable schema autocommits, we will commit everything at once
        schema.autocommit(False)
        try:
            schema.upgrade(schema_store)
        except UnknownPatchError:
            schema.drop(schema_store)
            schema_store.commit()
            schema.upgrade(schema_store)
        else:
            # Clean up tables here to ensure that the first test run starts
            # with an empty db
            schema.delete(schema_store)

    def _get_schema_mtime(self, schema):
        """
        Return the modification time of the C{schema}'s patch directory.
        """
        schema_stat = os.stat(os.path.dirname(schema._patch_package.__file__))
        return int(schema_stat.st_mtime)

    def _get_schema_stamp_mtime(self, name):
        """
        Return the modification time of schemas's patch directory, as saved
        in the stamp directory.
        """
        # Let's create the stamp directory if it doesn't exist
        if not os.path.exists(self.schema_stamp_dir):
            os.makedirs(self.schema_stamp_dir)

        schema_stamp_path = os.path.join(self.schema_stamp_dir, name)

        # Get the last schema modification time we ran the upgrade for, or -1
        # if this is our first run
        if os.path.exists(schema_stamp_path):
            with open(schema_stamp_path) as fd:
                schema_stamp_mtime = int(fd.read())
        else:
            schema_stamp_mtime = -1

        return schema_stamp_mtime

    def _set_schema_stamp_mtime(self, name, schema_mtime):
        """
        Save the schema's modification time in the stamp directory.
        """
        schema_stamp_path = os.path.join(self.schema_stamp_dir, name)
        with open(schema_stamp_path, "w") as fd:
            fd.write("%d" % schema_mtime)

    def clean(self, resource):
        """Clean up the stores after a test."""
        try:
            for name, store in self._zstorm.iterstores():
                # Ensure that the store is in a consistent state
                store.flush()
                # Clear the alive cache *before* abort is called,
                # to prevent a useless loop in Store.invalidate
                # over the alive objects
                store._alive.clear()
        finally:
            transaction.abort()

        # Clean up tables after each test if a commit was made
        needs_commit = False
        for name, store in self._zstorm.iterstores():
            if self.force_delete or store in self._commits:
                schema_store = self._schema_zstorm.get(name)
                schema = self._schemas[name]
                schema.delete(schema_store)
                needs_commit = True
        if needs_commit:
            transaction.commit()
        self._commits = {}
