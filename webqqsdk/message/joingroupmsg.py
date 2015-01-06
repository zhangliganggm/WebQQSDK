#coding=UTF8
import basemsg
BaseMsg = basemsg.BaseMsg
class JoinGroupMsg(BaseMsg):
    """
    有人申请加群，只有管理员才能收到此消息
    self.group : Group实例
    self.uin : int
    self.ip : int
    """

    def __init__(self):

        super(JoinGroupMsg, self).__init__()

        self.group = None
        self.uin = None
        self.ip = 0
