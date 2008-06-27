# coding=utf-8
from Products.Five import BrowserView
from zope.component import createObject
from Products.CustomUserFolder.userinfo import GSUserInfo
from queries import GroupMemberQuery

import logging
log = logging.getLogger('GSGroupMember')

class GSInviationsRespond(BrowserView):
    def __init__(self, context, request):
        self.context = context
        self.request = request
        self.siteInfo = createObject('groupserver.SiteInfo', context)
        self.groupsInfo = createObject('groupserver.GroupsInfo', context)
        self.userInfo = GSUserInfo(context)
        
        da = self.context.zsqlalchemy 
        assert da, 'No data-adaptor found'
        self.groupMemberQuery = GroupMemberQuery(da)
        
        self.__currentInvitations = None
        self.__pastInvitations = None

    @property
    def currentInvitations(self):
        if self.__currentInvitations == None:
            self.__currentInvitations = self.get_currentInvitations()
        assert type(self.__currentInvitations) == list
        return self.__currentInvitations
        
    def get_currentInvitations(self):
        m = u'Generating a list of current group-invitations for %s (%s) '\
          u'on %s (%s).' %\
            (self.userInfo.name, self.userInfo.id,
             self.siteInfo.name, self.siteInfo.id)
        log.info(m)
        
        invitations = self.groupMemberQuery.get_current_invitiations_for_site(
            self.siteInfo.id, self.userInfo.id)
        for inv in invitations:
            usrInf = createObject('groupserver.UserFromId', 
              self.context, inv['inviting_user_id'])
            inv['inviting_user'] = usrInf
            grpInf = createObject('groupserver.GroupInfo',
              self.groupsInfo.groupsObj, inv['group_id'])
            inv['group'] = grpInf
            
        assert type(invitations) == list
        return invitations

    def process_form(self):
        '''Process the forms in the page.
        
        This method uses the "submitted" pattern that is used for the
        XForms impementation on GroupServer. 
          * The method is called whenever the page is loaded by
            tal:define="result view/process_form".
          * The submitted form is checked for the hidden "submitted" field.
            This field is only returned if the user submitted the form,
            not when the page is loaded for the first time.
            - If the field is present, then the form is processed.
            - If the field is absent, then the method re  turns.
        
        RETURNS
            A "result" dictionary, that at-least contains the form that
            was submitted
        '''
        form = self.context.REQUEST.form
        result = {}
        result['form'] = form

        if form.has_key('submitted'):
            groupIds = [k.split('-respond')[0] for k in form.keys() 
              if  '-respond' in k]
            responses = [form['%s-respond' % k] for k in groupIds]          

            print responses

            accepted = [k.split('-accept')[0] for k in responses
              if '-accept' in k]
            print accepted
            acceptedGroups = [createObject('groupserver.GroupInfo',
              self.groupsInfo.groupsObj, g) for g in accepted]
              
            declined = [k.split('-decline')[0] for k in responses
              if '-decline' in k]
            print declined
            declinedGroups = [createObject('groupserver.GroupInfo',
              self.groupsInfo.groupsObj, g) for g in declined]
            
            am = ', '.join(['%s (%s)' % (g.name, g.id) 
                            for g in acceptedGroups])
            m = u'%s (%s) accepting invitations to join the groups '\
              u'%s on %s (%s)' % (self.userInfo.name, self.userInfo.id,
              am, self.siteInfo.name, self.siteInfo.id)
            log.info(m)
            
            dm = ', '.join(['%s (%s)' % (g.name, g.id) 
                            for g in declinedGroups])
            m = u'%s (%s) declining invitations to join the groups '\
              u'%s on %s (%s)' % (self.userInfo.name, self.userInfo.id,
              dm, self.siteInfo.name, self.siteInfo.id)
            log.info(m)

            result['error'] = False
            
            m = u''
            if accepted:
                acceptedLinks = ['<a href="%s">%s</a>' % (g.url, g.name)
                  for g in acceptedGroups]
                if len(acceptedLinks) > 1:
                    c = u', '.join([g for g in acceptedLinks][:-1])
                    a = u' and '.join((c, acceptedLinks[-1]))
                    i = 'invitations'
                    t = 'these groups'
                else:
                    a = acceptedLinks[0]
                    i = 'invitation'
                    t = 'this group'
                m = u'Accepted the %s to join %s. You are now a member of '\
                  u'%s.' % (i, a, t)
            else:
                m = u'You did not accept any invitations.'
            if declined:
                declinedLinks = ['<a href="%s">%s</a>' % (g.url, g.name)
                  for g in declinedGroups]
                if len(declinedLinks) > 1:
                    c = u', '.join([g for g in declinedLinks][:-1])
                    a = u' and '.join((c, declinedLinks[-1]))
                    i = 'invitations'
                else:
                    a = declinedLinks[0]
                    i = 'invitation'
                m = u'<ul><li>%s</li>'\
                  u'<li>Declined the %s to join %s.</li</ul>' %\
                  (m, i, a)
            else:
               m = u'<ul><li>%s</li>'\
                  u'<li>You did not decline any invitations.</li</ul>' % m

            result['message'] = m
            
            assert result.has_key('error')
            assert type(result['error']) == bool
            assert result.has_key('message')
            assert type(result['message']) == unicode
        
        assert result.has_key('form')
        assert type(result['form']) == dict
        return result


