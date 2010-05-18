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
Module for parsing primary.xml.gz from the repository metadata.
"""

__all__ = ('PrimaryXml', )

from packagexml import PackageXmlMixIn
from errors import UnknownElementError
from xmlcommon import XmlStreamedParser, SlotNode

class _Metadata(SlotNode):
    """
    Python representation of primary.xml.gz from the repository metadata.
    """

    __slots__ = ()

    def addChild(self, child):
        """
        Parse children of metadata element.
        """

        if child.getName() != 'package':
            raise UnknownElementError(child)
        # We're not accumulating package data here, extract it from the
        # iterator instead

class PrimaryXml(XmlStreamedParser, PackageXmlMixIn):
    """
    Handle registering all types for parsing primary.xml.gz.
    """

    def _registerTypes(self):
        """
        Setup databinder to parse xml.
        """

        PackageXmlMixIn._registerTypes(self)
        self._databinder.registerType(_Metadata, name='metadata')
