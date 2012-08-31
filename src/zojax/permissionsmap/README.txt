===============
Permissions map
===============

Package that allow group permissions and manage object grants by 
group. This package will only work with zojax.security securitypolicy.

Permissionsmap implements zcml directive `zope:permissions` that allow
manage permissions maps with zcml.

  >>> from zope import interface, component
  >>> from zope.interface.verify import verifyObject

  >>> import zojax.permissionsmap
  >>> from zojax.permissionsmap import interfaces, tests

  >>> from zope.configuration import xmlconfig
  >>> context = xmlconfig.file('meta.zcml', zojax.permissionsmap)

We can register new permissions maps with <zope:permissions /> directive,
We can use following subdirectives: grant, deny, unset, grantAll,
denyAll, unsetAll

  >>> context = xmlconfig.string("""
  ... <configure xmlns="http://namespaces.zope.org/zope">
  ...   <permissions name="myPermissions" title="My Permissions">
  ...     <unsetAll permission="my.p1" />
  ...     <unset permission="my.p1" role="r1" />
  ...     <grantAll permission="my.p1" />
  ...     <grant permission="my.p1" role="r1 r2 r3" />
  ...     <deny permission="my.p2" role="r1 r3" />
  ...     <denyAll permission="my.p3" />
  ...   </permissions>
  ... </configure>""", context)

  >>> permissions = component.getUtility(
  ...    interfaces.IPermissionsMap, 'myPermissions')

  >>> verifyObject(interfaces.IPermissionsMap, permissions)
  True

  >>> for p, settings in permissions.getPermissionsForRole('r1'):
  ...   print p, settings.getName()
  my.p1 Allow
  my.p3 Deny
  my.p2 Deny

  >>> for p, settings in permissions.getPermissionsForRole('r2'):
  ...   print p, settings.getName()
  my.p1 Allow
  my.p3 Deny

  >>> for p, settings in permissions.getPermissionsForRole('r3'):
  ...   print p, settings.getName()
  my.p1 Allow
  my.p3 Deny
  my.p2 Deny

We can add permissions later

  >>> context = xmlconfig.string("""
  ... <configure xmlns="http://namespaces.zope.org/zope">
  ...   <permissions name="myPermissions" title="My Permissions">
  ...     <unsetAll permission="my.p1" />
  ...   </permissions>
  ... </configure>""", context)


We can create permissions map for class or interface

  >>> context = xmlconfig.string("""
  ... <configure xmlns="http://namespaces.zope.org/zope">
  ...
  ...   <permissions for="zojax.permissionsmap.tests.TestContent1"
  ...        name="myPermissions1">
  ...
  ...     <grant permission="my.p1" role="r1 r2 r3" />
  ...     <deny permission="my.p2" role="r2" />
  ...     <denyAll permission="my.p3" />
  ...   </permissions>
  ... </configure>""", context)

  >>> content = tests.TestContent1()

  >>> perms = component.getAdapter(content, \
  ...     interfaces.IPermissionsMap, 'myPermissions1')

  >>> print perms.getPermissionsForRole('r1')
  [('my.p1', PermissionSetting: Allow), ('my.p3', PermissionSetting: Deny)]

We can define permissionsmap with same name and for multple times

  >>> context = xmlconfig.string("""
  ... <configure xmlns="http://namespaces.zope.org/zope">
  ...   <permissions for="zojax.permissionsmap.tests.TestContent1"
  ...        name="myPermissions1">
  ...     <deny permission="my.p2" role="r1" />
  ...   </permissions>
  ... </configure>""", context)

  >>> print perms.getPermissionsForRole('r1')
  [('my.p1', PermissionSetting: Allow), ('my.p3', PermissionSetting: Deny), ('my.p2', PermissionSetting: Deny)]

  >>> verifyObject(interfaces.IDefaultPermissionsMap, perms)
  True

