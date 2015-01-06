#coding=UTF8

class Group(object):
    """
        self.uin: int, 群临时号码
        self.qq: int, 群QQ号
        self.markName: string，备注
        self.code: int, 群code
        self.creator: GroupMember，群主
        self.createTime: int,群创建时间
        self.name: string, 群名
        self.mask: int, 群消息设置 0 接收并提醒，1 接收不提醒，2 不接受
        self.members: list<GroupMember>, 群成员
        self.memberCount: int, 群员人数
        self.level: int, 群等级
    """

    def __init__(self):
        
        self.uin = 0
        self.code = 0
        self.name = ""
        self.creator = None
        self.createTime = 0
        self.mask = 0 
        self.members = []
        self.memberCount = 0
        self.level = 0

    def _getMemberByUin(self,uin):
        """
        @param uin:群成员的临时号码
        @rtype: GroupMember
        请调用getMemberByUin，勿调用此方法获取群成员
        """
        for i in self.members:
            if i.uin == uin:
                return i
#
#        return self._getMemberByUin(self.uin, uin)
#
    def getMemberByUin(self, memberUin):
        """
        
        """

    def __getattr__(self,name):

        if "qq" == name:
            return self.getQQ(self.code)

    def getQQ(self,uin):
        """
        返回QQ号(int)
        """
