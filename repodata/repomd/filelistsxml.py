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
Module for parsing filelists.xml files from the repository metadata.
"""

__all__ = ('FilelistXml', )

from xmlcommon import XmlStreamedParser, SlotNode
from packagexml import PackageXmlMixIn, _Package

class _FileLists(SlotNode):
    """
    Python representation of filelists.xml from the repository metadata.
    """
    __slots__ = ()

class _PackageFL(_Package):
    __slots__ = ()

    def addChild(self, node):
        return _Package.addChild(self, node)

    def finalize(self):
        for attrName, attrVal in self._iterAttributes():
            if attrName == 'name':
                self.name = attrVal
            elif attrName == 'arch':
                self.arch = attrVal
            elif attrName == 'pkgid':
                self.pkgid = attrVal
        return self

class FileListsXml(XmlStreamedParser, PackageXmlMixIn):
    """
    Handle registering all types for parsing filelists.xml files.
    """

    def _registerTypes(self):
        """
        Setup databinder to parse xml.
        """

        PackageXmlMixIn._registerTypes(self)
        self._databinder.registerType(_PackageFL, name='package')
        self._databinder.registerType(_FileLists, name='filelists')
