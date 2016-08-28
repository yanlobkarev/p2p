#!python
from twisted.internet.protocol import DatagramProtocol
from twisted.internet import task, stdio
from common import unpack_datagramm_args
from prompt import ColoredPrompt
import socket


class BaseServer(DatagramProtocol, object):
    def __init__(self, prompt=None):
        self.clients = {}
        self.prompt = prompt or ColoredPrompt(prompt='>')

    def startProtocol(self):
        self.loop = task.LoopingCall(self.sendHeartbeat)
        self.loop.start(0.5)

    def stopProtocol(self):
        self.loop.stop()

    def datagramReceived(self, data, addr):
        if data.startswith('CONNECT'):
            self.handleConnect(addr, data)
        elif data.startswith('BEAT'):
            self.handleHeartbeat(addr)
        else:
            super(BaseServer, self).datagramReceived(data, addr)

    @unpack_datagramm_args
    def handleConnect(self, addr, private_ip, private_port, name):
        if addr in self.clients:
            return

        ep = {  
            'name': name, 
            'private_endpoint': (private_ip, private_port)
        }
        self.clients[addr] = ep
        self.transport.write('RESP|SUCCESS|', addr)
        self.prompt.log("connected %s - %s" % (addr, ep))

    def sendHeartbeat(self):
        for endpoint, client in self.clients.copy().iteritems():
            missed = client.get('missed_beats', 1)
            if missed > 30:
                del self.clients[endpoint]
                self.prompt.log("disconnected %s" % str(endpoint))
            else:    
                client['missed_beats'] = missed + 1
                self.transport.write('HEART', endpoint)

    def handleHeartbeat(self, addr):
        if addr not in self.clients:
            return

        client = self.clients[addr]
        client['missed_beats'] = 0


class BaseClient(DatagramProtocol, object):
    def datagramReceived(self, data, addr):
        if data.startswith('RESP'):
            self.handleResponse(addr, data)
        elif data.startswith('HEART'):
            self.transport.write('BEAT', addr)
        else:
            super(BaseClient, self).datagramReceived(data, addr)

    def connectToServer(self, server_endpoint, private_endpoint):
        private_ip, private_port = private_endpoint
        name = BaseClient.getClientName()
        msg = b'CONNECT|%s|%s|%s' % (private_ip, private_port, name)
        self.transport.write(msg, server_endpoint)

    @staticmethod
    def getClientName():
        return socket.gethostname() or 'Unknown'

    @unpack_datagramm_args
    def handleResponse(self, addr, status, detailed_message):
        if status == 'ERROR':
            self.prompt.logError(detailed_message)


