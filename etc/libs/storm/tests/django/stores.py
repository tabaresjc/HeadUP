#
# Copyright (c) 2008 Canonical
#
# Written by James Henstridge <jamesh@canonical.com>
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

import threading

try:
    import django
    import transaction
except ImportError:
    have_django_and_transaction = False
else:
    have_django_and_transaction = True
    from django import conf
    from storm.django import stores
    from storm.zope.zstorm import global_zstorm

from storm.store import Store
from tests.helper import TestHelper


class DjangoStoreTests(TestHelper):

    def is_supported(self):
        return have_django_and_transaction

    def setUp(self):
        super(DjangoStoreTests, self).setUp()
        conf.settings.configure(STORM_STORES={})

    def tearDown(self):
        if django.VERSION >= (1, 1):
            conf.settings._wrapped = None
        else:
            conf.settings._target = None
        # Reset the utility to cleanup the StoreSynchronizer's from the
        # transaction.
        global_zstorm._reset()
        stores.have_configured_stores = False
        # Free the transaction to avoid having errors that cross
        # test cases.
        transaction.manager.free(transaction.get())
        super(DjangoStoreTests, self).tearDown()

    def test_configure_stores_configures_store_uris(self):
        conf.settings.MIDDLEWARE_CLASSES += (
            "storm.django.middleware.ZopeTransactionMiddleware",)
        conf.settings.STORM_STORES = {"name1": "sqlite:1",
                                      "name2": "sqlite:2",
                                      "name3": "sqlite:3"}
        stores.configure_stores(conf.settings)
        default_uris = global_zstorm.get_default_uris()
        self.assertEquals(default_uris, {"name1": "sqlite:1",
                                         "name2": "sqlite:2",
                                         "name3": "sqlite:3"})

    def test_get_store(self):
        conf.settings.MIDDLEWARE_CLASSES += (
            "storm.django.middleware.ZopeTransactionMiddleware",)
        conf.settings.STORM_STORES = {"name": "sqlite:"}
        store = stores.get_store("name")
        self.assertTrue(isinstance(store, Store))
        # Calling get_store() twice returns the same store.
        store2 = stores.get_store("name")
        self.assertTrue(store is store2)

    def test_get_store_returns_per_thread_stores(self):
        conf.settings.MIDDLEWARE_CLASSES += (
            "storm.django.middleware.ZopeTransactionMiddleware",)
        conf.settings.STORM_STORES = {"name": "sqlite:"}

        store = stores.get_store("name")
        other_stores = []
        def f():
            other_stores.append(stores.get_store("name"))

        thread = threading.Thread(target=f)
        thread.start()
        thread.join()
        self.assertEqual(len(other_stores), 1)
        self.assertNotEqual(other_stores[0], store)

    def test_get_store_uri(self):
        conf.settings.MIDDLEWARE_CLASSES += (
            "storm.django.middleware.ZopeTransactionMiddleware",)
        conf.settings.STORM_STORES = {"name": "sqlite:"}

        self.assertEqual(stores.get_store_uri("name"), "sqlite:")
