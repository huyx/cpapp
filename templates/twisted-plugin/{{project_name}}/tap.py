# -*- coding: utf-8 -*-
from . import echo, ssh
from twisted.application import service, internet
from twisted.internet import reactor
from twisted.python import logfile, log, usage
from version import version
import settings

# HACK: 修改缺省的 LogFile 为 DailyLogFile
logfile.LogFile = logfile.DailyLogFile
# HACK: 修改 log 的缺省时间格式
log.FileLogObserver.timeFormat = '%Y-%m-%d %H:%M:%S'

class Options(usage.Options):
    pass

class RootService(service.MultiService):
    def TCPServer(self, port, factory, backlog=50, interface=''):
        service = internet.TCPServer(port, factory, backlog, interface)
        service.setServiceParent(self)

    def UDPServer(self, port, protocol, interface='', maxPacketSize=8192):
        service = internet.UDPServer(port, protocol, interface, maxPacketSize)
        service.setServiceParent(self)

    def TimerService(self, step, callable, *args, **kwargs):
        service = internet.TimerService(step, callable, *args, **kwargs)
        service.setServiceParent(self)

    def SSHServer(self, port, passwd, namespace=None):
        namespace = namespace or {}
        namespace.update(
            root=self,
            version=version,
        )
        service = internet.TCPServer(port, ssh.SSHFactory(passwd, namespace))
        service.setServiceParent(self)

def makeService(config):
    root = RootService()

    root.TCPServer(settings.ECHO_PORT, echo.TCPEcho())
    root.UDPServer(settings.ECHO_PORT, echo.UDPEcho())
    # root.TimerService(10, callable)

    # ssh 调试服务
    root.SSHServer(settings.SSH_PORT, settings.SSH_PASSWD)

    # 输出版本信息
    reactor.callWhenRunning(log.msg, version)

    return root
