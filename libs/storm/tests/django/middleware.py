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

from storm.exceptions import DisconnectionError

try:
    import django
    import transaction
except ImportError:
    have_django_and_transaction = False
else:
    have_django_and_transaction = True
    from django import conf
    from django.http import HttpRequest, HttpResponse
    from storm.django.middleware import ZopeTransactionMiddleware

from tests.helper import TestHelper


class TransactionMiddlewareTests(TestHelper):

    def is_supported(self):
        return have_django_and_transaction

    def setUp(self):
        super(TransactionMiddlewareTests, self).setUp()
        conf.settings.configure(STORM_COMMIT_SAFE_METHODS=False)
        from django.db import transaction as django_transaction
        self.django_transaction = django_transaction

    def tearDown(self):
        if django.VERSION >= (1, 1):
            conf.settings._wrapped = None
        else:
            conf.settings._target = None
        super(TransactionMiddlewareTests, self).tearDown()

    def test_process_request_begins_transaction(self):
        begin = self.mocker.replace("transaction.begin")
        enter_transaction_management = self.mocker.replace(
            "django.db.transaction.enter_transaction_management")
        managed = self.mocker.replace(
            "django.db.transaction.managed")
        enter_transaction_management()
        managed(True)
        begin()
        self.mocker.replay()

        zope_middleware = ZopeTransactionMiddleware()
        request = HttpRequest()
        request.method = "GET"
        zope_middleware.process_request(request)

    def test_process_exception_aborts_transaction(self):
        abort = self.mocker.replace("transaction.abort")
        leave_transaction_management = self.mocker.replace(
            "django.db.transaction.leave_transaction_management")
        set_clean = self.mocker.replace(
            "django.db.transaction.set_clean")
        abort()
        set_clean()
        leave_transaction_management()
        self.mocker.replay()

        zope_middleware = ZopeTransactionMiddleware()
        request = HttpRequest()
        request.method = "GET"
        exception = RuntimeError("some error")
        zope_middleware.process_exception(request, exception)

    def test_process_response_commits_transaction_if_managed(self):
        commit = self.mocker.replace("transaction.commit")
        leave_transaction_management = self.mocker.replace(
            "django.db.transaction.leave_transaction_management")
        is_managed = self.mocker.replace(
            "django.db.transaction.is_managed")
        set_clean = self.mocker.replace(
            "django.db.transaction.set_clean")
        # We test three request methods
        self.expect(is_managed()).result(True).count(3)
        self.expect(commit()).count(3)
        self.expect(set_clean()).count(3)
        self.expect(leave_transaction_management()).count(3)
        self.mocker.replay()

        # Commit on all methods
        conf.settings.STORM_COMMIT_SAFE_METHODS = True

        zope_middleware = ZopeTransactionMiddleware()
        request = HttpRequest()
        response = HttpResponse()

        request.method = "GET"
        zope_middleware.process_response(request, response)
        request.method = "HEAD"
        zope_middleware.process_response(request, response)
        request.method = "POST"
        zope_middleware.process_response(request, response)

    def test_process_response_aborts_transaction_for_safe_methods(self):
        abort = self.mocker.replace("transaction.abort")
        commit = self.mocker.replace("transaction.commit")
        leave_transaction_management = self.mocker.replace(
            "django.db.transaction.leave_transaction_management")
        is_managed = self.mocker.replace(
            "django.db.transaction.is_managed")
        set_clean = self.mocker.replace(
            "django.db.transaction.set_clean")
        # We test three request methods
        self.expect(is_managed()).result(True).count(3)
        self.expect(abort()).count(2)
        commit()
        self.expect(set_clean()).count(3)
        self.expect(leave_transaction_management()).count(3)
        self.mocker.replay()

        # Don't commit on safe methods
        conf.settings.STORM_COMMIT_SAFE_METHODS = False

        zope_middleware = ZopeTransactionMiddleware()
        request = HttpRequest()
        response = HttpResponse()

        request.method = "GET"
        zope_middleware.process_response(request, response)
        request.method = "HEAD"
        zope_middleware.process_response(request, response)
        request.method = "POST"
        zope_middleware.process_response(request, response)

    def test_process_response_aborts_transaction_not_managed(self):
        abort = self.mocker.replace("transaction.abort")
        commit = self.mocker.replace("transaction.commit")
        leave_transaction_management = self.mocker.replace(
            "django.db.transaction.leave_transaction_management")
        is_managed = self.mocker.replace(
            "django.db.transaction.is_managed")
        set_clean = self.mocker.replace(
            "django.db.transaction.set_clean")

        self.expect(is_managed()).result(False).count(2)
        # None of these methods should be called
        self.expect(commit()).count(0)
        self.expect(abort()).count(0)
        self.expect(set_clean()).count(0)
        self.expect(leave_transaction_management()).count(0)
        self.mocker.replay()

        zope_middleware = ZopeTransactionMiddleware()
        request = HttpRequest()
        response = HttpResponse()

        request.method = "GET"
        zope_middleware.process_response(request, response)

        # Try the same with a safe method.
        conf.settings.STORM_COMMIT_SAFE_METHODS = False
        zope_middleware = ZopeTransactionMiddleware()
        zope_middleware.process_response(request, response)

    def test_process_response_aborts_transaction_on_failed_commit(self):
        _transaction = transaction.get()
        resource1 = self.mocker.mock()
        self.expect(resource1.prepare).throw(AttributeError).count(0)
        resource2 = self.mocker.mock()
        self.expect(resource2.prepare).throw(AttributeError).count(0)
        leave_transaction_management = self.mocker.replace(
            "django.db.transaction.leave_transaction_management")
        is_managed = self.mocker.replace(
            "django.db.transaction.is_managed")
        set_clean = self.mocker.replace(
            "django.db.transaction.set_clean")

        self.expect(is_managed()).result(True).count(1)
        self.expect(resource1.tpc_begin(_transaction)).throw(DisconnectionError)
        self.expect(resource1.abort(_transaction)).count(2)
        # None of these methods should be called
        self.expect(set_clean()).count(0)
        self.expect(leave_transaction_management()).count(0)
        self.mocker.replay()

        _transaction.join(resource1)
        zope_middleware = ZopeTransactionMiddleware()
        request = HttpRequest()
        response = HttpResponse()

        # Processing this response should fail on "commit()" with a
        # DisconnectionError. The error is saved by
        # "_saveAndRaiseCommitishError()", and re-raised, so we need to catch
        # it and abort the transaction.
        request.method = "POST"
        self.assertRaises(DisconnectionError, zope_middleware.process_response,
                          request, response)

        # Now the transaction should have been cleared by "abort()". A resource
        # joining the transaction manager should not fail with a
        # "TransactionFailedError".
        transaction.get().join(resource2)
