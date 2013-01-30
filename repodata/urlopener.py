#
# Copyright (c) SAS Institute Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
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

    def request(self, *args, **kwargs):
        ret = transport.Transport.request(self, *args, **kwargs)
        return ret[0]
