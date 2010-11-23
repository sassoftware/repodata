#
# Copyright (c) 2010 rPath, Inc.
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
import sys

from conary.repository import transport

log = logging.getLogger(__name__)

from repodata import errors
TransportError = errors.TransportError

class URLOpener(transport.URLOpener):
    # Be careful when changing these constants. The exponential backoff will
    # make the sleep times go up really fast. RBL-7871 for details
    RETRIES_ON_ERROR = 6
    BACKOFF_FACTOR = 1.8
    FATAL_ERRORS = set([ 404 ])
    def http_error_default(self, url, fp, errcode, errmsg, headers, data=None):
        raise TransportError("Unable to open %s: %s" % (url, errmsg),
            msg = errmsg, code = errcode, headers = headers, url = url)

    def open(self, url, data=None):
        timer = transport.BackoffTimer()
        timer.factor = self.BACKOFF_FACTOR

        for i in range(self.RETRIES_ON_ERROR):
            try:
                return transport.URLOpener.open(self, url, data=data)
            except TransportError, e:
                # If the error is in a specific set, there's no need to retry
                if e.code in self.FATAL_ERRORS:
                    raise
                log.error("Error: %s; retrying after %.3f seconds", e,
                    timer.delay)
                timer.sleep()
            except IOError, e:
                # From conary.repository.transport
                if e.args[0] == 'socket error':
                    timer.sleep()
                    continue
                if e.args[0] == 'http error':
                    code, msg = e.args[1:3]
                else:
                    code, msg = e.args[0:2]
                raise TransportError(
                    "Unable to download: %s: %s" % (code, msg),
                    code=code, msg=msg, url = url), None, sys.exc_info()[2]
        exc_info = sys.exc_info()
        if isinstance(e, IOError):
            raise TransportError("Unable to download: %s" % e), None, exc_info[2]
        raise exc_info[0], exc_info[1], exc_info[2]

class Transport(transport.Transport):
    def parse_response(self, file):
        # Conary's transport assumes the response is a list inside a tuple
        ret = transport.Transport.parse_response(self, file)
        return ([ ret ], )

    def request(self, *args, **kwargs):
        ret = transport.Transport.request(self, *args, **kwargs)
        return ret[0][1]
