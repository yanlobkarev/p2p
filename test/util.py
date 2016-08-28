from random import randrange, choice
import string

FAKE_ENDPOINT = ('111.22.33.44', 4000)

class MockedPrompt(object):
    def log(self, msg): pass
    def logError(self, msg): pass
    def logChatMsg(self, name, msg): pass


def generate_endpoint():
    IP = '.'.join([str(randrange(0, 256)) for x in range(4)])
    port = randrange(1, 65536)
    return (IP, port)


def generate_string(length):
    return ''.join(choice(string.lowercase) for i in range(length))
