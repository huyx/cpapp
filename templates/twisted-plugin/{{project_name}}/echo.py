# -*- coding: utf-8 -*-
from twisted.internet import protocol

class EchoProtocol(protocol.Protocol):
    def dataReceived(self, data):
        self.transport.write(data)

class TCPEcho(protocol.ServerFactory):
    protocol = EchoProtocol

class UDPEcho(protocol.DatagramProtocol):
    def datagramReceived(self, datagram, addr):
        self.transport.write(datagram, addr)
