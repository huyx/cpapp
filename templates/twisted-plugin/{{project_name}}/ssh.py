# -*- coding: utf-8 -*-
from twisted.application import strports
from twisted.conch import manhole, manhole_ssh
from twisted.conch.insults import insults
from twisted.conch.ssh import factory
from twisted.cred import portal, checkers
from twisted.internet import reactor
from twisted.internet.error import ProcessTerminated
from twisted.python import log, failure

class DebugRealm(manhole_ssh.TerminalRealm):
    def __init__(self, namespace):
        self.chainedProtocolFactory = lambda :\
            insults.ServerProtocol(manhole.ColoredManhole, namespace)

class SSHFactory(manhole_ssh.ConchFactory):
    def __init__(self, passwd, namespace=None):
        namespace = namespace or {}
        realm = DebugRealm(namespace)
        checker = checkers.FilePasswordDB(passwd)
        self.portal = portal.Portal(realm, [checker])
