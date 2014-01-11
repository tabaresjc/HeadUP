#
# Copyright (c) 2006, 2007 Canonical
#
# Written by Robert Collins <robert@canonical.com>
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

"""Glue to wire a storm timeline tracer up to a WSGI app."""

import threading
import weakref

__all__ = ['make_app']

def make_app(app):
    """Capture the per-request timeline object needed for storm tracing.

    To use firstly make your app and then wrap it with this make_app::

       >>> app, find_timeline = make_app(app)

    Then wrap the returned app with the timeline app (or anything that sets
    environ['timeline.timeline'])::

       >>> app = timeline.wsgi.make_app(app)

    Finally install a timeline tracer to capture storm queries::

       >>> install_tracer(TimelineTracer(find_timeline))

    @return: A wrapped WSGI app and a timeline factory function for use with
    TimelineTracer.
    """
    timeline_map = threading.local()
    def wrapper(environ, start_response):
        timeline = environ.get('timeline.timeline')
        timeline_map.timeline = None
        if timeline is not None:
            timeline_map.timeline = weakref.ref(timeline)
        # We could clean up timeline_map.timeline after we're done with the
        # request, but for that we'd have to consume all the data from the
        # underlying app and it wouldn't play well with some non-standard
        # tricks (e.g. let the reactor consume IBodyProducers asynchronously
        # when returning large files) that some people may want to do.
        return app(environ, start_response)

    def get_timeline():
        timeline = getattr(timeline_map, 'timeline', None)
        if timeline is not None:
            return timeline()
    return wrapper, get_timeline
