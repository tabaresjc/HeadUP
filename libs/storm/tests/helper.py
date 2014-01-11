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
from cStringIO import StringIO
import tempfile
import logging
import shutil
import sys

from tests import mocker


__all__ = ["TestHelper", "MakePath", "LogKeeper"]


class TestHelper(mocker.MockerTestCase):

    helpers = []

    def is_supported(self):
        return True

    def setUp(self):
        super(TestHelper, self).setUp()
        self._helper_instances = []
        for helper_factory in self.helpers:
            helper = helper_factory()
            helper.set_up(self)
            self._helper_instances.append(helper)

    def tearDown(self):
        for helper in reversed(self._helper_instances):
            helper.tear_down(self)
        super(TestHelper, self).tearDown()

    @property
    def _testMethod(self):
        try:
            name = self._testMethodName
        except AttributeError:
            # On Python < 2.5
            name = self._TestCase__testMethodName
        return getattr(self, name)

    def run(self, result=None):
        # Skip if is_supported() does not return True.
        if not self.is_supported():
            if hasattr(result, "addSkip"):
                result.startTest(self)
                result.addSkip(self, "Test not supported")
            return
        super(TestHelper, self).run(result)

    def assertVariablesEqual(self, checked, expected):
        self.assertEquals(len(checked), len(expected))
        for check, expect in zip(checked, expected):
            self.assertEquals(check.__class__, expect.__class__)
            self.assertEquals(check.get(), expect.get())


class MakePath(object):

    def set_up(self, test_case):
        self.dirname = tempfile.mkdtemp()
        self.dirs = []
        self.counter = 0
        test_case.make_dir = self.make_dir
        test_case.make_path = self.make_path

    def tear_down(self, test_case):
        shutil.rmtree(self.dirname)
        [shutil.rmtree(dir) for dir in self.dirs]

    def make_dir(self):
        path = tempfile.mkdtemp()
        self.dirs.append(path)
        return path

    def make_path(self, content=None, path=None):
        if path is None:
            self.counter += 1
            path = "%s/%03d" % (self.dirname, self.counter)
        if content is not None:
            file = open(path, "w")
            try:
                file.write(content)
            finally:
                file.close()
        return path


class LogKeeper(object):
    """Record logging information.

    Puts a 'logfile' attribute on your test case, which is a StringIO
    containing all log output.
    """

    def set_up(self, test_case):
        logger = logging.getLogger()
        test_case.logfile = StringIO()
        handler = logging.StreamHandler(test_case.logfile)
        self.old_handlers = logger.handlers
        # Sanity check; this might not be 100% what we want
        if self.old_handlers:
            test_case.assertEquals(len(self.old_handlers), 1)
            test_case.assertEquals(self.old_handlers[0].stream, sys.stderr)
        logger.handlers = [handler]

    def tear_down(self, test_case):
        logging.getLogger().handlers = self.old_handlers
