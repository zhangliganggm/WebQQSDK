#coding=UTF8

import basemsg

class GroupMsg(basemsg.BaseMsg):
    """
    self.group: entity.group.Group实例,发送者所在的群
    self.groupMember : entity.groupmember.GroupMember实例,发送者
    """

    def __init__(self):

        super(GroupMsg, self).__init__()

        self.group = None
        self.groupMember = None
        self.fontStyle = None

