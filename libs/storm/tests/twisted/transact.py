from tests import has_psycopg
from tests.helper import TestHelper
from tests.zope import has_transaction, has_zope_component
from tests.twisted import has_twisted

if has_transaction and has_zope_component and has_twisted:
    import transaction

    from twisted.trial.unittest import TestCase
    from zope.component import getUtility

    from storm.zope.interfaces import IZStorm
    from storm.exceptions import IntegrityError, DisconnectionError

    from storm.twisted.transact import Transactor, transact
    from storm.twisted.testing import FakeThreadPool
else:
    # We can't use trial's TestCase as base
    TestCase = TestHelper
    TestHelper = object

if has_psycopg:
    from psycopg2.extensions import TransactionRollbackError


class TransactorTest(TestCase, TestHelper):

    def is_supported(self):
        return has_transaction and has_zope_component and has_twisted

    def setUp(self):
        TestCase.setUp(self)
        TestHelper.setUp(self)
        self.threadpool = FakeThreadPool()
        self.transaction = self.mocker.mock()
        self.transactor = Transactor(self.threadpool, self.transaction)
        self.function = self.mocker.mock()

    def test_run(self):
        """
        L{Transactor.run} executes a function in a thread, commits
        the transaction and returns a deferred firing the function result.
        """
        self.mocker.order()
        self.expect(self.function(1, arg=2)).result(3)
        self.expect(self.transaction.commit())
        self.mocker.replay()
        deferred = self.transactor.run(self.function, 1, arg=2)
        deferred.addCallback(self.assertEqual, 3)
        return deferred

    def test_run_with_function_failure(self):
        """
        If the given function raises an error, then L{Transactor.run}
        aborts the transaction and re-raises the same error.
        """
        self.mocker.order()
        self.expect(self.function()).throw(ZeroDivisionError())
        self.expect(self.transaction.abort())
        self.mocker.replay()
        deferred = self.transactor.run(self.function)
        self.assertFailure(deferred, ZeroDivisionError)
        return deferred

    def test_run_with_disconnection_error(self):
        """
        If the given function raises a L{DisconnectionError}, then a C{SELECT
        1} will be executed in each registered store such that C{psycopg}
        actually detects the disconnection.
        """
        self.transactor.retries = 0
        self.mocker.order()
        zstorm = self.mocker.mock()
        store1 = self.mocker.mock()
        store2 = self.mocker.mock()
        gu = self.mocker.replace(getUtility)
        self.expect(self.function()).throw(DisconnectionError())
        self.expect(gu(IZStorm)).result(zstorm)
        self.expect(zstorm.iterstores()).result(iter((("store1", store1),
                                                      ("store2", store2))))
        self.expect(store1.execute("SELECT 1"))
        self.expect(store2.execute("SELECT 1"))
        self.expect(self.transaction.abort())
        self.mocker.replay()
        deferred = self.transactor.run(self.function)
        self.assertFailure(deferred, DisconnectionError)
        return deferred

    def test_run_with_disconnection_error_in_execute_is_ignored(self):
        """
        If the given function raises a L{DisconnectionError}, then a C{SELECT
        1} will be executed in each registered store such that C{psycopg}
        actually detects the disconnection. If another L{DisconnectionError}
        happens during C{execute}, then it is ignored.
        """
        self.transactor.retries = 0
        zstorm = self.mocker.mock()
        store1 = self.mocker.mock()
        store2 = self.mocker.mock()
        gu = self.mocker.replace(getUtility)
        self.mocker.order()
        self.expect(self.function()).throw(DisconnectionError())
        self.expect(gu(IZStorm)).result(zstorm)
        self.expect(zstorm.iterstores()).result(iter((("store1", store1),
                                                      ("store2", store2))))
        self.expect(store1.execute("SELECT 1")).throw(DisconnectionError())
        self.expect(store2.execute("SELECT 1"))
        self.expect(self.transaction.abort())
        self.mocker.replay()
        deferred = self.transactor.run(self.function)
        self.assertFailure(deferred, DisconnectionError)
        return deferred

    def test_run_with_commit_failure(self):
        """
        If the given function succeeds but the transaction fails to commit,
        then L{Transactor.run} aborts the transaction and re-raises
        the commit exception.
        """
        self.mocker.order()
        self.expect(self.function())
        self.expect(self.transaction.commit()).throw(ZeroDivisionError())
        self.expect(self.transaction.abort())
        self.mocker.replay()
        deferred = self.transactor.run(self.function)
        self.assertFailure(deferred, ZeroDivisionError)
        return deferred

    def test_wb_default_transaction(self):
        """
        By default L{Transact} uses the global transaction manager.
        """
        transactor = Transactor(self.threadpool)
        self.assertIdentical(transaction, transactor._transaction)

    def test_decorate(self):
        """
        A L{transact} decorator can be used with methods of an object that
        contains a L{Transactor} instance as a C{transactor} instance variable,
        ensuring that the decorated function is called via L{Transactor.run}.
        """
        self.mocker.order()
        self.expect(self.transaction.commit())
        self.mocker.replay()

        @transact
        def function(self):
            """docstring"""
            return "result"

        # Function metadata is copied to the wrapper.
        self.assertEqual("docstring", function.__doc__)
        deferred = function(self)
        deferred.addCallback(self.assertEqual, "result")
        return deferred

    def test_run_with_integrity_error_retries(self):
        """
        If the given function raises a L{IntegrityError}, then the function
        will be retried another two times before letting the exception bubble
        up.
        """
        self.transactor.sleep = self.mocker.mock()
        self.transactor.uniform = self.mocker.mock()
        self.mocker.order()

        self.expect(self.function()).throw(IntegrityError())
        self.expect(self.transaction.abort())
        self.expect(self.transactor.uniform(1, 2 ** 1)).result(1)
        self.expect(self.transactor.sleep(1))

        self.expect(self.function()).throw(IntegrityError())
        self.expect(self.transaction.abort())
        self.expect(self.transactor.uniform(1, 2 ** 2)).result(2)
        self.expect(self.transactor.sleep(2))

        self.expect(self.function()).throw(IntegrityError())
        self.expect(self.transaction.abort())
        self.mocker.replay()

        deferred = self.transactor.run(self.function)
        self.assertFailure(deferred, IntegrityError)
        return deferred

    def test_run_with_transaction_rollback_error_retries(self):
        """
        If the given function raises a L{TransactionRollbackError}, then the
        function will be retried another two times before letting the exception
        bubble up.
        """
        if not has_psycopg:
            return

        self.transactor.sleep = self.mocker.mock()
        self.transactor.uniform = self.mocker.mock()
        self.mocker.order()

        self.expect(self.function()).throw(TransactionRollbackError())
        self.expect(self.transaction.abort())
        self.expect(self.transactor.uniform(1, 2 ** 1)).result(1)
        self.expect(self.transactor.sleep(1))

        self.expect(self.function()).throw(TransactionRollbackError())
        self.expect(self.transaction.abort())
        self.expect(self.transactor.uniform(1, 2 ** 2)).result(2)
        self.expect(self.transactor.sleep(2))

        self.expect(self.function()).throw(TransactionRollbackError())
        self.expect(self.transaction.abort())
        self.mocker.replay()

        deferred = self.transactor.run(self.function)
        self.assertFailure(deferred, TransactionRollbackError)
        return deferred

    def test_run_with_disconnection_error_retries(self):
        """
        If the given function raises a L{DisconnectionError}, then the
        function will be retried another two times before letting the exception
        bubble up.
        """
        zstorm = self.mocker.mock()
        gu = self.mocker.replace(getUtility)
        self.transactor.sleep = self.mocker.mock()
        self.transactor.uniform = self.mocker.mock()
        self.mocker.order()

        self.expect(self.function()).throw(DisconnectionError())
        self.expect(gu(IZStorm)).result(zstorm)
        self.expect(zstorm.iterstores()).result(iter(()))
        self.expect(self.transaction.abort())
        self.expect(self.transactor.uniform(1, 2 ** 1)).result(1)
        self.expect(self.transactor.sleep(1))

        self.expect(self.function()).throw(DisconnectionError())
        self.expect(gu(IZStorm)).result(zstorm)
        self.expect(zstorm.iterstores()).result(iter(()))
        self.expect(self.transaction.abort())
        self.expect(self.transactor.uniform(1, 2 ** 2)).result(2)
        self.expect(self.transactor.sleep(2))

        self.expect(self.function()).throw(DisconnectionError())
        self.expect(gu(IZStorm)).result(zstorm)
        self.expect(zstorm.iterstores()).result(iter(()))
        self.expect(self.transaction.abort())
        self.mocker.replay()

        deferred = self.transactor.run(self.function)
        self.assertFailure(deferred, DisconnectionError)
        return deferred

    def test_run_with_integrity_error_on_commit_retries(self):
        """
        If the given function raises a L{IntegrityError}, then the function
        will be retried another two times before letting the exception bubble
        up.
        """
        self.transactor.sleep = self.mocker.mock()
        self.transactor.uniform = self.mocker.mock()
        self.mocker.order()

        self.expect(self.function())
        self.expect(self.transaction.commit()).throw(IntegrityError())
        self.expect(self.transaction.abort())
        self.expect(self.transactor.uniform(1, 2 ** 1)).result(1)
        self.expect(self.transactor.sleep(1))

        self.expect(self.function())
        self.expect(self.transaction.commit()).throw(IntegrityError())
        self.expect(self.transaction.abort())
        self.expect(self.transactor.uniform(1, 2 ** 2)).result(2)
        self.expect(self.transactor.sleep(2))

        self.expect(self.function())
        self.expect(self.transaction.commit()).throw(IntegrityError())
        self.expect(self.transaction.abort())
        self.mocker.replay()

        deferred = self.transactor.run(self.function)
        self.assertFailure(deferred, IntegrityError)
        return deferred

    def test_run_with_on_retry_callback(self):
        """
        If a retry callback is passed with the C{on_retry} parameter, then
        it's invoked with the number of retries performed so far.
        """
        calls = []

        def on_retry(context):
            calls.append(context)

        self.transactor.on_retry = on_retry

        self.transactor.sleep = self.mocker.mock()
        self.transactor.uniform = self.mocker.mock()
        self.mocker.order()

        self.expect(self.function(1, a=2))
        error = IntegrityError()
        self.expect(self.transaction.commit()).throw(error)
        self.expect(self.transaction.abort())
        self.expect(self.transactor.uniform(1, 2 ** 1)).result(1)
        self.expect(self.transactor.sleep(1))

        self.expect(self.function(1, a=2))
        self.expect(self.transaction.commit())
        self.mocker.replay()

        deferred = self.transactor.run(self.function, 1, a=2)

        def check(_):
            [context] = calls

            self.assertEqual(self.function, context.function)
            self.assertEqual((1,), context.args)
            self.assertEqual({"a": 2}, context.kwargs)
            self.assertEqual(1, context.retry)
            self.assertEqual(1, context.retry)
            self.assertIs(error, context.error)

        return deferred.addCallback(check)
