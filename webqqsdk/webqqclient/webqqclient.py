#coding=UTF8
import sys
import thread
import threading
import time
import traceback
import os

__curpath = os.path.dirname(__file__)
__parpath = os.path.dirname(__curpath)
if not __parpath:
    __parpath = ".."
sys.path.append(__parpath)
import qqapi
import entity
import message
import msgevent
import utils
import eventlistener

EventListener = eventlistener.EventListener


class WebQQClient(qqapi.WebQQ,threading.Thread):
    """
    self.loginSucCount: int, 登录成功的次数
    """


    def __init__(self,qq,pwd):

        qqapi.WebQQ.__init__(self,qq,pwd)
        threading.Thread.__init__(self)
        self.logoutCodes = [121, 103, 108]
        self.getMsgFailedCount = 0
#        self.__msgPool = []
        # events 列表,每个元素都是个MsgEvent实例
 
        self.newMemberJoinGroupEvent = []
        self.groupAdminChangeEvents = []
        self.groupMsgEvents = []
        self.friendMsgEvents = []
        self.addMeFiendEvents = []
        self.logoutEvents = []
        self.loginFailedEvents = []
        self.loginSuccessEvents = []
        self.needVerifyCodeEvents = []
        self.tempMsgEvents = []
        self.errorMsgEvents = []
        self.leaveGroupEvents = []
        self.friendStatusChangeEvents = []
        self.logMsgEvents = []
        self.sendBuddyEvents = []
        self.sendGroupEvents = []

       # msgs 列表，每个元素都是个message实例
        self.__needVerifyCodeMsgs = []
        self.__loginSuccessMsgs = []
        self.__loginFailedMsgs = []
        self.__logoutMsgs = []
        self.__addMeFiendMsgs = []
        self.__friendMsgs = []
        self.__groupMsgs = []
        self.__groupAdminChangeMsgs = []
        self.__newMemberJoinGroupMsgs = []
        self.__tempMsgs = []
        self.__leaveGroupMsgs = []
        self.__friendStatusChangeMsgs = []

        # log消息

        self.__logMsgs = []
        self.__sendBuddyMsgs = []
        self.__sendGroupMsgs = []
        self.__errorMsgs = []

        #
        self.__qqNumbers = {} # key uin,qq
        self.__groupQQNumbers = {} # 同上

        self.__eventListen = True

        self.loginSucCount = 0 # 登录成功次数

        self.sendMsgFuncPool = []

        self.msgIds = [] # item 为元组(msg_id1, msg_id2)，用于保存已经收到过的msg
        self.msgIdsMaxNum = 50 # self.msgIds 最大容量，超出则pop(0)

        self.start()


    def uin2number(self,uin,type=1):
        """
        type 4:群
        """
        if type == 1:
            qqNumberDict = self.__qqNumbers
        elif type == 4:
            qqNumberDict = self.__groupQQNumbers
        else:
            return

        if qqNumberDict.has_key(uin):
            return qqNumberDict[uin]
        qq = super(WebQQClient,self).uin2number(uin,type)
            
        if qq:
            qqNumberDict[uin] = qq
        return qq

    def addErrorMsg(self,msg):

        self.__errorMsgs.append(msg)

    def addLogMsg(self,msgContent):

        logMsg = message.BaseMsg()
        logMsg.time = time.time()
        logMsg.msg = msgContent
        self.__logMsgs.append(logMsg)

    def addFriendMsg(self,msg):

        self.__friendMsgs.append(msg)

    def clearEvents(self):
        """
        清空events
        """ 
        del self.newMemberJoinGroupEvent[:]
        del self.groupAdminChangeEvents[:]
        del self.groupMsgEvents[:]
        del self.friendMsgEvents[:]
        del self.addMeFiendEvents[:]
        del self.logoutEvents[:]
        del self.loginFailedEvents[:]
        del self.loginSuccessEvents[:]
        del self.needVerifyCodeEvents[:]
        del self.tempMsgEvents[:]
        del self.errorMsgEvents[:]
        del self.leaveGroupEvents[:]
        del self.friendStatusChangeEvents[:]
        del self.logMsgEvents[:]
        del self.sendBuddyEvents[:]
        del self.sendGroupEvents[:]

    def addSendBuddyEvent(self, msgEvent):
        """
        添加处理发送buddy消息（好友，临时）的事件
        """
        msgEvent.setupQQInstance(self)
        self.sendBuddyEvents.append(msgEvent)

    def addSendGroupEvent(self, msgEvent):
        """
        添加处理发送群消息的事件
        """
        msgEvent.setupQQInstance(self)
        self.sendGroupEvents.append(msgEvent)

    def addLogMsgEvent(self, msgEvent):
        """
        添加处理log信息的事件
        """
        msgEvent.setupQQInstance(self)
        self.logMsgEvents.append(msgEvent)

    def addErrorMsgEvent(self,msgEvent):
        """
        添加处理错误信息的事件
        msgEvent: MsgEvent实例
        """
        msgEvent.setupQQInstance(self)
        self.errorMsgEvents.append(msgEvent)

    def addTempMsgEvent(self,msgEvent):
        """
        添加处理临时会话的事件
        msgEvent: MsgEvent实例
        """
        msgEvent.setupQQInstance(self)
        self.tempMsgEvents.append(msgEvent)

    def addNewMemberJoinGroupEvent(self,msgEvent):
        """
        添加处理新成员申请入群的事件，只有自己是管理才能收到此消息
        msgEvent: MsgEvent实例
        """
        msgEvent.setupQQInstance(self)
        self.newMemberJoinGroupEvent.append(msgEvent)

    def addGroupAdminChangeEvent(self,msgEvent):
        """
        添加处理管理员变更的事件
        msgEvent: MsgEvent实例
        """
        msgEvent.setupQQInstance(self)
        self.logoutEvents.append(msgEvent)

    def addGroupMsgEvent(self,msgEvent):
        """
        添加处理群消息的事件
        msgEvent: MsgEvent实例
        """
        msgEvent.setupQQInstance(self)
        self.groupMsgEvents.append(msgEvent)

    def addNeedVerifyCodeEvent(self,msgEvent):
        """
        添加处理需要验证码的事件
        msgEvent: MsgEvent实例
        """
        msgEvent.setupQQInstance(self)
        self.needVerifyCodeEvents.append(msgEvent)

    def addLoginSuccessEvent(self,msgEvent):
        """
        添加处理登录成功的事件
        msgEvent: MsgEvent实例
        """
        msgEvent.setupQQInstance(self)
        self.loginSuccessEvents.append(msgEvent)

    def addLoginFailedEvent(self,msgEvent):
        """
        添加处理登录失败的事件
        msgEvent: MsgEvent实例
        """
        msgEvent.setupQQInstance(self)
        self.loginFailedEvents.append(msgEvent)

    def addLogoutEvent(self,msgEvent):
        """
        添加处理掉线或者登出的事件
        msgEvent: MsgEvent实例
        """
        msgEvent.setupQQInstance(self)
        self.logoutEvents.append(msgEvent)

    def addAddMeFiendEvent(self,msgEvent):
        """
        添加处理别人加我好友的事件
        msgEvent: MsgEvent实例
        """
        msgEvent.setupQQInstance(self)
        self.addMeFiendEvents.append(msgEvent)

    def addFriendMsgEvent(self,msgEvent):
        """
        添加处理好友消息的事件
        msgEvent: MsgEvent实例
        """
        msgEvent.setupQQInstance(self)
        self.friendMsgEvents.append(msgEvent)

    def addLogoutEvent(self,msgEvent):
        """
        添加登出（掉线）事件
        msgEvent: MsgEvent实例
        """
        msgEvent.setupQQInstance(self)
        self.logoutEvents.append(msgEvent)

    def addLeaveGroupEvent(self,msgEvent):
        """
        添加我被踢出群事件
        """

        msgEvent.setupQQInstance(self)
        self.leaveGroupEvents.append(msgEvent)

    def addFriendStatusChangeEvent(self,msgEvent):
        """
        添加好友状态改变事件
        """

        msgEvent.setupQQInstance(self)
        self.friendStatusChangeEvents.append(msgEvent)

    def debug(self):
        self.__startListenEventsAfterLogin()

    def login(self):

        msg = u"开始登陆...\n"
        if not self.loginSucCount:
            self.__startListenEventsBeforLogin()
        checkResult = self.check()
        msg += u"是否需要验证码:" + unicode(not checkResult) + "\n"
        if not checkResult:
            _msg = message.BaseMsg()
            _msg.msg = checkResult
            self.__needVerifyCodeMsgs.append(_msg)
            while self.needVerifyCode: pass

        loginResult = super(WebQQClient, self).login()
        msg += u"登录结果: %s"%(unicode(loginResult))
        self.addLogMsg(msg)

        if loginResult != True:
            msg = message.BaseMsg()
            msg.msg = loginResult
            self.__loginFailedMsgs.append(msg)
            if u"验证码不正确" in loginResult:
                self.login()
        else:
            #self.__loginSuccessMsgs.append(loginResult)
            self.qqUser = entity.QQUser()
            self.qqUser.gtk = self.gtk
            self.online = True
            for event in self.loginSuccessEvents:
                event.main(loginResult)
            
            if not self.loginSucCount:
                self.__startListenEventsAfterLogin()
                thread.start_new_thread(self.__startSendMsgFuncPool,(None,))

            self.loginSucCount += 1

    def __startListenEventsBeforLogin(self):


        self.__listenEvent(self.__needVerifyCodeMsgs, self.needVerifyCodeEvents)
