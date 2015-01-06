#coding=UTF8
import basemsg
BaseMsg = basemsg.BaseMsg

class FriendMsg(BaseMsg):
    """
    self.friend : Friend实例
    """

    def __init__(self):

        super(FriendMsg, self).__init__()
        self.friend = None
        self.fontStyle = None



