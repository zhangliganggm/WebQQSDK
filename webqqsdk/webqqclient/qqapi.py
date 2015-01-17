#coding=UTF8

import sys
import thread
import re 
import json 
import urllib
import random
import time
import os

curpath = os.path.dirname(__file__)
parpath = os.path.dirname(curpath)
if not parpath:
    parpath = ".."
sys.path.append(parpath)
from utils import *
import entity

encypt = webqq_encypt.Encypt()


class WebQQ(object):
    
    def __init__(self,qq,pwd):

        self.qq = qq
        self.pwd = pwd
        self.headers = {
                "User-Agent":"Mozilla/5.0 (Windows NT 6.2; WOW64; rv:23.0) Gecko/20100101 Firefox/23.0",
                "Accept":"*/*",
                "Accept-Encoding":"gzip,deflate",
                "Accept-Language":"zh-CN,zh;q=0.8",
                "Connection":"keep-alive",
                "host":"d.web2.qq.com",
                "Referer":"http://d.web2.qq.com/proxy.html?v=20110331002&callback=1&id=2",
                "Content-Type":"application/x-www-form-urlencoded; charset=UTF-8"}

        self.headers = {}
        self.http = httpserver.Http()
        self.http.set_tryagain(3)
#        self.http = httpserver.Http(cookie_path="webqq_cookie.txt")
#        self.http.headers = self.headers
        self.clientid = "605644"
        self.ptwebqq = ""
        self.vfwebqq = ""
        self.psessionid = ""
        self.port = ""
        self.gtk = ""
        self.verifyCode = ""
        self.needVerifyCode = False
        self.groupMsg_id = self.buddyMsgId = random.randint(0,6000000)
        self.fontStyle = entity.FontStyle(u"黑体",12,16711680)
        self.verifyCodePath = "verfiycode.jpg"

        self.friends_dic = {}
        self.groups_dic = {}
        self.groups_info_dic = {} # key gcode, value dict

        # key: uin, value: qq
        

        self.online= False

        

    def __getSession(self,key):
        
        return re.findall(key+"=(.*?);",self.http.res_headers["Set-Cookie"])[0]
#        return re.findall(key+"=(.*?);",self.http.fOpen("cookies.txt"))[0]

    def __getPtui(self,key,data):
        
        data = data.strip()
#        print data
        data = data[:-1].replace(key,"")
        return eval(data)


    def check(self):
        """
        检查QQ是否需要验证码
        @rtype:bool
        """
        url = "https://ssl.ptlogin2.qq.com/check?uin=" + self.qq + "&appid=1003903&js_ver=10074&js_type=0&login_sig=Gyg0BsQ6G1XFUqD0wrW5f8fnxfqo-9wnjsPY07GqpIxGr75e3mAcaPkWiTRZ3MR9&u1=http%3A%2F%2Fweb2.qq.com%2Floginproxy.html&r=0.2673544683493674"

#        url = "https://ssl.ptlogin2.qq.com/check?uin="+self.qq+"&appid=1003903&js_ver=10074&js_type=0&login_sig=VoWX*m26Eywvl6cStE-l5XdY4LzvWfgaEv9lHrCpnPK1jJXrqa1uSPitTP3PW05u&u1=http%3A%2F%2Fweb2.qq.com%2Floginproxy.html&r=0.3267894003605193"
        data = self.http.connect(url)
        if not data:
            return False

#        print data
        tmp=self.__getPtui("ptui_checkVC",data)
#        print tmp[2]
        #提取验证码
#        tmp=re.findall(",'(.*?)',",data)
        self.verifyCode=tmp[1]
        self.uin=tmp[2]
#        print tmp
        if "0"!=tmp[0]:
            url="https://ssl.captcha.qq.com/getimage?aid=1003903&r=0.2938272715546191&uin="+self.qq
#            print "\n验证码"
            data = self.http.connect(url,encoding="")
#            print data
            self.http.file_open(self.verifyCodePath,"wb",data)
            self.needVerifyCode = True
            return False
        #print verifyCode
