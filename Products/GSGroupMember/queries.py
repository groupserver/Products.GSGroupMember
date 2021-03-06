# coding=utf-8
import sqlalchemy as sa
from gs.database import getTable, getSession

import logging
log = logging.getLogger("GroupMemberQuery") #@UndefinedVariable

class GroupMemberQuery(object):
    def __init__(self, da=None):
        self.userInvitationTable = getTable('user_group_member_invitation')

    def get_count_current_invitations_in_group(self, siteId, groupId, userId):
        uit = self.userInvitationTable
        cols = [sa.func.count(uit.c.invitation_id.distinct())]
        s = sa.select(cols)
        s.append_whereclause(uit.c.site_id == siteId)
        s.append_whereclause(uit.c.group_id == groupId)
        s.append_whereclause(uit.c.user_id == userId)
        s.append_whereclause(uit.c.withdrawn_date == None)
        s.append_whereclause(uit.c.response_date == None)

        session = getSession()
        r = session.execute(s)
        retval = r.scalar()
        if retval == None:
            retval = 0
        assert retval >= 0
        return retval

    def get_invited_members(self, siteId, groupId):
        assert siteId
        assert groupId
        uit = self.userInvitationTable
        s = sa.select([uit.c.user_id.distinct()])
        s.append_whereclause(uit.c.site_id == siteId)
        s.append_whereclause(uit.c.group_id == groupId)
        s.append_whereclause(uit.c.withdrawn_date == None)
        s.append_whereclause(uit.c.response_date == None)
        
        session = getSession()
        r = session.execute(s)
        retval = []
        if r.rowcount:
            retval = [ x['user_id'] for x in r ]
        assert type(retval) == list
        return retval

