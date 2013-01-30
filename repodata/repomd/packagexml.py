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
Module for parsing package sections of xml files from the repository metadata.
"""

__all__ = ('PackageXmlMixIn', )

import os

from rpath_xmllib import api1 as xmllib

from errors import UnknownElementError, UnknownAttributeError
from xmlcommon import SlotNode

class _Package(SlotNode):
    """
    Python representation of package section of xml files from the repository
    metadata.
    """

    # Yield this element when we're done parsing it
    WillYield = True

    # R0902 - Too many instance attributes
    # pylint: disable-msg=R0902

    __slots__ = ('name', 'arch', 'epoch', 'version', 'release',
                 'checksum', 'checksumType', 'summary', 'description',
                 'fileTimestamp', 'buildTimestamp', 'packageSize',
                 'installedSize', 'archiveSize', 'location', 'format',
                 'license', 'vendor', 'group', 'buildhost',
                 'sourcerpm', 'headerStart', 'headerEnd',
                 'licenseToConfirm', 'files', 'pkgid')

    # All attributes are defined in __init__ by iterating over __slots__,
    # this confuses pylint.
    # W0201 - Attribute $foo defined outside __init__
    # pylint: disable-msg=W0201


    def addChild(self, child):
        """
        Parse children of package element.
        """

        # R0912 - Too many branches
        # pylint: disable-msg=R0912

        # R0915 - Too many statements
        # pylint: disable-msg=R0915

        # E0203 - Access to member 'files' before its definition line 84
        # files is set to None by the superclasses __init__
        # pylint: disable-msg=E0203

        n = child.getName()
        if n == 'name':
            self.name = child.finalize()
        elif n == 'arch':
            self.arch = child.finalize()
        elif n == 'version':
            self.epoch = child.getAttribute('epoch')
            self.version = child.getAttribute('ver')
            self.release = child.getAttribute('rel')
        elif n == 'checksum':
            self.checksum = child.finalize()
            self.checksumType = child.getAttribute('type')
            if child.getAttribute('pkgid') == 'YES':
                self.pkgid = self.checksum
        elif n == 'summary':
            self.summary = child.finalize()
        elif n == 'description':
            self.description = child.finalize()
        elif n == 'packager':
            self.packager = child.finalize()
        elif n == 'url':
            self.url = child.finalize()
        elif n == 'time':
            self.fileTimestamp = child.getAttribute('file')
            self.buildTimestamp = child.getAttribute('build')
        elif n == 'size':
            self.packageSize = child.getAttribute('package')
            self.installedSize = child.getAttribute('installed')
            self.archiveSize = child.getAttribute('archive')
        elif n == 'location':
            self.location = child.getAttribute('href')
        elif n == 'file':
            if self.files is None:
                self.files = []
            self.files.append(
                _File(child.getText(), type=child.getAttribute('type')))
        elif child.getName() == 'format':
            self.format = []
            for node in child.iterChildren():
                nn = node.getName()
                if nn == 'rpm:license':
                    self.license = node.getText()
                elif nn == 'rpm:vendor':
                    self.vendor = node.getText()
                elif nn == 'rpm:group':
                    self.group = node.getText()
                elif nn == 'rpm:buildhost':
                    self.buildhost = node.getText()
                elif nn == 'rpm:sourcerpm':
                    self.sourcerpm = node.getText()
                elif nn == 'rpm:header-range':
                    self.headerStart = node.getAttribute('start')
                    self.headerEnd = node.getAttribute('end')
                elif nn in ('rpm:provides', 'rpm:requires',
                                        'rpm:obsoletes', 'rpm:recommends',
                                        'rpm:conflicts', 'suse:freshens',
                                        'rpm:enhances', 'rpm:supplements',
                                        'rpm:suggests', ):
                    self.format.append(node)
                elif nn == 'file':
                    pass
                else:
                    raise UnknownElementError(node)
        elif n == 'pkgfiles':
            pass
        elif n == 'suse:license-to-confirm':
            self.licenseToConfirm = child.finalize()
        else:
            raise UnknownElementError(child)

    def __repr__(self):
        if self.location is None:
            return "%s-%s-%s.%s.rpm" % (self.name, self.version, self.release,
                self.arch)
        return os.path.basename(self.location)

    def getNevra(self):
        """
        Return the name, epoch, version, release, and arch the package.
        """

        return (self.name, self.epoch, self.version, self.release, self.arch)

    def getConaryVersion(self):
        """
        Get the conary version of a source package.
        """

        assert self.arch == 'src'
        filename = os.path.basename(self.location)
        nameVerRelease = ".".join(filename.split(".")[:-2])
        ver = "_".join(nameVerRelease.split("-")[-2:])
        return ver

    def getFileName(self):
        """
        Returns the expected package file name.
        """

        return '%s-%s-%s.%s.rpm' % (self.name, self.version,
                                    self.release, self.arch)


class _RpmEntry(SlotNode):
    """
    Parse any element that contains rpm:entry or suse:entry elements.
    """

    __slots__ = ()

    def addChild(self, child):
        """
        Parse rpm:entry and suse:entry nodes.
        """

        if child.getName() in ('rpm:entry', 'suse:entry'):
            for attr, value in child.iterAttributes():
                if attr == 'kind':
                    child.kind = value
                elif attr == 'name':
                    child.name = value
                elif attr == 'epoch':
                    child.epoch = value
                elif attr == 'ver':
                    child.version = value
                elif attr == 'rel':
                    child.release = value
                elif attr == 'flags':
                    child.flags = value
                elif attr == 'pre':
                    child.pre = value
                else:
                    raise UnknownAttributeError(child, attr)
            SlotNode.addChild(self, child)
        else:
            raise UnknownElementError(child)


class _RpmEntries(SlotNode):
    """
    Class to represent all rpm:entry and suse:entry types.
    """

    __slots__ = ('kind', 'name', 'epoch', 'version', 'release', 'flags',
        'pre', )


class _RpmRequires(_RpmEntry):
    """
    Parse rpm:requires children.
    """

    __slots__ = ()


class _RpmRecommends(_RpmEntry):
    """
    Parse rpm:recommends children.
    """

    __slots__ = ()


class _RpmProvides(_RpmEntry):
    """
    Parse rpm:provides children.
    """

    __slots__ = ()


class _RpmObsoletes(_RpmEntry):
    """
    Parse rpm:obsoletes children.
    """

    __slots__ = ()


class _RpmConflicts(_RpmEntry):
    """
    Parse rpm:conflicts children.
    """

    __slots__ = ()


class _RpmEnhances(_RpmEntry):
    """
    Parse rpm:enhances children.
    """

    __slots__ = ()


class _RpmSupplements(_RpmEntry):
    """
    Parse rpm:supplements children.
    """

    __slots__ = ()


class _RpmSuggests(_RpmEntry):
    """
    Parse rpm:suggests children.
    """

    __slots__ = ()


class _SuseFreshens(_RpmEntry):
    """
    Parse suse:freshens children.
    """

    __slots__ = ()

class _File(object):
    "Representation of a file"
    __slots__ = ('type', 'name')
    def __init__(self, name, type=None):
        self.type = type
        self.name = name

    def __repr__(self):
        return self.name

class PackageXmlMixIn(object):
    """
    Handle registering all types for parsing package elements.
    """
    PackageFactory = _Package

    def _registerTypes(self):
        """
        Setup databinder to parse xml.
        """

        self._databinder.registerType(self.PackageFactory, name='package')
        self._databinder.registerType(xmllib.StringNode, name='name')
        self._databinder.registerType(xmllib.StringNode, name='arch')
        self._databinder.registerType(xmllib.StringNode, name='checksum')
        self._databinder.registerType(xmllib.StringNode, name='summary')
        self._databinder.registerType(xmllib.StringNode, name='description')
        self._databinder.registerType(xmllib.StringNode, name='url')
        self._databinder.registerType(_RpmEntries, name='entry',
                                      namespace='rpm')
        self._databinder.registerType(_RpmEntries, name='entry',
                                      namespace='suse')
        self._databinder.registerType(_RpmRequires, name='requires',
                                      namespace='rpm')
        self._databinder.registerType(_RpmRecommends, name='recommends',
                                      namespace='rpm')
        self._databinder.registerType(_RpmProvides, name='provides',
                                      namespace='rpm')
        self._databinder.registerType(_RpmObsoletes, name='obsoletes',
                                      namespace='rpm')
        self._databinder.registerType(_RpmConflicts, name='conflicts',
                                      namespace='rpm')
        self._databinder.registerType(_RpmEnhances, name='enhances',
                                      namespace='rpm')
        self._databinder.registerType(_RpmSupplements, name='supplements',
                                      namespace='rpm')
        self._databinder.registerType(_RpmSuggests, name='suggests',
                                      namespace='rpm')
        self._databinder.registerType(_SuseFreshens, name='freshens',
                                      namespace='suse')
        self._databinder.registerType(xmllib.StringNode,
                                      name='license-to-confirm',
                                      namespace='suse')
