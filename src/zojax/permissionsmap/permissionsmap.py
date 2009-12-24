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
from zope import interface
from zope.component import getUtilitiesFor
from zope.securitypolicy.interfaces import IRole
from zope.securitypolicy.interfaces import Allow, Deny, Unset
from zope.securitypolicy.securitymap import PersistentSecurityMap
from zope.securitypolicy.rolepermission import RolePermissionManager

from interfaces import IPermissionsMap


class PermissionsMap(PersistentSecurityMap, RolePermissionManager):
    interface.implements(IPermissionsMap)

    def __init__(self, name, title, description=''):
        super(PermissionsMap, self).__init__()
        self.name = name
        self.title = title
        self.description = description

        self.denyall = []
        self.grantall = []

    def __repr__(self):
        return 'PermissionsMap(%r)' % self.name

    def getPermissionsForRole(self, role_id):
        settings = {}

        if self.grantall:
            settings.update(
                [(pid, Allow) for pid in self.grantall])

        if self.denyall:
            settings.update(
                [(pid, Deny) for pid in self.denyall])

        if settings:
            settings.update(
                [(pid, setting) for pid, setting in \
                     super(PermissionsMap,self).getPermissionsForRole(role_id)])

            return settings.items()

        else:
            return super(PermissionsMap, self).getPermissionsForRole(role_id)

    def getRolesForPermission(self, permission_id):
        all = None

        if permission_id in self.denyall:
            all = Deny
        elif permission_id in self.grantall:
            all = Allow

        if all is not None:
            settings = dict(
                [(id, all) for id, role in getUtilitiesFor(IRole)])

            settings.update(
                [(rid, setting) for rid, setting in \
                     super(PermissionsMap, self).getRolesForPermission(
                        permission_id)])

            return settings.items()
        else:
            return super(PermissionsMap, self).getRolesForPermission(permission_id)