#        pos=data.rfind(",")
#        uin=eval(data[pos+1:-2])
        return True
        
    def inputVerifyCode(self,code):
        """
        @param code:验证码
        验证码在当前目录下
        """

        self.verifyCode = code
        self.needVerifyCode = False

    def __login1(self):
        """
        成功返回True
        失败返回失败原因(str)
        """

        p = encypt.encyptPwd(self.pwd,self.verifyCode,self.uin)

        data = self.http.connect("https://ssl.ptlogin2.qq.com/login?u="+self.qq+"&p="+p+"&verifycode="+self.verifyCode+"&webqq_type=10&remember_uin=1&login2qq=1&aid=1003903&u1=http%3A%2F%2Fweb2.qq.com%2Floginproxy.html%3Flogin2qq%3D1%26webqq_type%3D10&h=1&ptredirect=0&ptlang=2052&daid=164&from_ui=1&pttype=1&dumy=&fp=loginerroralert&action=2-30-59555&mibao_css=m_webqq&t=1&g=1&js_type=0&js_ver=10039&login_sig=hjVAqjuh862EOt*vVy5QVVDwSTrs*pRmlJsXN3vJbIfIEG7d8u4dxMcJ8i9h65zR")
        self.needVerifyCode = False
        if not data:
            return u"网络错误!"
#        print data
        ptui = self.__getPtui("ptuiCB",data)
        if ptui[0] == "0":
            self.ptwebqq=self.__getSession("ptwebqq")
            self.hash_code = encypt.getHash(self.qq,self.ptwebqq)
#            print "ptwebqq",self.ptwebqq
            skey = self.__getSession("skey")
#            skey = skey[1:]
#            print skey
            self.gtk = encypt.get_gtk(skey)
            url = ptui[2]
#            url = url.split("url=")[1]
#            url = urllib.unquote(url)
            if not self.http.connect(url):
                return u"网络错误"
#            print self.http.resUrl
#            print self.http.res_content
            self.gtk = str(self.gtk)
            return True
        else:
            return data
#        print self.ptwebqq


    def __login2(self):
        """
        成功返回True
        失败返回失败原因(str)
        """
        url="http://d.web2.qq.com/channel/login2"
        self.http.headers["Referer"] = "http://d.web2.qq.com/proxy.html?v=20110331002&callback=1&id=2"
        a={"status":"callme","ptwebqq":self.ptwebqq,"passwd_sig":"","clientid":self.clientid,"psessionid":""}
#        a="{\"status\":\"callme\",\"ptwebqq\":\"%s\",\"passwd_sig\":\"\",\"clientid\":\"%s\",\"psessionid\":\"\"}"%(self.ptwebqq,self.clientid)
        a=json.dumps(a)
#        a=json.encoder.JSONEncoder().encode(a)
#        print a;
        a = {"r":a,"clientid":self.clientid,"psessionid":"null"}
#        a = "r=%s"%(a)
#        print a
        data = self.http.connect(url,a)
        if not data:
            return u"网络错误!"
#        print self.http.res_content
        result = json.loads(self.http.res_content)
#        print result
        if not result["retcode"]:
            self.vfwebqq = result["result"]["vfwebqq"]
            self.psessionid = result["result"]["psessionid"]
            self.port = result["result"]["port"]
            self.index = result["result"]["index"]
            return True
        else:
            return result


    def login(self):
        """
        @return True:登录成功
        @return dic: 登录失败的原因
        """
        loginReuslt = self.__login1()
        if loginReuslt == True:
            loginReuslt = self.__login2()
            if loginReuslt == True:
                self.online = True
                return True
            else:
                return loginReuslt

        else:
            return loginReuslt
            
    def logout(self):
        """
        @return: 是否登出成功
        @rtype: bool
        """
        """
        http://d.web2.qq.com/channel/logout2?ids=&clientid=8745204&psessionid=8368046764001d636f6e6e7365727665725f77656271714031302e3133332e34312e383400000f45000000bb026e0400ecc3f92a6d0000000a405567555632306442656d00000028bfe6b3a295e03ef3b9491e5c366de0096cc6a710529f8c527249e7f3aafe4a8036cd44f7a39e02dc&t=1386995870481
        """
        url =  "http://d.web2.qq.com/channel/logout2?ids=&clientid=" + self.clientid + "&psessionid=" + self.psessionid + "&t=" + str(int(time.time()))
        data = self.http.connect(url)
        if not data:
            return False
        data = json.loads(data)
