#!python
from twisted.internet import reactor
from common import get_localhost_ip
from common import SIGNAL_SERVER_IP, SIGNAL_SERVER_PORT
from common import unpack_datagramm_args
from base import BaseClient, BaseServer


class ChatServer(BaseClient, BaseServer):
    def __init__(self, signal_server=None, private=None):
        super(ChatServer, self).__init__()
        self.signal_server = signal_server
        self.private = private

    def startProtocol(self):
        super(ChatServer, self).startProtocol()
        self.connectToServer(self.signal_server, self.private)

    def datagramReceived(self, data, addr):
        data = data.strip()
        if data.startswith(b'INITIATE_PEER_CONNECTION'):
            self.handleInitiatePeerConnection(addr, data)
        elif data.startswith(b'PUNCH'):
            self.transport.write(b'HOLED', addr)
        elif data.startswith(b'MSG'):
            self.handleChatMessage(addr, data)
        else:
            super(ChatServer, self).datagramReceived(data, addr)

    @unpack_datagramm_args
    def handleInitiatePeerConnection(self, _, public_ip, public_port, private_ip, private_port):
        #   Assume worst case- when client 
        #   peer is behind symmetric NAT.        
        for p in xrange(1, 2**16-1):
            self.transport.write('X', (public_ip, p))

        #   Also send one packet- in case 
        #   peer in the same private network
        #   as a server peer.
        private_endpoint = (private_ip, int(private_port))
        self.transport.write('X', private_endpoint)

    @unpack_datagramm_args
    def handleChatMessage(self, addr, line):
        client = self.clients.get(addr)
        if client is None:
            return

        name = client.get('name')
        msg = 'MSG|%s|%s' % (name, line)
        for endpoint, client in self.clients.iteritems():
            if addr != endpoint:
                self.transport.write(msg, endpoint)


if __name__ == '__main__':
    PORT = 8888
    local = (get_localhost_ip(), PORT)
    signal = (SIGNAL_SERVER_IP, SIGNAL_SERVER_PORT)

    print "Starting Chat Server on port %s" % PORT
    cs = ChatServer(signal_server=signal, private=local)
    reactor.listenUDP(PORT, cs)
    reactor.run()


