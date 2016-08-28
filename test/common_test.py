from twisted.trial import unittest
from common import unpack_datagramm_args
from twisted.test import proto_helpers 
from twisted.trial import unittest
from twisted.internet import task
from base import BaseServer, BaseClient
from test.util import generate_endpoint


class Proto:
    @unpack_datagramm_args
    def concat(_, __, a, b):
        return a + b

    @unpack_datagramm_args
    def do_raise(_, __, a, b):
        raise RuntimeError

    @unpack_datagramm_args
    def do_something(self, addr, cmd, boat, flower, _2016, Penny):
        self.transport.write('SUCCESS', addr)


class UnpackDatagramTest(unittest.TestCase):
    def setUp(self):
        self.proto = Proto()
        self.transport = self.proto.transport = \
                proto_helpers.FakeDatagramTransport()
        self.endpoint = generate_endpoint()
        
    def test_decoratedReturn(self):
        res = self.proto.concat(self.endpoint, 'ADD|Hello|World')
        self.assertEqual(res, 'HelloWorld')

    def test_decoratedRaises(self):
        with self.assertRaises(RuntimeError): 
            self.proto.do_raise(self.endpoint, '_||')

    @property
    def written(self):
        resp, _ = self.transport.written[-1]
        return resp

    def test_errorMessage(self):
        error_message = \
                'RESP|ERROR|WRONG_PARAMS:SHOULD_BE CMD,BOAT,FLOWER,_2016,PENNY'

        self.proto.do_something(self.endpoint, '')
        self.assertEqual(self.written, error_message)

        self.proto.do_something(self.endpoint, 'CMD|1|2|3|4|5|6')
        self.assertEqual(self.written, error_message)

        self.proto.do_something(self.endpoint, 'CMD|1|2|3|4')
        self.assertEqual(self.written, error_message)

        self.proto.do_something(self.endpoint, 'CMD|1|2|3|4|5')
        self.assertEqual(self.written, 'SUCCESS')


