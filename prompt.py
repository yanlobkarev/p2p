#!python
from twisted.internet import reactor
from twisted.protocols.basic import LineReceiver


OKBLUE = '\033[94m'
OKGREEN = '\033[92m'
FAIL = '\033[91m'
ENDC = '\033[0m' 
ERASE_2END = '\x1b[K'


class ColoredPrompt(LineReceiver, object):
    from os import linesep as delimiter

    def __init__(self, sender=None, prompt='You'):
        self.sender = sender
        self.prompt = prompt

    def lineReceived(self, line):
        self._writePrompt()
        if self.sender:
            reactor.callLater(0, self.sender.sendLine, line)
        
    def log(self, msg):
        self._erasePrompt()
        self.transport.write(OKBLUE + msg + ENDC + "\n")
        self._writePrompt()

    def logChatMsg(self, name, msg):
        self._erasePrompt()
        self.transport.write("%s%s%s %s\n" % (OKBLUE, name, ENDC, msg))
        self._writePrompt()

    def logError(self, msg):
        self._erasePrompt()
        self.transport.write("%s%s%s %s\n" % (FAIL, 'ERROR', ENDC, msg))
        self._writePrompt()

    def _erasePrompt(self):
        backward_coursor = '\x1b[%dD' % len(self._prompt)
        self.transport.write(backward_coursor + ERASE_2END)

    def _writePrompt(self):
        self.transport.write(self._prompt)

    @property
    def _prompt(self):
        return OKGREEN + self.prompt + ENDC + ' '


