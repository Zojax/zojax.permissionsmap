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
""" zojax.permissionsmap tests

$Id$
"""
__docformat__ = "reStructuredText"

import unittest, doctest
from zope import interface
from zope.component import provideAdapter, provideUtility
from zope.app.testing import setup

from zope.securitypolicy.role import Role
from zope.security.permission import Permission
from zope.annotation.attribute import AttributeAnnotations
from zope.location.location import Location

from manager import PermissionsMapManager
from support import ObjectPermissionsMaps, ObjectPermissionsMapsManager


r1 = Role('r1', 'Role1')
r2 = Role('r2', 'Role2')
r3 = Role('r3', 'Role3')

p1 = Permission('my.p1')
p2 = Permission('my.p2')
p3 = Permission('my.p3')


class ITestContent1(interface.Interface):
    pass

class ITestContent2(interface.Interface):
    pass


class ITestContent3(interface.Interface):
    pass

class ITestContent4(interface.Interface):
    pass

class ITestContent5(interface.Interface):
    pass

class TestContent1(Location):
    interface.implements(ITestContent1)

class TestContent2(Location):
    interface.implements(ITestContent2)


class TestContent3(Location):
    interface.implements(ITestContent3)

class TestContent4(Location):
    interface.implements(ITestContent4)

class TestContent5(Location):
    interface.implements(ITestContent5)

#class TestContent


def setUp(test):
    setup.placelessSetUp()

    provideUtility(r1, name='r1')
    provideUtility(r2, name='r2')
    provideUtility(r3, name='r3')

    provideUtility(p1, name='my.p1')
    provideUtility(p2, name='my.p2')
    provideUtility(p3, name='my.p3')

    provideAdapter(AttributeAnnotations)
    provideAdapter(ObjectPermissionsMaps)
    provideAdapter(ObjectPermissionsMapsManager)
    provideAdapter(PermissionsMapManager,
                   (interface.Interface,), name='zojax.permissionsmap')

def tearDown(test):
    setup.placelessTearDown()


def test_suite():
    return unittest.TestSuite((
            doctest.DocFileSuite(
                'README.txt',
                setUp=setUp, tearDown=tearDown,
                optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS),
            ))
