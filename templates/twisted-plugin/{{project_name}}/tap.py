# -*- coding: utf-8 -*-
from twisted.application import service, internet
from twisted.python import logfile, log, usage
from {{project_name}} import echo

import settings

# HACK: 修改缺省的 LogFile 为 DailyLogFile
logfile.LogFile = logfile.DailyLogFile
# HACK: 修改 log 的缺省时间格式
log.FileLogObserver.timeFormat = '%Y-%m-%d %H:%M:%S'

class Options(usage.Options):
    pass

class RootService(service.MultiService):
    def TCPServer(self, *args, **kwargs):
        server = internet.TCPServer(*args, **kwargs)
        server.setServiceParent(self)

    def UDPServer(self, *args, **kwargs):
        server = internet.UDPServer(*args, **kwargs)
        server.setServiceParent(self)

def makeService(config):
    root = RootService()

    root.TCPServer(settings.ECHO_PORT, echo.TCPEcho())
    root.UDPServer(settings.ECHO_PORT, echo.UDPEcho())

    return root
