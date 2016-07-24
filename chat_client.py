#!python
from twisted.internet import reactor, stdio
from common import get_localhost_ip, unpack_datagramm_args
from common import SIGNAL_SERVER_IP, SIGNAL_SERVER_PORT
from prompt import ColoredPrompt
from base import BaseClient
import sys


class ChatClient(BaseClient): 
    def __init__(self, signal_server=None, private=None):
        super(ChatClient, self).__init__()
        self.private = private
        self.signal_server = signal_server
        
        self.prompt = ColoredPrompt(sender=self, prompt=self.getClientName())
        stdio.StandardIO(self.prompt) 

        self.chat_server_endpoint = None
        self.punched_endpoints = []
        self.punches = []

    def sendLine(self, line):
        if self.chat_server_endpoint is None:
            return

        line = line.strip()
        line = line.replace('|', '_')  # replace special characters
        msg = 'MSG|%s' % line
        self.transport.write(msg, self.chat_server_endpoint)

    def startProtocol(self):
        self.ensureConnectionToChatServer()
 
    def datagramReceived(self, data, addr):
        if data.startswith(b'INITIATE_PEER_CONNECTION'):
            self.handleInitiatePeerConnection(addr, data)
        elif data.startswith(b'HOLED'):
            self.handlePuncholed(addr)
        elif data.startswith('MSG'):
            self.handleChatMessage(addr, data)
        else:
            super(ChatClient, self).datagramReceived(data, addr)

    def ensureConnectionToChatServer(self):
        if self.chat_server_endpoint is None:
            msg = b'INITIATE_PEER_CONNECTION|%s|%s' % self.private
            self.transport.write(msg, self.signal_server)

    @unpack_datagramm_args
    def handleInitiatePeerConnection(self, _, public_ip, public_port, private_ip, private_port):
        private_endpoint = (private_ip, int(private_port))
        public_endpoint = (public_ip, int(public_port))

        self.prompt.log('connecting to following addresses %s, %s.' % (private_endpoint, public_endpoint))

        PUNCHOLING_TIME = 3  # 3s.
        PACKETS_PER_SEC = 100
        self.punched_endpoints = [private_endpoint, public_endpoint]

        self.clearPunches()
        for i in xrange(PUNCHOLING_TIME * PACKETS_PER_SEC):
            time = float(i)/PACKETS_PER_SEC 
            deferred = reactor.callLater(time, self.punch, public_endpoint)
            self.punches.append(deferred)
        self.punches.append(reactor.callLater(0.1, self.punch, private_endpoint))

        #   reconnect recursion
        reactor.callLater(PUNCHOLING_TIME, self.ensureConnectionToChatServer)        

    def handlePuncholed(self, addr):
        if addr not in self.punched_endpoints:
            return
        
        self.prompt.log("connected to %s." % str(addr))
        self.punched_endpoints = []
        self.clearPunches()
        self.chat_server_endpoint = addr
        self.connectToServer(addr, self.private)

    @unpack_datagramm_args
    def handleChatMessage(self, addr, name, msg):
        if addr == self.chat_server_endpoint:
            self.prompt.logChatMsg(name, msg)

    def punch(self, endpoint):
        self.transport.write('PUNCH', endpoint)

    def clearPunches(self):
        for punch in self.punches:
            if punch.active():
                punch.cancel()
        self.punches = []        


if __name__ == '__main__':
    PORT = 8889
    try:
        PORT = int(sys.argv[1])
    except (IndexError, ValueError):
        pass

    local = (get_localhost_ip(), PORT)
    signal = (SIGNAL_SERVER_IP, SIGNAL_SERVER_PORT)

    cc = ChatClient(signal_server=signal, private=local)

    print "Starting Chat Client on port %s" % PORT
    reactor.listenUDP(PORT, cc)
    reactor.run()


