#!/usr/bin/python
from twisted.internet import reactor
from common import unpack_datagramm_args
from base import BaseServer


class SignalServer(BaseServer):
    def datagramReceived(self, data, addr):
        data = data.strip()
        if data.startswith('INITIATE_PEER_CONNECTION'):
            self.handleInitiatePeerConnection(addr, data)
        else:
            super(SignalServer, self).datagramReceived(data, addr)

    @property
    def chat_server(self):
        endpoints = self.clients.keys()
        return endpoints[0] if endpoints else None

    @property
    def chat_server_info(self):
        infos = self.clients.values()  
        return infos[0] if infos else None

    def handleConnect(self, addr, *args):
        if (self.chat_server is None or     # No chat servers at the moment
           self.chat_server == addr):       # Or chat server had been restarted
            super(SignalServer, self).handleConnect(addr, *args)
        else:
            #   Permit more than one chat 
            #   servers at the same time.
            self.transport.write('RESP|ERROR|ALREADY_HAVE_ONE_CHAT_SERVER', addr)

    @unpack_datagramm_args
    def handleInitiatePeerConnection(self, peer, private_ip, private_port):
        if self.chat_server is None:
            self.transport.write('RESP|ERROR|NO_SERVER_PEER_AVAILABLE', peer)
            return
        elif self.chat_server == peer:
            self.transport.write('RESP|ERROR|CANT_INITIATE_CONNECTION_TO_SELF', peer)
            return

        self.prompt.log('Initiated peer-to-peer connection from %s' % str(peer))

        #   one for chat_server
        public_ip, public_port = peer
        msg = 'INITIATE_PEER_CONNECTION|%s|%s|%s|%s' % \
                (public_ip, public_port, private_ip, private_port)
        self.transport.write(msg, self.chat_server)

        #   one for chat_client
        public_ip, public_port = self.chat_server
        private_ip, private_port = self.chat_server_info.get('private_endpoint', (None, None))
        msg = 'INITIATE_PEER_CONNECTION|%s|%s|%s|%s' % \
                (public_ip, public_port, private_ip, private_port)
        self.transport.write(msg, peer)


if __name__ == '__main__':
    ss = SignalServer()
    print "Starting UDP Signal Server server on port 8888"
    reactor.listenUDP(8888, ss)
    reactor.run()


