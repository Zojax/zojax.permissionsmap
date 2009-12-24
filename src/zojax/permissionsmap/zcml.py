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
""" zcml directive

$Id$
"""
from zope.component import globalregistry
from zope.component import getUtility, queryUtility, getUtilitiesFor

from zope import schema, interface, component
from zope.security.zcml import Permission
from zope.configuration.fields import Tokens, GlobalObject
from zope.configuration.exceptions import ConfigurationError
from zope.securitypolicy.interfaces import IRole

from interfaces import IPermissionsMap
from interfaces import IDefaultPermissionsMap
from permissionsmap import PermissionsMap


class IPermissionsMapDirective(interface.Interface):
    """ define permissions map directive"""

    name = schema.TextLine(
        title=u"Name",
        description=u"Permissions map identifier.",
        required=False)

    for_ = GlobalObject(
        title=u"For",
        required=False)

    title = schema.TextLine(
        title=u"Title",
        description=u"Permissions map title.",
        required=False)

    description = schema.TextLine(
        title=u"Description",
        description=u"Permissions map description.",
        required=False)

    override = schema.Bool(
        title=u"Override",
        description=u"Allow override sub directives for this declaration.",
        required=False,
        default=True)


class IGrantDirective(interface.Interface):

    role = Tokens(
        title=u"Role",
        description=u"Specifies the role.",
        required=True,
        value_type=schema.TextLine())

    permission = Tokens(
        title=u"Permission",
        description=u"Specifies the permission to be mapped.",
        required=True,
        value_type=Permission())


class IDenyDirective(interface.Interface):

    role = Tokens(
        title=u"Role",
        description=u"Specifies the role.",
        required=True,
        value_type=schema.TextLine())

    permission = Tokens(
        title=u"Permission",
        description=u"Specifies the permission to be mapped.",
        required=True,
        value_type=Permission())


class IUnsetDirective(interface.Interface):

    role = Tokens(
        title=u"Role",
        description=u"Specifies the role.",
        required=True,
        value_type=schema.TextLine())

    permission = Tokens(
        title=u"Permission",
        description=u"Specifies the permission to be mapped.",
        required=True,
        value_type=Permission())


class IGrantAllDirective(interface.Interface):

    permission = Tokens(
        title=u"Permission",
        description=u"Specifies the permission to be mapped.",
        required=True,
        value_type=Permission())


class IDenyAllDirective(interface.Interface):

    permission = Tokens(
        title=u"Permission",
        description=u"Specifies the permission to be mapped.",
        required=True,
        value_type=Permission())


class IUnsetAllDirective(interface.Interface):

    permission = Tokens(
        title=u"Permission",
        description=u"Specifies the permission to be mapped.",
        required=True,
        value_type=Permission())


class ClassPermissionsFactory(object):

    def __init__(self, permissionsmap):
        self.permissionsmap = permissionsmap

    def __call__(self, context):
        return self.permissionsmap

classPermissions = {}


def permissionsHandler(name, for_, title, description):
    # check if map already exists
    sm = globalregistry.globalSiteManager

    if for_ is not None:
        global classPermissions

        perms = classPermissions.get((for_, name))
        if perms is not None:
            return

        perms = PermissionsMap(name, title, description)
        classPermissions[(for_, name)] = perms
        interface.alsoProvides(perms, IDefaultPermissionsMap)

        # register map as adapter for for_
        factory = ClassPermissionsFactory(perms)
        sm.registerAdapter(factory, (for_,), IPermissionsMap, name)

    else:
        perms = sm.queryUtility(IPermissionsMap, name)
        if perms is not None:
            return

        # register map as utility
        perms = PermissionsMap(name, title, description)
        sm.registerUtility(perms, IPermissionsMap, name)


def directiveHandler(name, method, permissions, roles, for_=None, check=False):
    sm = globalregistry.globalSiteManager

    if for_ is not None:
        permissionmap = classPermissions[(for_, name)]
    else:
        permissionmap = sm.getUtility(IPermissionsMap, name)

    for role in roles:
        for permission in permissions:
            if not check:
                getattr(permissionmap, method)(permission, role, False)
            else:
                getattr(permissionmap, method)(permission, role)


def directiveHandlerAll(name, method, permissions, attr, for_=None):
    sm = globalregistry.globalSiteManager

    if for_ is not None:
        permissionmap = classPermissions[(for_, name)]
    else:
        permissionmap = sm.getUtility(IPermissionsMap, name)

    if attr == 'unsetall':
        for role_id, role in getUtilitiesFor(IRole):
            for permission in permissions:
                getattr(permissionmap, method)(permission, role_id)
    else:
        lst = getattr(permissionmap, attr)
        for permission in permissions:
            if permission not in lst:
                lst.append(permission)


class permissionsMapDirective(object):

    def __init__(self, _context, name=None, for_=None,
                 title='', description='', override=True):

        if for_ is None and not name:
            raise ConfigurationError(
                "'for' or 'name' should be provided for permissionsmap declaration")

        if not name:
            name = '__default_class__'

        self.for_ = for_
        self.name = name
        self.override = override

        _context.action(
            discriminator = self.discriminator(('zojax.permissions', name)),
            callable = permissionsHandler,
            args = (name, for_, title, description))

    def discriminator(self, data):
        if self.override:
            data = data + (object(),)
        return data

    def grant(self, _context, role, permission):
        _context.action(
            discriminator = self.discriminator(
                ('zojax.permissions.grant',
                 self.name, self.for_, tuple(role), tuple(permission))),
            callable = directiveHandler,
            args = (self.name, 'grantPermissionToRole',
                    permission, role, self.for_))

    def deny(self, _context, role, permission):
        _context.action(
            discriminator = self.discriminator(
                ('zojax.permissions.deny',
                 self.name, self.for_, tuple(role), tuple(permission))),
            callable = directiveHandler,
            args = (self.name, 'denyPermissionToRole',
                    permission, role, self.for_))

    def unset(self, _context, role, permission):
        _context.action(
            discriminator = self.discriminator(
                ('zojax.permissions.unset',
                 self.name, self.for_, tuple(role), tuple(permission))),
            callable = directiveHandler,
            args = (self.name, 'unsetPermissionFromRole',
                    permission, role, self.for_, True))

    def grantAll(self, _context, permission):
        _context.action(
            discriminator = self.discriminator(
                ('zojax.permissions.grantAll',
                 self.name, self.for_, tuple(permission))),
            callable = directiveHandlerAll,
            args = (self.name, 'grantPermissionToRole',
                    permission, 'grantall', self.for_))

    def denyAll(self, _context, permission):
        _context.action(
            discriminator = self.discriminator(
                ('zojax.permissions.denyAll',
                 self.name, self.for_, tuple(permission))),
            callable = directiveHandlerAll,
            args = (self.name, 'denyPermissionToRole',
                    permission, 'denyall', self.for_))

    def unsetAll(self, _context, permission):
        _context.action(
            discriminator = self.discriminator(
                ('zojax.permissions.unsetAll',
                 self.name, self.for_, tuple(permission))),
            callable = directiveHandlerAll,
            args = (self.name, 'unsetPermissionFromRole',
                    permission, 'unsetall', self.for_))
