from twisted.test import proto_helpers 
from twisted.trial import unittest
from twisted.internet import task
from signal_server import SignalServer
from test.util import *


class SignalServerTest(unittest.TestCase):
    def setUp(self):
        self.transport = proto_helpers.FakeDatagramTransport()
        self.server = SignalServer(prompt=MockedPrompt())
        self.server.transport = self.transport

    def _connect(self, fromEndpoint=None):
        msg = 'CONNECT|127.0.0.1|1111|Buddy'
        self.server.datagramReceived(msg, fromEndpoint or generate_endpoint())
        
    def test_connectChatServer(self):
        self.assertEqual(self.server.chat_server, None)
        chat_server = generate_endpoint()

        #   expecting connected chat server
        #   to be available as property
        self._connect(chat_server)
        self.assertEqual(self.server.chat_server, chat_server)

    def test_ignoreAnotherChatServers(self):
        self._connect()
        self._connect(generate_endpoint())

        #   error if one chat server is already 
        #   available (we don't need ianothers)
        resp, _ = self.transport.written[-1]
        self.assertEqual(resp, 'RESP|ERROR|ALREADY_HAVE_ONE_CHAT_SERVER')

    def test_initiatePeersConnection(self):
        chat_client = generate_endpoint()
        msg = 'INITIATE_PEER_CONNECTION|127.0.0.2|2222'
        self.server.datagramReceived(msg, chat_client)

        #   error if no chat server peer
        resp, _ = self.transport.written[-1]
        self.assertEqual(resp, 'RESP|ERROR|NO_SERVER_PEER_AVAILABLE')

        #   expecting coordination if both chat 
        #   peers (client & server) available
        chat_server = generate_endpoint()
        self._connect(chat_server)
        self.server.datagramReceived(msg, chat_client)
        d1, d2 = self.transport.written[-2:]
        self.assertEqual(set([d1, d2]), set([
            ('INITIATE_PEER_CONNECTION|%s|%s|127.0.0.2|2222' % chat_client, chat_server),
            ('INITIATE_PEER_CONNECTION|%s|%s|127.0.0.1|1111' % chat_server, chat_client),           ]))        

        #   error if peer tries to connect to itself
        msg = 'INITIATE_PEER_CONNECTION|127.0.0.1|1111'
        self.server.datagramReceived(msg, chat_server)
        resp, _ = self.transport.written[-1]
        self.assertEqual(resp, 'RESP|ERROR|CANT_INITIATE_CONNECTION_TO_SELF')