#        thread.start_new_thread(self.__listenEvent,(self.__loginSuccessMsgs, self.loginSuccessEvents))
        self.__listenEvent(self.__loginFailedMsgs, self.loginFailedEvents)
        self.__listenEvent(self.__errorMsgs, self.errorMsgEvents)

    def __startListenEventsAfterLogin(self):

        self.__listenEvent(self.__addMeFiendMsgs, self.addMeFiendEvents)
        self.__listenEvent(self.__friendMsgs, self.friendMsgEvents)
        self.__listenEvent(self.__logoutMsgs, self.logoutEvents)
        self.__listenEvent(self.__groupMsgs, self.groupMsgEvents)
        self.__listenEvent(self.__groupAdminChangeMsgs, self.groupAdminChangeEvents)
        self.__listenEvent(self.__newMemberJoinGroupMsgs, self.newMemberJoinGroupEvent)
        self.__listenEvent(self.__tempMsgs, self.tempMsgEvents)
        self.__listenEvent(self.__leaveGroupMsgs, self.leaveGroupEvents)
        self.__listenEvent(self.__friendStatusChangeMsgs, self.friendStatusChangeEvents)
        self.__listenEvent(self.__logMsgs, self.logMsgEvents)
        self.__listenEvent(self.__sendBuddyMsgs, self.sendBuddyEvents)
        self.__listenEvent(self.__sendGroupMsgs, self.sendGroupEvents)

    def __listenEvent(self,msgs,events):

        EventListener(msgs,events,self.addErrorMsg).start()



