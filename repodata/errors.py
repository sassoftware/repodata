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
Errors specific to repomd module.
"""

__all__ = ('RepositoryError', 'DownloadError')

class RepositoryError(Exception):
    """
    Base exception for all repomd exceptions. This should never be
    expllicitly raised.
    """

class DownloadError(RepositoryError):
    "Error downloading content"
    def __init__(self, text, code = None, msg = None):
        RepositoryError.__init__(self, text)
        self.code = code
        self.msg = msg

class TransportError(DownloadError):
    def __init__(self, text, code = None, msg = None, url = None,
                 headers = None):
        DownloadError.__init__(self, text, code = code, msg = msg)
        self.headers = headers
        self.url = url
