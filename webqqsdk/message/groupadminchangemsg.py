#coding=UTF8
import basemsg
BaseMsg = basemsg.BaseMsg

class GroupAdminChangeMsg(BaseMsg):
    """
    self.group : Group实例
    self.groupMember : GroupMember实例
    self.opType : int, 0 取消管理员，1 设置管理员
    """
    def __init__(self):

        super(GroupAdminChangeMsg, self).__init__()
        self.group = None
        self.groupMember = None
        self.opType = 0 # 0 取消管理员，1 设置管理员
