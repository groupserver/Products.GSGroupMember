# coding=utf-8
from AccessControl import ModuleSecurityInfo
from AccessControl import allow_class

groupmembership_security = ModuleSecurityInfo('Products.GSGroupMember.groupmembership')
groupmembership_security.declarePublic('get_group_users')
groupmembership_security.declarePublic('get_unverified_group_users')
groupmembership_security.declarePublic('join_group')
groupmembership_security.declarePublic('user_member_of_group')