#    def inputVerifyCodeEvent(self,eventArgs):
    def run(self):

        while True:
            if self.online:
                try:
                    msg = self.getMsg()
#                    print msg
                    self.__analysisMsg(msg)
                except Exception,e:

                    msg = message.ErrorMsg()
                    msg.msg = traceback.format_exc()
                    msg.summary = e
                    self.addErrorMsg(msg)
            time.sleep(0.1)


    def getGroupByUin(self,uin):
        """
        @rtype: entity.Group实例
        """

        for i in range(6):
            if self.qqUser.groups.has_key(uin):
                return self.qqUser.groups[uin]
            else:
                self.getGroups()

    def getFriendByUin(self,uin):
        """
        @rtype: entity.Friend实例
        """
        
        for i in range(6):
            if self.qqUser.friends.has_key(uin):
                return self.qqUser.friends[uin]
            else:
                self.getFriends()
                

    def getFriends(self):

        """
        获取好友，结果将放在self.qqUser.friends里面
            self.qqUser.friends是个dict，key是uin，value是entity.Friend实例
        """
        """
        {"retcode":0,"result":{"friends":[{"flag":20,"uin":597845441,"categories":5},{"flag":20,"uin":769476381,"categories":5}],"marknames":[{"uin":3215442946,"markname":"林彬YAN","type":0}],"categories":[{"index":0,"sort":0,"name":"yi~~呀咿呀~"},{"index":5,"sort":5,"name":" 孤单相伴"}],"vipinfo":[{"vip_level":0,"u":597845441,"is_vip":0},{"vip_level":2,"u":769476381,"is_vip":1}],"info":[{"face":0,"flag":20972032,"nick":"林雨辰的那只神经喵喵","uin":597845441},{"face":288,"flag":20972102,"nick":" ☆紫梦璃★","uin":769476381}]}}
        """
        data = super(WebQQClient, self).getFriends()
        if data["retcode"] == 0:
            data = data["result"]
            for i in data["friends"]:
                friendObj = entity.Friend()
                uin = i["uin"]
                uin = long(uin)
                friendObj.uin = uin
                groupId = data["categories"]

                friendObj.groupId = groupId
                friendObj.groupName = self.__getValueFromDic(groupId, data["categories"], "index", "name")
                friendObj.markName = self.__getValueFromDic(uin, data["marknames"], "uin", "markname")
                friendObj.nick = self.__getValueFromDic(uin, data["info"], "uin", "nick")
                friendObj.getQQ = self.uin2number

                self.qqUser.friends[uin] = friendObj

    def getGroups(self):
        """
        结果保存在 self.qqUser.groups，self.qqUser.groups是个dict，key uin，value entity.Group实例
        """
        """
        {"retcode":0,"result":{"gmasklist":[{"gid":1000,"mask":3},{"gid":3181386224,"mask":0},{"gid":3063251357,"mask":2}],"gnamelist":[{"flag":1090519041,"name":"神经","gid":3181386224,"code":1597786235},{"flag":16777217,"name":"哭泣","gid":3063251357,"code":3462805735}],"gmarklist":[]}}
        """

        data = super(WebQQClient, self).getGroups()

        if data["retcode"] == 0:
            data = data["result"]