We can create permissionsmap without name, but in this case '__default_class__'
name will be used.

  >>> context = xmlconfig.string("""
  ... <configure xmlns="http://namespaces.zope.org/zope">
  ...   <permissions for="zojax.permissionsmap.tests.TestContent1">
  ...     <grant permission="my.p1" role="r1 r2 r3" />
  ...     <deny permission="my.p2" role="r1 r3" />
  ...     <grantAll permission="my.p3" />
  ...   </permissions>
  ... </configure>""", context)

  >>> perms = component.getAdapter(content, \
  ...     interfaces.IPermissionsMap, '__default_class__')

  >>> verifyObject(interfaces.IDefaultPermissionsMap, perms)
  True

  >>> perms.getRolesForPermission('my.p3')
  [(u'r1', PermissionSetting: Allow), (u'r2', PermissionSetting: Allow), (u'r3', PermissionSetting: Allow)]

DenyAll is higher than GrantAll

  >>> context = xmlconfig.string("""
  ... <configure xmlns="http://namespaces.zope.org/zope">
  ...   <permissions for="zojax.permissionsmap.tests.TestContent1"
  ...        name="myPermissions1">
  ...     <denyAll permission="my.p3" />
  ...     <grantAll permission="my.p3" />
  ...   </permissions>
  ... </configure>""", context)

  >>> perms = component.getAdapter(
  ...     content, interfaces.IPermissionsMap, 'myPermissions1')

  >>> perms.getRolesForPermission('my.p3')
  [(u'r1', PermissionSetting: Deny), (u'r2', PermissionSetting: Deny), (u'r3', PermissionSetting: Deny)]

  >>> context = xmlconfig.string("""
  ... <configure xmlns="http://namespaces.zope.org/zope">
  ...
  ...   <permissions>
  ...     <grant permission="my.p1" role="r1 r2 r3" />
  ...     <deny permission="my.p2" role="r1 r3" />
  ...     <denyAll permission="my.p3" />
  ...   </permissions>
  ... </configure>""", context)
  Traceback (most recent call last):
  ...
  ZopeXMLConfigurationError: ...

We can assign permissions map to any annotatable content

  >>> from zope.annotation.interfaces import IAttributeAnnotatable
  >>> interface.directlyProvides(content, IAttributeAnnotatable)

  >>> objectmaps = interfaces.IObjectPermissionsMaps(content)
  >>> verifyObject(interfaces.IObjectPermissionsMaps, objectmaps)
  True

  >>> list(objectmaps.get())
  []

  >>> objectmanager = interfaces.IObjectPermissionsMapsManager(content)
  >>> verifyObject(interfaces.IObjectPermissionsMapsManager, objectmanager)
  True

We can assign any permissions map to object

  >>> objectmanager.set(('myPermissions',))

When we set permissions map we can get notification

  >>> from zope.component.eventtesting import getEvents
  >>> event = getEvents()[-1]
  >>> interfaces.IObjectPermissionsMapsModifiedEvent.providedBy(event)
  True

  >>> event.object is content
  True

  >>> event.maps
  ('myPermissions',)

Now we can get object permissions map

  >>> objectmaps = interfaces.IObjectPermissionsMaps(content)
  >>> list(objectmaps.get())
  [PermissionsMap(u'myPermissions')]

To remove permissions maps simply set empty tuple

  >>> objectmanager.set(())
  >>> objectmaps = interfaces.IObjectPermissionsMaps(content)
  >>> list(objectmaps.get())
  []

We can't set unregistered permissions maps

  >>> objectmanager.set(('unknown',))
  Traceback (most recent call last):
  ...
  UnknownPermissionsMap: ...


