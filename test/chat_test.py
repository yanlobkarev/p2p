from twisted.test import proto_helpers 
from twisted.trial import unittest
from twisted.internet import task
from chat_server import ChatServer
from test.util import *


class ChatTest(unittest.TestCase):
    def setUp(self):
       self.transport = proto_helpers.FakeDatagramTransport()
       self.server = ChatServer(prompt=MockedPrompt())
       self.server.transport = self.transport         

    def test_punchHole(self):
        self.server.datagramReceived('PUNCH', FAKE_ENDPOINT)
        resp, addr = self.transport.written[0]
        self.assertEqual(addr, FAKE_ENDPOINT)
        self.assertEqual(resp, 'HOLED')

    def test_broadcasteMessage(self):
        buddy = generate_endpoint()
        destination = [generate_endpoint() for x in xrange(10)]

        #   conect clients
        self.server.datagramReceived('CONNECT|127.0.0.1|3000|Buddy', buddy)        
        for d in destination:
            self.server.datagramReceived('CONNECT|127.0.0.1|3000|RandomName', d)

        #   post a message
        line = generate_string(20)
        self.server.datagramReceived('MSG|%s' % line, buddy)

        #   check message received by others
        broadcasted_line = 'MSG|Buddy|%s' % line
        for d in destination:
            self.assertTrue((broadcasted_line, d) in self.transport.written)


