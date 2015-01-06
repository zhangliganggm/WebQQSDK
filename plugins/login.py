# -*- encoding:UTF8 -*-
import plugin
MsgEvent = plugin.webqqsdk.MsgEvent

class Plugin(plugin.QQPlugin):

    def install(self):

        event = MsgEvent(self.inputVerifyCode)
        self.qqClient.addNeedVerifyCodeEvent(event)
        self.qqClient.addLoginSuccessEvent(MsgEvent(self.loginSuccess))
        self.qqClient.addLoginFailedEvent(MsgEvent(self.loginFailed))
        self.qqClient.addLogoutEvent(MsgEvent(self.logout))
#        self.qqClient.getGroups()
#        print self.qqClient.qqUser.groups
#        print self.qqClient.qqUser.groups[977514971].qq

    def inputVerifyCode(self,msg):
        # 输入验证码
        code = raw_input(u"输入验证码:".encode("gbk"))
        self.qqClient.inputVerifyCode(code)

    def loginSuccess(self,msg):
#        print self.qqClient.qqUser.groups
#        print self.qqClient.getMsg() # 处理离线消息
        print u"登录成功"

    def loginFailed(self,msg):
        print u"登录失败",msg.msg

    def logout(self,msg):
        print u"掉线了"
        self.qqClient.login()
