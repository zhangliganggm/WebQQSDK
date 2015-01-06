#coding=UTF8
__doc__ = """
"""

import os
import sys

__curPath = os.path.dirname(__file__)
__parPath = os.path.dirname(__curPath)

if not __parPath:
    sys.path.append("..")
else:
    sys.path.append(__parPath)

import webqqsdk
webqqsdk = webqqsdk

class QQPlugin:
    """
    self.qqClient: webqqsdk.WebQQClient的实例,里面包含了所有WebQQ api
    """

    def __init__(self):

        self.qqClient = None

    def setupQQInstance(self,qq):

        self.qqClient = qq

    def install(self):
        """
        插件安装时被调用
        """

    def uninstall(self):
        """
        插件卸载时被调用
        """

    def reinstall(self):
        """
        插件在不重启主程序的状态下重新安装时
        先是调用install再调用此函数
        """
