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