#        print data
        if data["result"] == "ok":
            return True
        else:
            return False
        return data

    def getDicFromList(self,dic_list,key,value):
        """
        """
        """
        @param dic_list: [{key:value},{key:value}]
        @param key: 
        @param value:
        @rtype: dict
        """
        result_list = [] # [{},{}]
        for dic in dic_list:
            if (isinstance(dic[key],int) or isinstance(dic[key],long)) and (isinstance(value,str) or isinstance(value,unicode)):
                if value.isdigit():
                    value = int(value)
            if dic[key] == value:
                result_list.append(dic)
        return result_list

    def getFriends(self):
        """
        例子：{"retcode":0,"result":{"friends":[{"flag":20,"uin":597845441,"categories":5},{"flag":20,"uin":769476381,"categories":5}],"marknames":[{"uin":3215442946,"markname":"林彬YAN","type":0}],"categories":[{"index":0,"sort":0,"name":"yi~~呀咿呀~"},{"index":5,"sort":5,"name":" 孤单相伴"}],"vipinfo":[{"vip_level":0,"u":597845441,"is_vip":0},{"vip_level":2,"u":769476381,"is_vip":1}],"info":[{"face":0,"flag":20972032,"nick":"林雨辰的那只神经喵喵","uin":597845441},{"face":288,"flag":20972102,"nick":" ☆紫梦璃★","uin":769476381}]}}
        @rtype: dict
        """

        url = "http://s.web2.qq.com/api/get_user_friends2"
        a = {"h":"hello","hash":self.hash_code,"vfwebqq":self.vfwebqq}
        a = json.dumps(a)
        data = {"r":a}
        data = self.http.connect(url,data)
        if not data:
            return None
        data = json.loads(data)
        return data
        if data["retcode"] == 0:
#            self.friends_dic = data["result"]
            return data["result"]
        else:
            return data["retcode"]
    

    def getOnlineFriedns(self):

        """
        例子：{"retcode":0,"result":[{"uin":597845441,"status":"online","client_type":1},{"uin":769476381,"status":"online","client_type":1}]}
        @rtype: dict
        
        """
        url = "http://d.web2.qq.com/channel/get_online_buddies2?clientid="+self.clientid+"&psessionid="+self.psessionid+"&t=1376715224899"
        data = self.http.connect(url)
        if not data:
            return None
        data = json.loads(data)
        return data


    def uin2number(self,uin,type=1):
        """
        uin转真实QQ号
        uin: int,临时号码
        type: int, 1 好友uin转QQ，4 群uin转群号
        @rtype: ink
        """

        

        url = "http://s.web2.qq.com/api/get_friend_uin2?tuin="+str(uin)+"&verifysession=&type=%d&code=&vfwebqq="%(type)+self.vfwebqq+"&t=1376721666740"
        data = self.http.connect(url)
        if not data:
            return 0
        data = json.loads(data)
        if not data.has_key("result"):
            return 0
#        print data
        qq = data["result"]["account"]
        return qq


    def getGroups(self):
        """
        {"retcode":0,"result":{"gmasklist":[{"gid":1000,"mask":3},{"gid":3181386224,"mask":0},{"gid":3063251357,"mask":2}],"gnamelist":[{"flag":1090519041,"name":"神经","gid":3181386224,"code":1597786235},{"flag":16777217,"name":"哭泣","gid":3063251357,"code":3462805735}],"gmarklist":[]}}
        
        mask: 群消息接收设置,如果为空，则使用群本身消息设置并每个群都接收
        code:gcode
        gid: 不明白
        @return: json
        @rtype: dict
        """

        url = "http://s.web2.qq.com/api/get_group_name_list_mask2"
        r = {"vfwebqq":self.vfwebqq,"hash":self.hash_code}
        a = json.dumps(r)
        data = {"r":a}
        data = self.http.connect(url,data)
        if not data:
            return None
        data = json.loads(data)
        return data
#        print data
        if data["retcode"] == 0:
            self.groups_dic = data["result"]
            
            if not self.get_dic_from_list(self.groups_dic["gmasklist"],"gid",1000):
                self.groups_dic["gmasklist"].append({"gid":"1000","mask":0})
            for dic in self.groups_dic["gnamelist"]:
                if not self.get_dic_from_list(self.groups_dic["gmasklist"],"gid",dic["gid"]):
                    self.groups_dic["gmasklist"].append({"gid":dic["gid"],"mask":0})
