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
from zope import interface, component
from zope.component import getAdapters
from zope.location.interfaces import ILocation
from zope.securitypolicy.interfaces import IRolePermissionMap

from interfaces import IPermissionsMap, IObjectPermissionsMaps


class PermissionsMapManager(object):
    component.adapts(ILocation)
    interface.implements(IRolePermissionMap)

    def __init__(self, context):
        perms = []
        # first get object permissionsmap
        supp = IObjectPermissionsMaps(context, None)
        if supp is not None:
            perms.extend(supp.get())

        for name, permissions in getAdapters((context,), IPermissionsMap):
        # then get adapted permissionsmap
            perms.append(permissions)

        self.perms = perms

        # collect parents permissionsmaps
        parent_perms = []
        if hasattr(context, '__parent__'):
            parent_context = context.__parent__
        else:
            parent_context = None
        while ILocation.providedBy(parent_context) and parent_context is not None:
            for name, permissions in getAdapters((parent_context,), IPermissionsMap):
                if permissions not in parent_perms:
                    parent_perms.append(permissions)
            parent_context = parent_context.__parent__

        self.parent_perms = parent_perms #tuple(reversed(parent_perms)) # Permissions are propagated in 'child -> parent' direction

    def getPermissionsForRole(self, role_id):
        permissions = {}

        for perm in self.perms:
            for permission, setting in perm.getPermissionsForRole(role_id):
                if permission not in permissions:
                    permissions[permission] = setting

        for perm in self.parent_perms: # inherit roles from parents of context
            for permission, setting in perm.getPermissionsForRole(role_id):
                if permission not in permissions: # check for permission duplicates, do not override them
                    permissions[permission] = setting

        return permissions.items()

    def getRolesForPermission(self, permission_id):
        """ check permissions in order """
        roles = {}

        for perm in self.perms: # apply roles defined for current context
            for role, setting in perm.getRolesForPermission(permission_id):
                if role not in roles:
                    roles[role] = setting

        for perm in self.parent_perms: # inherit roles from parents of context
            for role, setting in perm.getRolesForPermission(permission_id):
                if role not in roles: # check for role duplicates,do not them
                    roles[role] = setting

        return roles.items()

    def getSetting(self, permission_id, role_id):
        return ()

    def getRolesAndPermissions(self):
        return ()