#            print data
            for gname in data["gnamelist"]:
#                gid = maskDic["gid"]
#                uin = long(uin)                
                uin = gname["gid"]
                group = entity.Group()
                group.uin = uin
                group.code = gname["code"]
                mask = self.__getValueFromDic(uin, data["gmasklist"], "gid", "mask")
                if not mask:
                    mask = 0
                group.mask = mask
                group.name = gname["name"]
                group.getQQ = lambda u:self.uin2number(u,type=4)
                group.getMemberByUin = lambda memberUin,groupUin = uin:self.getGroupMemberByUin(groupUin, memberUin)
                # 记得分析gmarklist

#                group.members = []

                self.qqUser.groups[uin] = group
#                print self.groups

    def getGroupMembers(self,uin):
        """
        uin: group uin
        members保存在entity.Group.members
        """

        """
        {"retcode":0,"result":{"stats":[{"client_type":41,"uin":379450326,"stat":10},{"client_type":1,"uin":769476381,"stat":10}],"minfo":[{"nick":"神经喵咪","province":"","gender":"female","uin":379450326,"country":"","city":""},{"nick":" ☆紫梦璃★","province":"","gender":"female","uin":769476381,"country":"梵蒂冈","city":""}],"ginfo":{"face":0,"memo":"","class":10028,"fingermemo":"","code":1597786235,"createtime":1362561179,"flag":1090519041,"level":0,"name":"神经","gid":3181386224,"owner":769476381,"members":[{"muin":379450326,"mflag":4},{"muin":769476381,"mflag":196}],"option":2},"vipinfo":[{"vip_level":0,"u":379450326,"is_vip":0},{"vip_level":2,"u":769476381,"is_vip":1}]}}
        """
        group = self.getGroupByUin(uin)
        data = super(WebQQClient, self).getGroupInfo(group.code)
        members = []
        if data["retcode"] == 0:
            data = data["result"]
            # 如果有群名片的话，result里面会有cards这个key
            if data.has_key("cards"):
                cards = data["cards"] # [{muin: 3764013857, card: "呵呵"}]
            else:
                cards = []
            group.createTime = data["ginfo"]["createtime"]
            creator = data["ginfo"]["owner"]
#            print data
            for memberDic in data["ginfo"]["members"]:
                uin = memberDic["muin"]
#                uin = long(uin)
                member = entity.GroupMember()                
                if uin == creator:
                    group.creator = member
                member.nick = self.__getValueFromDic(uin, data["minfo"], "uin", "nick")
                member.isAdmin = not ((self.__getValueFromDic(uin, data["ginfo"]["members"], "muin", "mflag"))%2 == 0)
                member.status = self.__getValueFromDic(uin,data["stats"],"uin","stat")
                member.card = self.__getValueFromDic(uin,cards,"muin","card")
                member.uin = uin
                member.getQQ = self.uin2number
                members.append(member)

        group.members = members


    def __getValueFromDic(self,standardValue,dicList,standardKey,needKey):
        """
        """
        for i in dicList:
            if standardValue == i[standardKey]:
                return i[needKey]

        return ""
    def allowAddFriend(self,qq,mname):

        super(WebQQClient, self).allowAddFriend(qq, mname)

        logMsg = u"同意了QQ%d加我为好友的申请,并为其备注%s"%(qq,mname)

    def handleAddGroupMsg(self,reqUin,groupUin,msg="",allow = True):
        """
        @param reqUin: 加群者的uin
        @type reqUin: int

        @param groupUin: 所加的群的uin
        @type:int

        @msg: 拒绝加群时填的消息
        @type: str

        @param allow:是否同意加群
        @type: bool
        """
        super(WebQQClient, self).handleAddGroupMsg(reqUin, groupUin, msg, allow)
        qq = self.uin2number(reqUin)
        group = self.getGroupByUin(groupUin)
        msgContent = u"QQ%d加入群（%s）[%d], 验证信息：%s"%(qq, group.name, group.qq, msg)
        if allow:
            self.getGroupMembers(groupUin)
            logMsg = u"同意了" + msgContent
        else:
            logMsg = u"拒绝了" + msgContent

        self.addLogMsg(logMsg)

         

    def getGroupMemberByUin(self,groupUin,groupMemberUin):
        """
        @rtype: entity.GroupMember实例
        """

        group = self.getGroupByUin(groupUin)
        for i in range(6): # 最多获取三次
            member = group._getMemberByUin(groupMemberUin)
            if not member:
                self.getGroupMembers(groupUin)
            else:
                break
        return member


    def __mergeMsg(self,msg):
        
        result = ""
        for i in msg:
            if isinstance(i,list):
                continue
            else:
                result += i
        return result.strip()
    
    def checkMsgId(self, msgId1,msgId2):
        
        msgId = (msgId1, msgId2)
        exists = msgId in self.msgIds
        self.msgIds.append(msgId)

        if len(self.msgIds) > self.msgIdsMaxNum:
            self.msgIds.pop(0)

        return exists
        
    def __analysisMsg(self,msg):

        dic = msg

        logMsg = u"收到消息(全), " + str(msg)
        self.addLogMsg(logMsg)

        if not dic.has_key("retcode"):
            self.recordMsgError()
            return

        if 0 == dic["retcode"] and isinstance(dic["result"],list):

            self.getMsgFailedCount = 0

            for i in dic["result"]:

