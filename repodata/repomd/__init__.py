#
# Copyright (c) 2008-2010 rPath, Inc.
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
Common repository metadata parsing library.

Handles parsing most yum metadata including SuSE proprietary patch/delta rpm
data.

NOTE: parsing of the following files is not implemented:
    * filelists.xml.gz
    * other.xml.gz
    * product.xml

Example:
> import repomd
> client = repomd.Client(url)
> patches = client.getPatchDetail()
> for patch in patches:
>     # print all of the advisories in the repository
>     print patch.description
"""

from repomdxml import RepoMdXml
from repository import Repository
# pyflakes=ignore
from errors import RepoMdError, ParseError, UnknownElementError, DownloadError

__all__ = ('Client', 'RepoMdError', 'ParseError', 'UnknownElementError',
    'DownloadError')

class Client(object):
    """
    Client object for extracting information from repository metadata.
    """

    RepositoryFactory = Repository
    RepoMdXmlFactory = RepoMdXml

    def __init__(self, repoUrl, proxies=None):
        self._repoUrl = repoUrl

        self._baseMdPath = '/repodata/repomd.xml'
        self._repo = self.RepositoryFactory(self._repoUrl, proxies)
        self._repomd = self.RepoMdXmlFactory(self._repo, self._baseMdPath).parse()

    def download(self, relativePath, computeShaDigest=False):
        """
        Download a file from the repository.
        @return file object
        """
        return self._repo.get(relativePath, computeShaDigest=computeShaDigest)

    def getRepos(self):
        """
        Get a repository instance.
        @return instance of repomd.repository.Repository
        """

        return self._repo

    def getPrimaryDetail(self):
        node = self._repomd.getRepoData('primary')
        return node

    def getPatchDetail(self):
        """
        Get a list instances representing all patch data in the repository.
        @return [repomd.patchxml._Patch, ...]
        """

        node = self._repomd.getRepoData('patches')

        if node is None:
            return []

        ret = []
        for sn in node.iterSubnodes():
            sn._parser._repository = self._repo
            ret.append(sn.parseChildren())
        return ret

    def getPackageDetail(self):
        """
        Get a list instances representing all packages in the repository.
        @ return [repomd.packagexml._Package, ...]
        """

        node = self._repomd.getRepoData('primary')
        return node.iterSubnodes()

    def getFileLists(self):
        """
        Get a list instances representing filelists in the repository.
        @ return [repomd.filelistsxml._Package, ...]
        """
        node = self._repomd.getRepoData('filelists')
        return node.iterSubnodes()

    def getUpdateInfo(self):
        """
        Get a list of instances representing the advisory infomration for
        all updates.
        @return [ repomd.userinfoxml._Update ]
        """

        node = self._repomd.getRepoData('updateinfo')

        if not node:
            return []

        return node.iterSubnodes()
