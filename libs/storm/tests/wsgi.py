import Queue
from unittest import TestCase
import threading
import time

from storm.wsgi import make_app

class TestMakeApp(TestCase):

    def stub_app(self, environ, start_response):
        if getattr(self, 'in_request', None):
            self.in_request()
        getattr(self, 'calls', []).append('stub_app')
        start_response('200 OK', [])
        yield ''
        if getattr(self, 'in_generator', None):
            self.in_generator()

    def stub_start_response(self, status, headers):
        pass

    def test_find_timeline_outside_request(self):
        app, find_timeline = make_app(self.stub_app)
        # outside a request, find_timeline returns nothing:
        self.assertEqual(None, find_timeline())

    def test_find_timeline_in_request_not_set(self):
        # In a request, with no timeline object in the environ, find_timeline
        # returns None:
        app, find_timeline = make_app(self.stub_app)
        self.in_request = lambda:self.assertEqual(None, find_timeline())
        self.calls = []
        list(app({}, self.stub_start_response))
        # And we definitely got into the call:
        self.assertEqual(['stub_app'], self.calls)

    def test_find_timeline_set_in_environ(self):
        # If a timeline object is known, find_timeline finds it:
        app, find_timeline = make_app(self.stub_app)
        timeline = FakeTimeline()
        self.in_request = lambda:self.assertEqual(timeline, find_timeline())
        list(app({'timeline.timeline': timeline}, self.stub_start_response))

    def test_find_timeline_set_in_environ_during_generator(self):
        # If a timeline object is known, find_timeline finds it:
        app, find_timeline = make_app(self.stub_app)
        timeline = FakeTimeline()
        self.in_generator = lambda:self.assertEqual(timeline, find_timeline())
        list(app({'timeline.timeline': timeline}, self.stub_start_response))

    def test_timeline_is_replaced_in_subsequent_request(self):
        app, find_timeline = make_app(self.stub_app)
        timeline = FakeTimeline()
        self.in_request = lambda:self.assertEqual(timeline, find_timeline())
        list(app({'timeline.timeline': timeline}, self.stub_start_response))

        # Having left the request, the timeline is left behind...
        self.assertEqual(timeline, find_timeline())
        # ... but only until the next request comes through.
        timeline2 = FakeTimeline()
        self.in_request = lambda:self.assertEqual(timeline2, find_timeline())
        list(app({'timeline.timeline': timeline2}, self.stub_start_response))

    def test_lookups_are_threaded(self):
        # with two threads in a request at once, each only sees their own
        # timeline.
        app, find_timeline = make_app(self.stub_app)
        errors = Queue.Queue()
        sync = threading.Condition()
        waiting = []
        def check_timeline():
            timeline = FakeTimeline()
            def start_response(status, headers):
                # Block on the condition, so all test threads are in
                # start_response when the test resumes.
                sync.acquire()
                waiting.append('x')
                sync.wait()
                sync.release()
                found_timeline = find_timeline()
                if found_timeline != timeline:
                    errors.put((found_timeline, timeline))
            list(app({'timeline.timeline': timeline}, start_response))
        t1 = threading.Thread(target=check_timeline)
        t2 = threading.Thread(target=check_timeline)
        t1.start()
        try:
            t2.start()
            try:
                while True:
                    sync.acquire()
                    if len(waiting) == 2:
                        break
                    sync.release()
                    time.sleep(0)
                sync.notify()
                sync.notify()
                sync.release()
            finally:
                t2.join()
        finally:
            t1.join()
        if errors.qsize():
            found_timeline, timeline = errors.get(False)
            self.assertEqual(timeline, found_timeline)


class FakeTimeline(object):
    """A fake Timeline.

    We need this because we can't use plain object instances as they can't be
    weakreferenced.
    """