#                i = copy.deepcopy(i)
               
                """
                {u'retcode': 0, u'result': [{u'poll_type': u'buddies_status_change', u'value': { u'status': u'online', u'client_type': 1, u'uin': 2010848814}}]} 
                好友状态改变
                
                """
                if "buddies_status_change" == i["poll_type"]:

                    data = i["value"]
                    uin = data["uin"]
                    friend = self.getFriendByUin(uin)
                    if not friend:
                        continue
                    friend.status = data["status"]
                    friend.clientType = data["client_type"]
                    msg = message.FriendStatusChangeMsg()
                    msg.friend = friend
                    self.__friendStatusChangeMsgs.append(msg)

                    logMsg = u"收到好友在线状态改变消息：%s %s了"%(friend.getName(), friend.status)
                    self.addLogMsg(logMsg)

                elif "message" == i["poll_type"]:# new friend's message
                    """
                    {"retcode":0,"result":[{"poll_type":"message","value":{"msg_id":26113,"from_uin":908551613,"to_uin":721011692,"msg_id2":266862,"msg_type":9,"reply_ip":178848407,"time":1386500840,"content":[["font",{"size":11,"color":"ff00ff","style":[1,0,0],"name":"\u5FAE\u8F6F\u96C5\u9ED1"}],"\u5475\u5475 "]}}]}
                    """
                    data = i["value"]
                    if self.checkMsgId(data["msg_id"], data["msg_id2"]):
                        continue
                    uin = data["from_uin"]
#                    uin = long(uin)
                    friend = self.getFriendByUin(uin)
                    if not friend:
                        friend = entity.Friend()
                        friend.uin = uin
                        friend.getQQ = self.uin2number
                        friend.nick = u"单向好友，他有你，你没他"
                        self.qqUser.friends[uin] = friend
                    friend.ip = data["reply_ip"]
                    
                    msg = message.FriendMsg()
                    msg.friend = friend
                    msg.time = data["time"]
                    msg.originalMsg = data["content"][1:]
#                    print msg.originalMsg
                    msg.msg = self.__mergeMsg(msg.originalMsg)
#                    print msg.msg
                    msg.reply = lambda content,  fontStyle=None, friendUin=uin:self.sendMsg2Buddy(friendUin, content, fontStyle)
                    self.__friendMsgs.append(msg)
                    logMsg = u"收到了好友消息,  %s:%s"%(friend.getName(), msg.msg)
                    self.addLogMsg(logMsg)

                elif "sess_message" == i["poll_type"]:# new temporary conversation message
                    """
                    {"retcode":0,"result":[{"poll_type":"sess_message","value":{"msg_id":29709,"from_uin":3863325290,"to_uin":1546582558,"msg_id2":51531,"msg_type":140,"reply1_ip":178848406,"time":1376718421,"id":456949784,"ruin":379450326,"service_type":0,"flags":{"text":1,"pic":1,"file":1,"audio":1,"video":1},"content":[["font",{"size":11,"color":"ff0000","style":[1,0,0],"name":"\u5FAE\u8F6F\u96C5\u9ED1"}],"a "]}}]}

                    """
                    data = i["value"]
                    if self.checkMsgId(data["msg_id"], data["msg_id2"]):
                        continue
                    uin = data["from_uin"]
