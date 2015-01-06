#coding=UTF8
import basemsg
class TempMsg(basemsg.BaseMsg):
    """
    self.uin : int,发送者的uin
    self.qq : int,发送者的QQ
    self.ip : int, 发送者ip

    """

    def __init__(self):

        super(TempMsg, self).__init__()

        self.uin = 0
        self.qq = 0
        self.fontStyle = None
        self.ip = 0