#            return self.getGroups()
            return 0
        else:
            return data["retcode"]
       

    def getGroupInfo(self,gCode):
        """
        {"retcode":0,"result":{"stats":[{"client_type":41,"uin":379450326,"stat":10},{"client_type":1,"uin":769476381,"stat":10}],"minfo":[{"nick":"神经喵咪","province":"","gender":"female","uin":379450326,"country":"","city":""},{"nick":" ☆紫梦璃★","province":"","gender":"female","uin":769476381,"country":"梵蒂冈","city":""}],"ginfo":{"face":0,"memo":"","class":10028,"fingermemo":"","code":1597786235,"createtime":1362561179,"flag":1090519041,"level":0,"name":"神经","gid":3181386224,"owner":769476381,"members":[{"muin":379450326,"mflag":4},{"muin":769476381,"mflag":196}],"option":2},"vipinfo":[{"vip_level":0,"u":379450326,"is_vip":0},{"vip_level":2,"u":769476381,"is_vip":1}]}}

        @rtype: dict
        """
        url = "http://s.web2.qq.com/api/get_group_info_ext2?gcode="+str(gCode)+"&vfwebqq="+self.vfwebqq+"&t=1376720992778"
        data = self.http.connect(url)
        if not data:
            return None
        data = json.loads(data)
        return data
        if data["retcode"] == 0:
            self.groups_info_dic[gCode] = data["result"]
            return 0
        else:
            return data["retcode"]
#            return self.getGroupMember(gCode)
        return data


    def getMsg(self):
        """
        获取消息，返回json
        """

        url = "http://d.web2.qq.com/channel/poll2"
        a = {"clientid":self.clientid,"psessionid":self.psessionid,"key":0,"ids":[]}
        a = json.dumps(a)
#        print type(a)
        data = {"clientid":self.clientid,"psessionid":self.psessionid,"r":a}
        data = self.http.connect(url,data,timeout=120)
#        print self.http.res_content
        if not data:
            return {"retcode":-1}
        data = json.loads(data)
        return data

    def __convertMsg(self,content):

#        print content
#        while "\n\n" in content:
#            content = content.replace("\n\n","\n")

        content = content.replace("\\","\\\\").replace("\r\n","\n").replace("\n","\\n").replace("\"","\\\"").replace("\t","\\t")
#        is_long_line = len(content.splitlines()[0]) > 100
        """
        if "]" in content
            content = " " + content
        else:
            content = " \\n" + content
        content_split_list = content.split("]")
        if len(content_split_list) > 1:
            content = "\" \\r\\n"
            for i in content_split_list:
                content += "]\",\""
        """

#        content = "   \\r\\n" + content
#        content = "   \\n" + content
#        content = repr(content)[1:].strip("'").replace("\\n\\n","\\n")
#        print content
#        print repr(content)

        return content

    def __getGroupSig(self,groupId,buddyId):

        url = "http://d.web2.qq.com/channel/get_c2cmsg_sig2?id=%s&to_uin=%s&service_type=0&clientid=%s&psessionid=%s&t=%d"%(groupId,buddyId,self.clientid,self.psessionid,int(time.time() * 100))
        data = self.http.connect(url)
        if not data:
            return ""
        data = json.loads(data)
        if data["retcode"] != 0:
            return ""
        sig = data["result"]["value"]
        return sig

    def sendTempMsgFromGroup(self,groupId,buddyId,content,fontStyle=None):
        """
        groupId: 群uin
        buddyId: 对方uin
        content: 要发送的内容，Unicode编码
        fontStyle: entity.FontStyle
        """
        
        if not fontStyle:
            fontStyle = self.fontStyle
        group_sig = self.__getGroupSig(groupId,buddyId)
#        print "sig",group_sig

        content = self.__convertMsg(content)
        url = "http://d.web2.qq.com/channel/send_sess_msg2"
        a ={"to":buddyId,"group_sig":group_sig,"face":0,"content":"[\"%s\",[\"font\",%s]]"%(content,fontStyle),"msg_id":self.buddyMsgId,"service_type":0,"clientid":self.clientid,"psessionid":self.psessionid}
        a = json.encoder.JSONEncoder().encode(a)
        data={"clientid":self.clientid,"psessionid":self.psessionid,"r":a}

        data = self.http.connect(url,data)
        if not data:
            return None
        data = json.loads(data)