#                    uin = long(uin)
                    msg = message.TempMsg()
                    msg.uin = uin
#                    msg.ip = data["reply1_ip"]
                    msg.qq = int(data["ruin"])
                    self.__qqNumbers[uin] = msg.qq
                    msg.time = data["time"]
                    msg.originalMsg = data["content"][1:]
#                    print msg.originalMsg
                    msg.msg = self.__mergeMsg(msg.originalMsg)
#                    print msg.msg
                    msg.reply = lambda content, fontStyle=None, buddyUin=uin:self.sendMsg2Buddy(buddyUin,content, fontStyle)
                    self.__tempMsgs.append(msg)

                    logMsg = u"收到了临时会话消息, QQ%d：%s"%(msg.qq, msg.msg)
                    self.addLogMsg(logMsg)


                elif "group_message"==i["poll_type"]:# New group message
                    """
                     {"retcode":0,"result":[{"poll_type":"group_message","value":{"msg_id":16985,"from_uin":456949784,"to_uin":1546582558,"msg_id2":519158,"msg_type":43,"reply_ip":176488598,"group_code":432844316,"send_uin":1615088372,"seq":2869,"time":1376716816,"info_seq":141382064,"content":[["font",{"size":11,"color":"ff00ff","style":[1,0,0],"name":"\u5FAE\u8F6F\u96C5\u9ED1"}],"1 "]}}]}

                    """
                    data = i["value"]
                    if self.checkMsgId(data["msg_id"], data["msg_id2"]):
                        continue
                    uin = data["from_uin"]
#                    uin = long(uin)
                    memberUin = int(data["send_uin"])
                    group = self.getGroupByUin(uin)
                    if not group:
                        continue
#                    print group
#                    self.getGroupMembers(uin)
#                    print "group",group
                    group.qq = data["info_seq"]
                    self.__groupQQNumbers[uin] = group.qq
                    msg = message.GroupMsg()
                    msg.group = group
                    member = self.getGroupMemberByUin(uin,memberUin)
#                    member = group.getMemberByUin(memberUin)
#                    if type(member) == type(None):
                    if not member:
#                        print "getMembers"
                        self.getGroupMembers(uin)
                        member = group.getMemberByUin(memberUin)
#                        if type(member) == type(None):
                        if not member:
                            continue
                    msg.groupMember = member
#                    msg.groupMember.ip = data["reply_ip"]
                    msg.time = data["time"]
                    msg.originalMsg = data["content"][1:]
#                    print msg.originalMsg
                    msg.msg = self.__mergeMsg(msg.originalMsg)
#                    print msg
                    msg.reply = lambda content,fontStyle=None,groupUin=uin: self.sendMsg2Group(groupUin,content, fontStyle)

                    self.__groupMsgs.append(msg)

                    logMsg = u"收到了群消息, 群:%s(%d) -- 群成员:%s: %s"%(group.name, group.qq, member.getName(), msg.msg)
                    self.addLogMsg(logMsg)
                    
                elif "system_message" == i["poll_type"]:

                    data = i["value"]
                    if "verify_required" == data["type"]:# Add me friend
                        """
                        {"retcode":0,"result":[{"poll_type":"system_message","value":{"seq":34653,"type":"verify_required","uiuin":"","from_uin":3863325290,"account":379450326,"msg":"adfas","allow":1,"stat":10,"client_type":1}}]}
                        """
                        msg = message.AddMeFriendMsg()
                        uin = data["from_uin"]
#                        uin = long(uin)
                        msg.uin = uin
                        msg.qq = data["account"]
                        msg.msg = data["msg"]
                        msg.allow = data["allow"]

                        self.__addMeFiendMsgs.append(msg)

                        logMsg = u"收到了加我好友请求, 申请人QQ %d, 验证消息:%s"%(msg.qq, msg.msg)
                        self.addLogMsg(logMsg)

                    elif "added_buddy_sig" == data["type"]:

                        """
                        收到消息(全), {u'retcode': 0, u'result': [{u'poll_type': u'system_message', u'va lue': {u'account': 721011691, u'seq': 59188, u'stat': 20, u'uiuin': u'', u'sig': u'\xb5!\xdctN\xfbX@e\x03\xee\xf9\x0bb\xaa\x1f\x99S\xf1\x856\xe4/\xb2', u'from_uin': 1849509427, u'type': u'added_buddy_sig'}}]}
                        别人添加了我为好友 
                        """
                        msg = message.AddMeFriendMsg()
                        uin = data["from_uin"]
