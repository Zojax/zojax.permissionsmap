##############################################################################
#
# Copyright (c) 2009 Zope Foundation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
""" zojax.permissionsmap interfaces

$Id$
"""
from zope import schema, interface
from zope.component.interfaces import IObjectEvent


class UnknownPermissionsMap(Exception):
    """ Unknown permissions map """


class IPermissionsMap(interface.Interface):
    """ named IRolePermissionMap object """

    name = schema.TextLine(
        title=u"Name",
        description=u"Permissions map identifier.",
        required=True)

    title = schema.TextLine(
        title=u"Title",
        description=u"Permissions map title.",
        required=True)

    description = schema.TextLine(
        title=u"Description",
        description=u"Permissions map description.",
        required=False)


class IDefaultPermissionsMap(interface.Interface):
    """ marker interface for default class/interface permissions map """


class IObjectPermissionsMaps(interface.Interface):

    def get():
        """ return object permissions maps """


class IObjectPermissionsMapsManager(interface.Interface):

    def set(maps):
        """ set object permissions maps """


class IObjectPermissionsMapsModifiedEvent(IObjectEvent):
    """ object permissions maps modified """

    maps = interface.Attribute('Mew maps list')


class ObjectPermissionsMapsModifiedEvent(object):
    interface.implements(IObjectPermissionsMapsModifiedEvent)

    def __init__(self, object, maps):
        self.object = object
        self.maps = maps