PermissionsMap access
---------------------

  >>> from zope.securitypolicy.interfaces import IRolePermissionMap
  >>> map = component.getAdapter(content, IRolePermissionMap, 'zojax.permissionsmap')
  >>> map.getPermissionsForRole('r1')
  [('my.p1', PermissionSetting: Allow), ('my.p3', PermissionSetting: Deny), ('my.p2', PermissionSetting: Deny)]

  >>> map.getRolesForPermission('my.p3')
  [(u'r1', PermissionSetting: Deny), (u'r2', PermissionSetting: Deny), (u'r3', PermissionSetting: Deny)]

  >>> context = xmlconfig.string("""
  ... <configure xmlns="http://namespaces.zope.org/zope">
  ...   <permissions name="myPermissions1">
  ...     <grant permission="my.p1" role="r1 r2 r3" />
  ...     <deny permission="my.p2" role="r1 r3" />
  ...     <denyAll permission="my.p3" />
  ...   </permissions>
  ...   <permissions name="myPermissions2" title="My Permissions2">
  ...     <grant permission="my.p3" role="r1" />
  ...     <grant permission="my.p2" role="r2" />
  ...   </permissions>
  ... </configure>""", context)

  >>> objectmanager = interfaces.IObjectPermissionsMapsManager(content)
  >>> objectmanager.set(('myPermissions2', 'myPermissions1'))

  >>> map = component.getAdapter(
  ...     content, IRolePermissionMap, 'zojax.permissionsmap')
  >>> map.getPermissionsForRole('r1')
  [('my.p1', PermissionSetting: Allow), ('my.p3', PermissionSetting: Allow), ('my.p2', PermissionSetting: Deny)]

  >>> map.getRolesForPermission('my.p3')
  [(u'r1', PermissionSetting: Allow), (u'r2', PermissionSetting: Deny), (u'r3', PermissionSetting: Deny)]

getSetting and getRolesAndPermissions methods are not implemented

  >>> map.getSetting('', '')
  ()

  >>> map.getRolesAndPermissions()
  ()



PermissionsMap permissions inheritance
--------------------------------------

#  >>> from zope import interface, component
#  >>> from zope.interface.verify import verifyObject#

#  >>> import zojax.permissionsmap
#  >>> from zojax.permissionsmap import interfaces, tests
#  >>> from zope.configuration import xmlconfig

#  >>> context = xmlconfig.file('meta.zcml', zojax.permissionsmap)
   >>> from zojax.permissionsmap.manager import PermissionsMapManager


#  >>> xmlconfig._clearContext()



#  >>> context = xmlconfig.string("""
#  ... <configure xmlns="http://namespaces.zope.org/zope">

#  ...   <permissions name="myPermissions1">
#  ...     <grant permission="my.p2" role="r2" />
#  ...   </permissions>
#  ...
#  ...   <permissions name="myPermissions2">
#  ...     <grant permission="my.p3" role="r3" />
#  ...   </permissions>
#  ...
#  ...   <permissions name="myPermissions3">
#  ...
#  ...     <grant permission="my.p3" role="r3" />
#  ...   </permissions>
#  ... </configure>""")


#  >>> map = component.getAdapter(
#  ...     content, IRolePermissionMap, 'zojax.permissionsmap')

#  >>> tc1 = tests.TestContent1()
#  >>> interface.directlyProvides(tc1, IAttributeAnnotatable)
#  >>> objectmanager = interfaces.IObjectPermissionsMapsManager(tc1)
#  >>> objectmanager.set(('myPermissions1',))

#  >>> tc2 = tests.TestContent2()
#  >>> tc2.__parent__ = tc1
#  >>> interface.directlyProvides(tc2, IAttributeAnnotatable)
#  >>> objectmanager = interfaces.IObjectPermissionsMapsManager(tc2)
#  >>> objectmanager.set(('myPermissions2',))


#  >>> content = tests.TestContent3()
#  >>> interface.directlyProvides(content, IAttributeAnnotatable)
#  >>> objectmanager = interfaces.IObjectPermissionsMapsManager(content)
#  >>> objectmanager.set(('myPermissions3',))

#  >>> content.__parent__ = tc2
#  >>> perms = component.getAdapter(content, interfaces.IPermissionsMap, 'myPermissions3')

#  >>> map3 = component.getAdapter(content, IRolePermissionMap, 'zojax.permissionsmap')
#  >>> map2 = component.getAdapter(tc2, IRolePermissionMap, 'zojax.permissionsmap')
#  >>> map1 = component.getAdapter(tc1, IRolePermissionMap, 'zojax.permissionsmap')

