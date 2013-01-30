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

__all__ = ('Client', 'RepoMdError', 'ParseError', 'UnknownElementError')

class Client(object):
    """
    Client object for extracting information from repository metadata.
    """

    RepositoryFactory = Repository
    RepoMdXmlFactory = RepoMdXml

    def __init__(self, repoUrl, proxyMap=None):
        self._repoUrl = repoUrl

        self._baseMdPath = '/repodata/repomd.xml'
        self._repo = self.RepositoryFactory(self._repoUrl, proxyMap)
        self._repomdXml = None

    @property
    def repomdXml(self):
        if self._repomdXml is None:
            self._repomdXml = self.RepoMdXmlFactory(self._repo, self._baseMdPath).parse()
        return self._repomdXml

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
        node = self.repomdXml.getRepoData('primary')
        return node

    def getPatchDetail(self):
        """
        Get a list instances representing all patch data in the repository.
        @return [repomd.patchxml._Patch, ...]
        """

        node = self.repomdXml.getRepoData('patches')

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

        node = self.repomdXml.getRepoData('primary')
        return node.iterSubnodes()

    def getFileLists(self):
        """
        Get a list instances representing filelists in the repository.
        @ return [repomd.filelistsxml._Package, ...]
        """
        node = self.repomdXml.getRepoData('filelists')
        return node.iterSubnodes()

    def getUpdateInfo(self):
        """
        Get a list of instances representing the advisory infomration for
        all updates.
        @return [ repomd.userinfoxml._Update ]
        """

        node = self.repomdXml.getRepoData('updateinfo')

        if not node:
            return []

        return node.iterSubnodes()
