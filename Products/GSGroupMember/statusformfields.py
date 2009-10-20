# coding=utf-8
import AccessControl
from zope.app.apidoc import interface
from zope.component import createObject, adapts
from zope.interface import implements
from zope.formlib import form
from zope.schema import *

from Products.CustomUserFolder.interfaces import IGSUserInfo

from groupmembershipstatus import GSGroupMembershipStatus
from interfaces import IGSStatusFormFields, IGSGroupMembershipStatus,\
  IGSMemberActionsSchema

MAX_POSTING_MEMBERS = 5

class GSStatusFormFields(object):
    adapts(IGSGroupMembershipStatus)
    implements(IGSStatusFormFields)

    def __init__(self, status):
        assert IGSGroupMembershipStatus.providedBy(status),\
          u'%s is not a GSGroupMembershipStatus' % status
        
        self.status = status
        self.userInfo = status.userInfo
        self.groupInfo = status.groupInfo
        self.siteInfo = status.siteInfo
        
        self.__adminUserInfo = None
        self.__adminUserStatus = None
        
        self.__groupAdmin = None
        self.__moderator = None
        self.__moderate = None
        self.__postingMember = None
        self.__remove = None
        
        self.__allFields = None
        self.__validFields = None
        self.__form_fields = None
    
    @property
    def adminUserInfo(self):
        if self.__adminUserInfo == None:
            self.__adminUserInfo = \
              createObject('groupserver.LoggedInUser', 
                           self.groupInfo.groupObj)
        return self.__adminUserInfo
    
    @property
    def adminUserStatus(self):
        if self.__adminUserStatus == None:
            self.__adminUserStatus = \
              GSGroupMembershipStatus(self.adminUserInfo,
                self.groupInfo, self.siteInfo)
        return self.__adminUserStatus
    
    @property
    def allFields(self):
        if self.__allFields == None:
            self.__allFields = [
              self.groupAdmin,
              self.moderator,
              self.moderate,
              self.postingMember,
              self.remove
            ]
        return self.__allFields
    
    @property
    def validFields(self):
        if self.__validFields == None:
            self.__validFields = \
              filter(None, self.allFields)
        return self.__validFields
        
    @property
    def form_fields(self):
        if self.__form_fields == None:
            fields = \
              form.Fields(IGSMemberActionsSchema)
            for f in self.validFields:
                fields = \
                  form.Fields(
                    fields
                    +
                    form.Fields(f)
                  )
            self.__form_fields = fields.omit('dummy')
        return self.__form_fields
        
    @property
    def groupAdmin(self):
        if self.__groupAdmin == None:
            self.__groupAdmin = False
            if (self.status.isNormalMember or \
                self.status.isPtnCoach or \
                self.status.isModerator) and not self.status.isOddlyConfigured:
                self.__groupAdmin = \
                  Bool(__name__=u'%s_groupAdmin' % self.userInfo.id,
                    title=u'Make %s a Group Administrator' % self.userInfo.name,
                    description=u'Make %s a Group Administrator' % self.userInfo.name,
                    required=False)
            elif self.status.isGroupAdmin and self.adminUserStatus.isSiteAdmin:
                self.__groupAdmin = \
                  Bool(__name__=u'%s_groupAdmin' % self.userInfo.id,
                    title=u'Revoke the Group Administrator privileges '\
                      u'from %s' % self.userInfo.name,
                    description=u'Revoke the Group Administrator privileges '\
                      u'from %s' % self.userInfo.name,
                    required=False)
        return self.__groupAdmin
              
    @property
    def moderator(self):
        if self.__moderator == None:
            self.__moderator = False
            if self.status.groupIsModerated and not \
              (self.status.isModerator or \
               self.status.isModerated or \
               self.status.isInvited or \
               self.status.isUnverified or \
               self.status.isOddlyConfigured):
                self.__moderator =\
                  Bool(__name__=u'%s_moderator' % self.userInfo.id,
                    title=u'Make %s a Moderator for this group' %\
                      self.userInfo.name,
                    description=u'Make %s a Moderator for this group' %\
                      self.userInfo.name,
                    required=False)
            elif self.status.groupIsModerated and self.status.isModerator:
                self.__moderator =\
                  Bool(__name__=u'%s_moderator' % self.userInfo.id,
                    title=u'Revoke moderator status from %s' %\
                      self.userInfo.name,
                    description=u'Revoke moderator status from %s' %\
                      self.userInfo.name,
                    required=False)
        return self.__moderator
                  
    @property
    def moderate(self):
        if self.__moderate == None:
            self.__moderate = False
            if self.status.groupIsModerated and self.status.isNormalMember:
                self.__moderate =\
                  Bool(__name__=u'%s_moderate' % self.userInfo.id,
                    title=u'Start moderating messages from %s' %\
                      self.userInfo.name,
                    description=u'Start moderating messages from %s' %\
                      self.userInfo.name,
                    required=False)
            elif self.status.groupIsModerated and self.status.isModerated:
                self.__moderate =\
                  Bool(__name__=u'%s_moderate' % self.userInfo.id,
                    title=u'Stop moderating messages from %s' %\
                      self.userInfo.name,
                    description=u'Stop moderating messages from %s' %\
                      self.userInfo.name,
                    required=False)
        return self.__moderate         
    
    @property
    def postingMember(self):
        if self.__postingMember == None:
            self.__postingMember = False
            if self.status.postingIsSpecial and \
              (self.status.numPostingMembers < MAX_POSTING_MEMBERS) and \
              not (self.status.isPostingMember or \
                   self.status.isUnverified or \
                   self.status.isOddlyConfigured): 
                self.__postingMember =\
                  Bool(__name__=u'%s_postingMember' % self.userInfo.id,
                    title=u'Make %s a posting member' %\
                      self.userInfo.name,
                    description=u'Make %s a posting member' %\
                      self.userInfo.name,
                    required=False)
            elif self.status.postingIsSpecial and self.status.isPostingMember:
                self.__postingMember =\
                  Bool(__name__=u'%s_postingMember' % self.userInfo.id,
                    title=u'Revoke the ability to post from %s' %\
                      self.userInfo.name,
                    description=u'Revoke the ability to post from %s' %\
                      self.userInfo.name,
                    required=False)
        return self.__postingMember
    
    @property
    def remove(self):
        if self.__remove == None:
            self.__remove = False
            if not self.status.isSiteAdmin and \
              not(self.status.isGroupAdmin and \
                  self.adminUserStatus.isGroupAdmin):
                self.__remove =\
                  Bool(__name__=u'%s_remove' % self.userInfo.id,
                    title=u'Remove %s from the group' %\
                      self.userInfo.name,
                    description=u'Remove %s from the group' %\
                      self.userInfo.name,
                    required=False)
        return self.__remove
    
    