#        print data
        return data


    
    def sendMsg2Buddy(self,buddyId,content,fontStyle=None):
        # buddyId: 好友的uin
        # content: 要发送的内容，unicode编码
        # fontStyle: entity.FontStyle
        

        if not fontStyle:
            fontStyle = self.fontStyle

        url="http://d.web2.qq.com/channel/send_buddy_msg2"
#        print repr(content)


#        content = content.replace("\n","\\n")
#replace("\r","\\r")
        content = self.__convertMsg(content) 
#        content = content.replace("[",u"【")
#        content = content.replace("[","").replace("]",u"")
#        print content
#        content = " " + content + " "
#        content = repr(content)[1:].strip("'")
#        content = u"字数" * 400
        """
        content_split = content.split("]")
        if len(content_split) == 1:
            content = "\"%s\""%content_split[0]
        else:
            content = "\""
            content_list = []
            for i in content_split:
                content_list.append(i + u"]")
#                content_list.append(i)
            content_list[-1] = content_list[-1][:-1]
#            content_list[-1] = content_list[-1]
            content += "\",\"".join(content_list) + "\",\"\""
#        content = repr(content)
        """
#        print content_list
#        content = ",".join(content_list)
#        print content
#        content = u"你"*440
        self.buddyMsgId += 1
        a ={"to":buddyId,"face":1,"content":"[\"%s\",[\"font\",%s]]"%(content,fontStyle),"msg_id":self.buddyMsgId,"clientid":self.clientid,"psessionid":self.psessionid}        
#        a ={"to":buddyId,"face":1,"content":'["%s",["font",{"name":"%s","size":"12","style":[0,0,0],"color":"16711680"}]]'%(content,u"黑体"),"msg_id":self.buddyMsgId,"clientid":self.clientid,"psessionid":self.psessionid}        
#        a = json.dumps(a)
        a = json.encoder.JSONEncoder().encode(a)
#        open("test.txt","w").write(str(a))
#        print a
        data={"clientid":self.clientid,"psessionid":self.psessionid,"r":a}
#        open("test.txt","w").write(urllib.urlencode(data))
        data = self.http.connect(url,data)
        if not data:
            return None
        data = json.loads(data)
#        print data
        return data


    def sendMsg2Group(self,groupId,content,fontStyle=None):
        """
        groupId:群uin
        content: 要发送的内容, unicode编码
        fontStyle: entity.FontStyle实例
        """

        if not fontStyle:
            fontStyle = self.fontStyle

        url="http://d.web2.qq.com/channel/send_qun_msg2"
        content = self.__convertMsg(content)
#        content = repr(content)[1:].strip("'")
#        print content
        self.groupMsg_id+=1
        a = {"group_uin":groupId,"content":"[\""+content+"\",[\"font\",%s]]"%fontStyle,"msg_id":self.groupMsg_id,"clientid":self.clientid,"psessionid":self.psessionid}
        a=json.dumps(a)
        data={"clientid":self.clientid,"psessionid":self.psessionid,"r":a}
        data = self.http.connect(url,data)
        if not data:
            return None
        data = json.loads(data)
#        print data
        url = "http://tj.qstatic.com/getlog?qqweb2=%s$groupmask$bottom$send&t=1377456226064"%self.qq
        return data

    
    #同意别人添加自己好友
    #参数 别人的QQ号 备注
    def allowAddFriend(self,qq,mname):

        url = "http://s.web2.qq.com/api/allow_and_add2"

        r = {"account":qq,"gid":0,"mname":"","vfwebqq":self.vfwebqq}
        r = json.dumps(r)
        data = {"r":r}
        data = self.http.connect(url,data)
        if not data:
            return None
        data = json.loads(data)
        return data

    
    #处理别人加群消息（必须是管理员才有效）
    #参数 reqUin 加群者的临时号码， groupUIn 加的群的临时号码，msg 拒绝理由，allow True是同意加群，False是不同意
    def handleAddGroupMsg(self,reqUin,groupUin,msg="",allow = True):

        msg = self.http.quote(msg)
        if allow:
            opType = 2
        else:
            opType = 3
        url = "http://d.web2.qq.com/channel/op_group_join_req?group_uin=%s&req_uin=%s&msg=%s&op_type=%d&clientid=%s&psessionid=%s"%(groupUin,reqUin,msg,opType,self.clientid,self.psessionid)
        data = self.http.connect(url)
        if not data:
            return None
        return json.loads(data)

    def deleteGroupMember(self, group_number, qq_number):

        """
        @return 
            int: 0 成功
            int: 3 成员不存在
            int: 7 权限不足
            int: 11 群号错误
            int: -1 网络错误
        """
        url = "http://qinfo.clt.qq.com/cgi-bin/qun_info/delete_group_member"