#                        uin = long(uin)
                        msg.uin = uin
                        msg.qq = data["account"]
                        msg.msg = u"别人添加我为好友"
                        msg.allow = 0

                        self.__addMeFiendMsgs.append(msg)
                        logMsg = u"收到了已经加我为好友的消息, QQ %d "%(msg.qq, msg.msg)
                        self.addLogMsg(logMsg)


                    
                elif "sys_g_msg" == i["poll_type"]:# New group system message
                    
                    data = i["value"]
                    if self.checkMsgId(data["msg_id"], data["msg_id2"]):
                        continue
                    groupUin = data["from_uin"]#Group's temporary number
                    groupUin = int(groupUin)
                    msgType = data["type"]
                    
                    if "group_leave" == msgType:
                        """
                        我被踢出群
                        {"retcode":0,"result":[{"poll_type":"sys_g_msg","value":{"msg_id":25842,"from_uin":3547669097,"to_uin":721011692,"msg_id2":587672,"msg_type":34,"reply_ip":176488602,"type":"group_leave","gcode":869074255,"t_gcode":164461995,"op_type":3,"old_member":721011692,"t_old_member":"","admin_uin":3530940629,"t_admin_uin":"","admin_nick":"\u521B\u5EFA\u8005"}}]}
                        t_gcode: 群号
                        """
                        msg = message.LeaveGroupMsg()
                        msg.groupUin = data["from_uin"]
                        msg.groupQQ = data["t_gcode"]
                        msg.adminUin = data["admin_uin"]
                        msg.adminNick = data["admin_nick"]
                        self.__leaveGroupMsgs.append(msg)

                        logMsg = u"收到了我被踢出群消息，群号：%d, 操作管理员 %s"%(msg.groupQQ, msg.adminNick)
                        self.addLogMsg(logMsg)

                    elif "group_admin_op" == msgType:
                        """
                        
                        管理员变更(设置)
                        {u'retcode': 0, u'result': [{u'poll_type': u'sys_g_msg', u'value': {u'reply_ip': 180061933, u'uin_flag': 1, u'msg_type': 44, u't_uin': 721011692, u'type': u'group_admin_op', u't_gcode': 291186448, u'msg_id': 36217, u'uin': 721011692, u'msg_id2': 254668, u'op_type': 1, u'from_uin': 3124397784L, u'gcode': 3046992595L, u' to_uin': 721011692}}]} 
                        管理员变更(取消)
                        {u'retcode': 0, u'result': [{u'poll_type': u'sys_g_msg', u'value': {u'reply_ip': 176757008, u'uin_flag': 0, u'msg_type': 44, u't_uin': 721011692, u'type': u'group_admin_op', u't_gcode': 291186448, u'msg_id': 7304, u'uin': 721011692, u'msg_id2': 428715, u'op_type': 0, u'from_uin': 3124397784L, u'gcode': 3046992595L, u't o_uin': 721011692}}]}
                        
                        """
                        groupUin = data["from_uin"]
                        group = self.getGroupByUin(groupUin)
                        groupMemberUin = data["uin"]
                        groupMember = self.getGroupMemberByUin(groupUin, groupMemberUin)
                        groupMember.isAdmin = bool(data["uin_flag"])

                        msg = message.GroupAdminChangeMsg()
                        msg.opType = data["op_type"]
                        msg.group = group
                        msg.groupMember = groupMember

                        self.__groupAdminChangeMsgs.append(msg)
                        if msg.opType == 1:
                            opTypeStr = u"设置"
                        else:
                            opTypeStr = u"取消"
                        logMsg = u"收到了管理员变更消息, 群 %s %s了%s 的管理员"%(group.name, opTypeStr, groupMember.getName())
                        self.addLogMsg(logMsg)

                    elif "group_request_join" == msgType:# Somebody want to join group
                        """
                        {"retcode":0,"result":[{"poll_type":"sys_g_msg","value":{"msg_id":62532,"from_uin":456949784,"to_uin":1546582558,"msg_id2":29087,"msg_type":35,"reply_ip":176489085,"type":"group_request_join","gcode":432844316,"t_gcode":141382064,"request_uin":3863325290,"t_request_uin":"","msg":"123"}}]}
                        """
                        group = self.getGroupByUin(groupUin)
                        msg = message.JoinGroupMsg()
                        msg.group = group
                        msg.uin = int(data["request_uin"])
