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

"""
Repository access module.
"""

__all__ = ('Repository',  )

import os
import gzip
import sys
import tempfile

from repodata import urlopener

from repodata.repomd import errors
from conary.lib import digestlib, util

class Repository(object):
    """
    Access files from the repository.
    """
    URLOpenerFactory = urlopener.URLOpener
    TransportError = urlopener.errors.TransportError

    def __init__(self, repoUrl, proxies=None):
        self._repoUrl = repoUrl.rstrip('/')
        self._proxies = proxies
        self._opener = self.URLOpenerFactory(self._proxies)

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
