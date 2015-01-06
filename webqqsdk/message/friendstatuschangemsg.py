#coding=UTF8
import basemsg
BaseMsg = basemsg.BaseMsg
class FriendStatusChangeMsg(BaseMsg):
    """
    好友状态改变消息
    self.friend: Friend实例
    """

    def __init__(self):

        super(FriendStatusChangeMsg, self).__init__()

        self.friend = None
