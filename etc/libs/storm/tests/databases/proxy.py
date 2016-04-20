# -*- encoding: utf-8 -*-
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
import select
import socket
import SocketServer
import threading


TIMEOUT = 0.1


class ProxyRequestHandler(SocketServer.BaseRequestHandler):
    """A request handler that proxies traffic to another TCP port."""

    def __init__(self, request, client_address, server):
        self._generation = server._generation
        SocketServer.BaseRequestHandler.__init__(
            self, request, client_address, server)

    def handle(self):
        dst = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        dst.connect(self.server.proxy_dest)

        readers = [self.request, dst]
        while readers:
            rlist, wlist, xlist = select.select(readers, [], [], TIMEOUT)

            # If the server generation has been incremented, close the
            # connection.
            if self._generation != self.server._generation:
                return

            if self.request in rlist:
                chunk = os.read(self.request.fileno(), 1024)
                dst.send(chunk)
                if chunk == "":
                    readers.remove(self.request)
                    dst.shutdown(socket.SHUT_WR)

            if dst in rlist:
                chunk = os.read(dst.fileno(), 1024)
                self.request.send(chunk)
                if chunk == "":
                    readers.remove(dst)
                    self.request.shutdown(socket.SHUT_WR)


class ProxyTCPServer(SocketServer.ThreadingTCPServer):

    allow_reuse_address = True

    def __init__(self, proxy_dest):
        SocketServer.ThreadingTCPServer.__init__(
            self, ("127.0.0.1", 0), ProxyRequestHandler)
        # Python 2.4 doesn't retrieve the socket details, so record
        # them here.  We need to do this so we can recreate the socket
        # with the same address later.
        self.server_address = self.socket.getsockname()

        self.proxy_dest = proxy_dest
        self._start_lock = threading.Lock()
        self._thread = None
        self._generation = 0
        self._running = False
        self.start()

    def __del__(self):
        self.close()

    def close(self):
        if self._running:
            self.stop()

    def start(self):
        assert not self._running, "Server should not be running"
        self._thread = threading.Thread(target=self._run)
        self._thread.setDaemon(True)

        self._running = True
        self._start_lock.acquire()
        self._thread.start()
        # Wait for server to start
        self._start_lock.acquire()
        self._start_lock.release()

    def _run(self):
        self.server_activate()
        self.socket.settimeout(TIMEOUT)
        self._start_lock.release()
        while self._running:
            try:
                self.handle_request()
            except socket.timeout:
                pass

    def stop(self):
        assert self._running, "Server should be running"
        # Increment server generation, and wait for thread to stop.
        self._generation += 1
        self._running = False
        self._thread.join()

        # Recreate socket, to kill listen queue.  As we've allowed
        # address reuse, this should work.
        self.socket.close()
        self.socket = socket.socket(self.address_family,
                                    self.socket_type)
        self.server_bind()

    def restart(self):
        self.stop()
        self.start()
