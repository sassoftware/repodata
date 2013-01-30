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


"""
Repository access module.
"""

__all__ = ('Repository',  )

import os
import gzip
import tempfile

from repodata import urlopener

from conary.lib import digestlib, util
from conary.lib.http import http_error

class Repository(object):
    """
    Access files from the repository.
    """
    URLOpenerFactory = urlopener.URLOpener
    TransportError = http_error.TransportError

    def __init__(self, repoUrl, proxyMap=None):
        self._repoUrl = repoUrl.rstrip('/')
        self._proxyMap = proxyMap
        self._opener = self.URLOpenerFactory(proxyMap=self._proxyMap)

    def get(self, fileName, computeShaDigest = False):
        """
        Download a file from the repository.
        @param fileName: relative path to file
        @type fileName: string
        @return open file instance
        """

        fobj = self._getTempFileObject()
        realUrl = self._getRealUrl(fileName)

        inf = self._opener.open(realUrl)
        if computeShaDigest:
            dig = digestlib.sha1()
        else:
            dig = None
        util.copyfileobj(inf, fobj, digest = dig)
        fobj.seek(0)

        if not os.path.basename(fileName).endswith('.gz'):
            return self.FileWrapper.create(fobj, dig)
        return self.FileWrapper.create(gzip.GzipFile(fileobj=fobj, mode="r"),
            dig)

    @classmethod
    def _getTempFileObject(cls):
        """
        Generate a tempory file object.
        @return file object
        """

        return tempfile.TemporaryFile(prefix='mdparse')

    def _getRealUrl(self, path):
        """
        @param path: relative path to repository file
        @type path: string
        @return full repository url
        """

        return "%s/%s" % (self._repoUrl, path.lstrip('/'))

    class FileWrapper(object):
        __slots__ = [ 'file', 'sha1sum' ]

        def __init__(self, file, sha1sum):
            self.file = file
            self.sha1sum = sha1sum

        def read(self, size=-1):
            return self.file.read(size)

        def seek(self, offset, whence=0):
            return self.file.seek(offset, whence)

        def tell(self):
            return self.file.tell()

        def close(self):
            return self.file.close()

        @classmethod
        def create(cls, file, digestobj):
            if digestobj is None:
                return file
            return cls(file, digestobj.hexdigest())
