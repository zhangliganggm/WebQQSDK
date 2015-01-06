#coding=UTF8
import basemsg
BaseMsg = basemsg.BaseMsg
class AddMeFriendMsg(BaseMsg):
    """
    self.uin : int
    self.qq : int
    self.allow : int,好友验证类型
            0 为对方已经添加你为好友，不需要你的同意
            1 为对方请求你的同意
    """

    def __init__(self):

        super(AddMeFriendMsg, self).__init__()
        self.uin = 0
        self.qq = 0
        self.allow = 0
