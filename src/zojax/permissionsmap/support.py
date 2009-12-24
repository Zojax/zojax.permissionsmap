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
"""

$Id$
"""
from zope import event, interface, component
from zope.component import queryUtility
from zope.annotation.interfaces import IAnnotations, IAnnotatable

from interfaces import UnknownPermissionsMap
from interfaces import IPermissionsMap, ObjectPermissionsMapsModifiedEvent
from interfaces import IObjectPermissionsMaps, IObjectPermissionsMapsManager

KEY = 'zojax.permissionsmap'


class ObjectPermissionsMaps(object):
    component.adapts(IAnnotatable)
    interface.implements(IObjectPermissionsMaps)

    def __init__(self, context):
        annotations = IAnnotations(context)
        self.data = annotations.get(KEY, ())

    def get(self):
        perms = []
        for name in self.data:
            perm = queryUtility(IPermissionsMap, name=name)
            if perm is not None:
                yield perm


class ObjectPermissionsMapsManager(object):
    component.adapts(IAnnotatable)
    interface.implements(IObjectPermissionsMapsManager)

    def __init__(self, context):
        self.context = context
        self.annotations = IAnnotations(context)
        self.data = self.annotations.get(KEY, ())

    def set(self, perms):
        for name in perms:
            perm = queryUtility(IPermissionsMap, name=name)
            if perm is None:
                raise UnknownPermissionsMap(
                    "Undefined permissions map id", name)

        if perms:
            self.data = tuple(perms)
            self.annotations[KEY] = self.data
        else:
            if KEY in self.annotations:
                del self.annotations[KEY]

        event.notify(ObjectPermissionsMapsModifiedEvent(self.context, self.data))