#        gc=29248149&bkn=1757978480&ul=843516495

#        print self.gtk
        post_data = {"gc":group_number, "ul": qq_number, "bkn": self.gtk}

        res_content = self.http.connect(url, post_data)
        if not res_content:
            return {"ec": -1}

        json_data = json.loads(res_content)

#        print json_data
        return json_data["ec"]
        
    def quitGroup(self,gcode):
        #退群

        url = "http://s.web2.qq.com/api/quit_group2"
        r = json.dumps({"gcode":gcode,"vfwebqq":self.vfwebqq})
        post_data = {"r": r}
        res = self.http.connect(url, post_data)
        if not res:
            return None
        result = json.loads(res)
        return result

    def changeGroupMessageFilter(self,group_uin="",state=0,all_state=0):

        """
        @param group_uin: 群临时号码
        @param state: 0 接收并提醒，1 接收不提醒，2 不接受
        @param all_state: 0 使用每群自身的消息设置，1 所有群接收并提示， 2 接收不提示，3 不接收
        """
        """
        retype:1
        app:EQQ
        itemlist:{"groupmask":{"3063251357":"2","3181386224":"1","cAll":3,"idx":1075,"port":25293}}
        vfwebqq:9ac2d0e9f567ad545d57dc336165e1b3a340e14d1534d802ecd7fdf363f380cbe7751f8f7e657e4e
        """
        url = "http://cgi.web2.qq.com/keycgi/qqweb/uac/messagefilter.do"

        self.groups_dic["gmasklist"][0]["mask"] = all_state
        groupmask = {"cAll":all_state,"idx":self.index,"port":self.port}
        for dic in self.groups_dic["gmasklist"]:
            uin = str(dic["gid"])
            if uin == "1000":
                continue
            if uin == group_uin:
                dic["mask"] = state
            mask = dic["mask"]

            groupmask[uin] = "%d"%mask
#        groupmask = json.JSONEncoder().encode(groupmask)
#        groupmask = json.dumps(groupmask).replace(" ","")
#        groupmask = str(groupmask).replace(" ","")
#        print groupmask
#        print urllib.urlencode(groupmask)
        itemlist = {"groupmask":groupmask}
        itemlist = json.dumps(itemlist)#.replace(" ","").replace("\\","")
#        itemlist = str(itemlist).replace(" ","")
#        print itemlist
#        print urllib.urlencode(itemlist)
#        print itemlist
        post_data = {"retype":"1","app":"EQQ","itemlist":itemlist,"vfwebqq":self.vfwebqq}
#        post_data = "retype=1&app=EQQ&itemlist=%s&vfwebqq=%s"%(urllib.quote(itemlist),self.vfwebqq)
#        print post_data
#        print urllib.urlencode(post_data)
        result = self.http.connect(url,post_data)
        if not result:
            return -1
        result = json.loads(result)
        return result["retcode"]


if "__main__" == __name__:
    qq_number = ""
    qq_pwd = ""
    qq = WebQQ(qq_number, qq_pwd)
    checkResult = qq.check()
    if checkResult == False:
        qq.verifyCode = raw_input("verify code:")
        

    print qq.login()
#    print qq.delete_group_member("291186448","379450326")
#    print qq.getFriends()
    print qq.getGroups()
#    qq.deleteGroupMember("149443938", "721011691")
    print qq.getGroupInfo(raw_input())
#    print qq.quit_group(gcode)
#    print qq.change_group_message_filter(all_state=2)
#    print qq.groups_dic["gmasklist"]
    print qq.sendTempMsgFromGroup(raw_input(),raw_input(),raw_input())
    while 1:
        print qq.getMsg()
    print qq.logout()
