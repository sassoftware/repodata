#
# Copyright (c) 2011 rPath, Inc.
#
# This program is distributed under the terms of the Common Public License,
# version 1.0. A copy of this license should have been distributed with this
# source file in a file called LICENSE. If it is not present, the license
# is always available at http://www.rpath.com/permanent/licenses/CPL-1.0.
#
# This program is distributed in the hope that it will be useful, but
# without any warranty; without even the implied warranty of merchantability
# or fitness for a particular purpose. See the Common Public License for
# full details.
#

import logging
import socket
import sys

from conary.lib import timeutil
from conary.lib.http import http_error
from conary.lib.http import opener
from conary.repository import transport

log = logging.getLogger(__name__)

TransportError = http_error.TransportError


class URLOpener(opener.URLOpener):
    # Be careful when changing these constants. The exponential backoff will
    # make the sleep times go up really fast. RBL-7871 for details
    RETRIES_ON_ERROR = 6
    BACKOFF_FACTOR = 1.8
    FATAL_ERRORS = set([ 404 ])
    FATAL_SOCKET_ERRORS = set([ socket.EAI_NONAME ])

    def open(self, url, data=None, headers=()):
        timer = timeutil.BackoffTimer()
        timer.factor = self.BACKOFF_FACTOR
        # TODO: push down retry logic to conary

        for i in range(self.RETRIES_ON_ERROR):
            try:
                return opener.URLOpener.open(self, url, data=data,
                        headers=headers)
            except http_error.TransportError, e:
                # If the error is in a specific set, there's no need to retry
                if e.errcode in self.FATAL_ERRORS:
                    raise
                log.error("Error: %s; retrying after %.3f seconds", e,
                    timer.delay)
                timer.sleep()
            except IOError, err:
                if err.args[0] in self.FATAL_SOCKET_ERRORS:
                    raise
                timer.sleep()

        exc_info = sys.exc_info()
        e = exc_info[1]
        if isinstance(e, IOError):
            raise http_error.TransportError("Unable to download: %s" % e), None, exc_info[2]
        raise exc_info[0], exc_info[1], exc_info[2]


class Transport(transport.Transport):
    def parse_response(self, file):
        # Conary's transport assumes the response is a list inside a tuple
        ret = transport.Transport.parse_response(self, file)
        return ([ ret ], )

    def request(self, *args, **kwargs):
        ret = transport.Transport.request(self, *args, **kwargs)
        return ret[0][1]
