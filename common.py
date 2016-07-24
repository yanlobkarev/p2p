from socket import *
import inspect

#   There is deployed version
#   of `signal_server.py`.
SIGNAL_SERVER_IP = '107.172.138.8' 
SIGNAL_SERVER_PORT = 8888


def unpack_datagramm_args(func):
    spec = inspect.getargspec(func)
    args_count = len(spec.args)
    PARAMS = '_'.join(spec.args[2:]).upper()  # without `self, addr`
    ERR_MSG = 'RESP|ERROR|WRONG_PARAMS:SHOULD_BE %s' % PARAMS

    def wrapped(self, addr, data):
        args = data.strip().split('|')
        args.pop(0)
        args = [self, addr] + args
        if len(args) != args_count:
            self.transport.write(ERR_MSG, addr)
        else:
            func(*args)
    return wrapped


def get_localhost_ip():
    s = socket(AF_INET, SOCK_DGRAM)
    # connecting to a UDP address, doesn't send packet
    s.connect(('8.8.8.8', 1)) 
    ip = s.getsockname()[0]
    s.close()
    return ip




