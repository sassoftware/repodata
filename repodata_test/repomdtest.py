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


import os
from testrunner import testhelp
from repodata import errors
from repodata import repomd
from repodata_test import resources


class BaseTest(testhelp.TestCase):
    class Response(object):
        def __init__(self, path):
            self.path = path

            archivePath = resources.get_archive()
            f = file(os.path.join(archivePath, self.path))
            self.read = f.read

    def setUp(self):
        testhelp.TestCase.setUp(self)
        self.archivePath = resources.get_archive()

    def getRepositoryUrl(self, label):
        return 'file://%s/%s' % (self.archivePath, label)

class RepoMDTest(BaseTest):
    def testGetPrimaryDetail(self):
        url = self.getRepositoryUrl('suse-1')
        client = repomd.Client(url)
        pri = client.getPrimaryDetail()
        self.failUnlessEqual(pri.checksum,
            '6b5cb12e54b9262f230726db3652b1ef7f7de7da')
        self.failUnlessEqual(pri.checksumType, 'sha')
        self.failUnlessEqual(pri.timestamp, 1274094576)

    def testGetPackageDetail(self):
        url = self.getRepositoryUrl('suse-1')
        client = repomd.Client(url)
        pkgs = client.getPackageDetail()
        pkgs = [ x for x in pkgs ]
        checksums = [
            'f57a2832c587643e7ee89c9581c8e5819eaf0d16',
            '0d519e1d7d455352525b40f8e21db563decc15c3',
        ]
        self.failUnlessEqual([ x.pkgid for x in pkgs ], checksums)
        self.failUnlessEqual([ x.checksum for x in pkgs ], checksums)
        self.failUnlessEqual([ x.checksumType for x in pkgs ], ['sha', 'sha'])

    def testGetFileInfoDetail(self):
        url = self.getRepositoryUrl('suse-1')
        client = repomd.Client(url)
        pkgs = client.getFileLists()
        pkgs = [ x for x in pkgs ]
        checksums = [
            'f57a2832c587643e7ee89c9581c8e5819eaf0d16',
            '0d519e1d7d455352525b40f8e21db563decc15c3',
        ]
        self.failUnlessEqual([ x.pkgid for x in pkgs ], checksums)
        self.failUnlessEqual([ [ y.name for y in x.files ] for x in pkgs ],
            [
                [
                    '/etc/init.d/arpwatch',
                    '/usr/sbin/arpsnmp',
                    '/usr/sbin/arpwatch',
                    '/usr/sbin/rcarpwatch',
                    '/usr/share/doc/packages/arpwatch/CHANGES',
                    '/usr/share/doc/packages/arpwatch/FILES',
                    '/usr/share/doc/packages/arpwatch/INSTALL',
                    '/usr/share/doc/packages/arpwatch/README',
                    '/usr/share/doc/packages/arpwatch/missingcodes.txt',
                    '/usr/share/man/man8/arpsnmp.8.gz',
                    '/usr/share/man/man8/arpwatch.8.gz',
                    '/var/adm/fillup-templates/sysconfig.arpwatch',
                    '/usr/share/doc/packages/arpwatch',
                    '/var/lib/arpwatch',
                ],
                [
                    '/usr/bin/3Ddiag',
                    '/usr/bin/3Ddiag-result',
                    '/usr/bin/3Ddiag.devel',
                    '/usr/bin/3Ddiag.dri',
                    '/usr/bin/3Ddiag.ignoredb',
                    '/usr/bin/3Ddiag.nvidia_glx',
                    '/usr/bin/3Ddiag.runtime',
                    '/usr/bin/3dinfo',
                    '/usr/bin/switch2nv',
                    '/usr/bin/switch2nvidia',
                    '/usr/share/doc/packages/3ddiag/LICENSE',
                    '/usr/share/doc/packages/3ddiag',
                ]
            ])
        self.failUnlessEqual([ [ y.type for y in x.files ] for x in pkgs ],
            [
                [None] * 12 + [ 'dir', 'dir'],
                [None] * 11 + [ 'dir'],
            ])

    def testGetUpdateInfo(self):
        url = self.getRepositoryUrl('suse-1')
        client = repomd.Client(url)
        info = client.getUpdateInfo()

        info = [ x for x in info ]

        self.failUnlessEqual([ x.title for x in info ],
            [
                'Recommended update for release-notes-sles',
                'Security update for lcms',
                'Security update for curl',
                'Security update for Ghostscript',
            ])

    def testGetPatchDetail(self):
        url = self.getRepositoryUrl('suse-1')
        client = repomd.Client(url)
        info = client.getPatchDetail()

        info = [ x for x in info ]

        self.failUnlessEqual(len(info), 2)
        self.failUnlessEqual(info[0].description, """\
- #545668: wrong version of tomcat / mx4j in SDK migration
  catalog for SP3
""")
        # We don't test the second description, it's too large

    def testDownload(self):
        # Test that file downloads work. We extrapolate that package downloads
        # work too.
        url = self.getRepositoryUrl('suse-1')
        client = repomd.Client(url)
        fobj = client.download('repodata/repomd.xml')
        fobj.seek(0, 2)
        self.failUnlessEqual(fobj.tell(), 1180)
        self.failIf(hasattr(fobj, 'sha1sum'))

        fobj = client.download('repodata/repomd.xml', computeShaDigest=True)
        # test read() method of fileWrapper
        data = fobj.read(10)
        self.failUnlessEqual(len(data), 10)

        fobj.seek(0, 2)
        self.failUnlessEqual(fobj.tell(), 1180)
        self.failUnlessEqual(fobj.sha1sum,
            '35e108ee39635bd35cdd0793cb22c9b1c8374857')


    def testDownloadFailed(self):
        url = self.getRepositoryUrl('suse-1')
        client = repomd.Client(url)
        e = self.failUnlessRaises(errors.TransportError,
            client.download, 'blahblah')
        assert 'No such file or directory' in str(e)

    def skipTestDownloadThroughProxy(self):
        from conary.repository import transport as conarytransport
        def mockedUrlopen(slf, fullurl, data=None):
            fname = "suse-1/repodata/repomd.xml"
            return self.Response(fname)
        self.mock(conarytransport.URLOpener, "open", mockedUrlopen)

        url = "http://blah"
        proxies = dict(http="http://blah1", https="https://blah2")
        client = repomd.Client(url, proxies)
        client.download("blahblah")
