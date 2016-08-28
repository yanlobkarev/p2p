from twisted.test import proto_helpers 
from twisted.trial import unittest
from twisted.internet import task
from base import BaseServer, BaseClient
from test.util import MockedPrompt


class BaseServerTest(unittest.TestCase):
    def setUp(self):
       self.transport = proto_helpers.FakeDatagramTransport()
       self.server = BaseServer(prompt=MockedPrompt())
       self.server.transport = self.transport
       self.FAKE_ENDPOINT = ('111.22.33.44', 4000)

    def _connect(self):
        msg = 'CONNECT|127.0.0.1|3000|Buddy'
        self.server.datagramReceived(msg, self.FAKE_ENDPOINT)

    def _is_connected(self):
        return self.FAKE_ENDPOINT in self.server.clients        

    def test_connect(self):
        self._connect()
        resp, addr = self.transport.written[0]
        self.assertEqual(resp, 'RESP|SUCCESS|')
        self.assertEqual(addr, self.FAKE_ENDPOINT)
        self.assertTrue(self._is_connected())

    def test_ignoreExcessConnects(self):
        for x in xrange(10):
            self._connect()
        
        self.assertEqual(len(self.server.clients), 1)
    
    def test_timedDisconnect(self):
        self._connect() 

        #   still connected after 30 heartbeats
        for x in xrange(30):
            self.server.sendHeartbeat()
        self.assertTrue(self._is_connected())

        #   disconnected after 31th heartbeat
        self.server.sendHeartbeat()
        self.assertFalse(self._is_connected())


class BaseClientTest(unittest.TestCase):
    def setUp(self):
       self.transport = proto_helpers.FakeDatagramTransport()
       self.client = BaseClient()
       self.client.transport = self.transport
       self.FAKE_ENDPOINT = ('111.22.33.44', 4000)

    def test_heartbeat(self):
        self.client.datagramReceived('HEART', self.FAKE_ENDPOINT)
        resp, addr = self.transport.written[0] 
        self.assertEqual(resp, 'BEAT')