#                        msg.ip= data["reply_ip"]
                        msg.msg = data["msg"]
                        self.__newMemberJoinGroupMsgs.append(msg)

                        logMsg = u"收到了有人加群消息, 群：%s, 加群者uin: %d"%(group.name, msg.uin)
                        self.addLogMsg(logMsg)

        elif dic["retcode"] in self.logoutCodes:
            self.online = False
            msg = message.BaseMsg()
            msg.msg = dic["retcode"]
            self.__logoutMsgs.append(msg)
            logMsg = u"登出了，看看是不是掉线了"
            self.addLogMsg(logMsg)

        elif dic["retcode"] == -1:
            self.recordMsgError()
        
        elif dic["retcode"] in [102, 116]:
            """
            无消息
            """
            pass
        else:
            msg = message.ErrorMsg()
            msg.msg = str(dic)
            self.addErrorMsg(msg)

    def recordMsgError(self):

        self.getMsgFailedCount += 1
        msg = message.ErrorMsg()
        msg.msg = u"网络连接失败"
        self.addErrorMsg(msg)
        if self.getMsgFailedCount >= 3:
            self.online = False
            self.__logoutMsgs.append(msg)

    def __addSendBuddyMsg(self,buddyId,fontStyle,content):

        msg = message.SendBuddyMsg()
        msg.qq = self.uin2number(buddyId)
        msg.fontStyle = fontStyle
        msg.time = time.time()
        msg.content = content
        self.__sendBuddyMsgs.append(msg)
        logMsg = u"发送消息给QQ:%d：%s"%(msg.qq,content)
        self.addLogMsg(logMsg)

    def __addSendGroupMsg(self,uin,fontStyle,content):

        msg = message.SendGroupMsg()
        msg.group = self.getGroupByUin(uin)
        msg.fontStyle = fontStyle
        msg.time = time.time()
        msg.content = content
        self.__sendGroupMsgs.append(msg)
        logMsg = u"发送消息给群:%d：%s"%(msg.group.qq,content)
        self.addLogMsg(logMsg)

    def sendMsg2Buddy(self, buddyId, content, fontStyle=None):
        """
        # buddyId: 好友或陌生人的uin
        # content: 要发送的内容，unicode编码
        # fontStyle: entity.FontStyle

        """

        if fontStyle:
            fontStyle = fontStyle.__str__()
        else:
            fontStyle = self.qqUser.fontStyle

        self.__addSendBuddyMsg(buddyId,fontStyle,content)


        self.sendMsgFuncPool.append(lambda:super(WebQQClient,self).sendMsg2Buddy( buddyId, content, fontStyle))

    def sendMsg2Group(self, groupId, content, fontStyle=None):
        """
        groupId:群uin
        content: 要发送的内容, unicode编码
        fontStyle: entity.FontStyle实例
        """

        if fontStyle:
            fontStyle = fontStyle.__str__()
        else:
            fontStyle = self.qqUser.fontStyle

        self.__addSendGroupMsg(groupId,fontStyle,content)

        self.sendMsgFuncPool.append(lambda:super(WebQQClient,self).sendMsg2Group( groupId, content, fontStyle))

    def sendTempMsgFromGroup(self, groupId, buddyId, content, fontStyle=None):
        """
        groupId: 群uin
        buddyId: 对方uin
        content: 要发送的内容，Unicode编码
        fontStyle: entity.FontStyle
        """

        if fontStyle:
            fontStyle = fontStyle.__str__()
        else:
            fontStyle = self.qqUser.fontStyle
        
        self.__addSendBuddyMsg(buddyId,fontStyle,content)

        self.sendMsgFuncPool.append(lambda:super(WebQQClient,self).sendTempMsgFromGroup( groupId, buddyId,content, fontStyle))
    
    def __startSendMsgFuncPool(self,arg):
        
        while True:
            if not self.online:
                continue
            if self.sendMsgFuncPool:
                sendFunc = self.sendMsgFuncPool.pop(0)
                try:
                    sendFunc()
                except Exception,e:
                    msg = message.ErrorMsg()
                    msg.msg = traceback.format_exc()
                    msg.summary = e
                    self.addErrorMsg(msg)
            time.sleep(0.5)
        

    def deleteGroupMember(self, group_number, qq_number):

        res = super(WebQQClient, self).deleteGroupMember(group_number, qq_number)
        code = res
        if code == 0:
            result = u"删除成功"
        elif code == 3:
            result = u"删除失败,此成员不存在"
        elif code == 7:
            result = u"删除失败,权限不足"
        elif code == 11:
            result = u"群号错误"
        elif code == -1:
            result = u"网络错误"
        else:
            result = u"删除失败，我不是管理员诶~"
        return result


