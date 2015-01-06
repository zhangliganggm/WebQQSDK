#coding=UTF8
import basemsg
BaseMsg = basemsg.BaseMsg
class LeaveGroupMsg(BaseMsg):
    """
    我被踢出群的消息
    self.groupUin： 群uin
    self.groupQQ： 群号
    self.adminUin：踢我的管理员uin
    self.adminNick：踢我的管理员昵称
    """

    def __init__(self):

        super(LeaveGroupMsg, self).__init__()

        self.groupUin = 0
        self.groupQQ = 0
        self.adminUin = 0
        self.adminNick = ""
