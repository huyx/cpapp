# -*- coding: utf-8 -*-
from . import ssh, share
from .version import version
from twisted.application import service, internet
from twisted.internet import reactor
from twisted.python import logfile, log, usage
import settings
import sys

# HACK: 修改缺省编码
reload(sys)
encoding = 'cp936' if sys.platform == 'win32' else 'utf-8'
sys.setdefaultencoding(encoding)

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
        return service

    def UDPServer(self, port, protocol, interface='', maxPacketSize=8192):
        service = internet.UDPServer(port, protocol, interface, maxPacketSize)
        service.setServiceParent(self)
        return service

    def TimerService(self, step, callable, *args, **kwargs):
        service = internet.TimerService(step, callable, *args, **kwargs)
        service.setServiceParent(self)
        return service

    def SSHServer(self, port, passwd, namespace=None):
        namespace = namespace or {}
        namespace.update(
            root=self,
            version=version,
            share=share,
        )
        service = internet.TCPServer(port, ssh.SSHFactory(passwd, namespace))
        service.setServiceParent(self)
        return service

def startup():
    # 输出版本信息
    log.msg('version:', version)

    # 输出配置信息
    for k in dir(settings):
        if k == k.upper():
            log.msg('settings: %s=%r' % (k, getattr(settings, k)))

def shutdown():
    log.msg(u'Shuting down ...')

def makeService(config):
    root = RootService()

    root.TCPServer(settings.ECHO_PORT, share.tcp_echo)
    root.UDPServer(settings.ECHO_PORT, share.udp_echo)
    # root.TimerService(10, callable)

    # ssh 调试服务
    root.SSHServer(settings.SSH_PORT, settings.SSH_PASSWD)

    # 注册事件处理器
    reactor.addSystemEventTrigger('after', 'startup', startup)
    reactor.addSystemEventTrigger('before', 'shutdown', shutdown)

    return root
