#coding=UTF8

import sys
import traceback
import time
import webqqsdk

WebQQClient = webqqsdk.WebQQClient

class Main(WebQQClient):
    """
    self.startTime: int, 程序启动的时间戳
    """

    def __init__(self,qq,pwd):

        WebQQClient.__init__(self,qq,pwd)

        self.startTime = time.time()

        self.pluginsPath = "plugins"
        self.pluginListPath = self.pluginsPath + "/PluginList.txt"
        sys.path.append(self.pluginsPath)

        self.pluginNames = [] # 每项元素是插件所在的文件的文件名
        self.pluginModules = [] # 每项元素是插件模块
        self.plugins = [] # 每项元素是Plugin实例

        self.readPlugins()
        self.installPlugins()

        self.login()
#        self.debug()

    def reInstallPlugins(self):

        self.uninstallPlugins()
        self.readPlugins()

        for module in self.pluginModules:
            reload(module)

        self.installPlugins()
        for plugin in self.plugins:
            plugin.reinstall()

    def readPlugins(self):

        self.pluginModules = []
        self.pluginNames = []
        with open(self.pluginListPath) as f:
            data = f.readlines()

        pluginNames = [i.strip() for i in data if (not (i.strip().startswith("#")) and i.strip())]
        for i in pluginNames:
            self.pluginNames.append(i)
            try:
                self.pluginModules.append(__import__(i))
            except:
                traceback.print_exc()

        
#        print self.pluginNames

    def installPlugins(self):

#        print self.pluginModules
        for plugin in self.pluginModules:
            try:
                p = plugin.Plugin()
                p.setupQQInstance(self)
                p.install()
                self.plugins.append(p)
            except:
                traceback.print_exc()
#        print u"main",self.friendMsgEvents

    def uninstallPlugins(self):
        """
        卸载所有插件，实际上调用的是插件的uninstall方法
        """
        for plugin in self.plugins:
            try:
                plugin.uninstall()
            except:
                traceback.print_exc()

        self.clearEvents()
        self.plugins = []


if __name__ == "__main__":

    test = Main(raw_input("QQ:"),raw_input("password:"))
