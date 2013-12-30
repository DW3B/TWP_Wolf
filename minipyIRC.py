import socket, sys

class pyIRC:
    """Minimal implementation of irc protocol
    
    Meant for use with TWP_Wolf"""

    required = ('nick','chan','serv','msg')
    PORT = 6667
    autoJoin = False

    def __init__(self, **args):
        self.data = args
        self.sock = None
        
        if 'autojoin' in self.data:
            self.autoJoin = True

        if 'port' not in self.data:
            self.data["port"] = self.PORT

        for r in self.required:
            if r not in self.data:
                sys.stderr.write('%s is required argument' % r)
                exit(1)

        self.connect()

    def sendRaw(self, msg):
        """Send somewhat raw irc strings.

        Not entirely raw:
        * newline is appended
        * string is passed through encode()

        Returns with the value of socket.send or False"""
        if self.sock is None:
            sys.stderr.write('No socket open?\n')
            return False

        try:
            self.sock.send(msg.encode() +b'\n')
        except:
            e = sys.exc_info()[0]
            sys.stderr.write('Exception: %s\n' % e)
            return False

        return True

    def sendMsg(self, target, msg):
        "Wrapper function for PRIVMSG's using sendRaw()"
        return self.sendRaw('PRIVMSG %s :%s' % (target, msg))

    def checkPing(self, msg):
        """Respond to IRC PING requests.

        Returns with value of sendRaw() or False"""
        if msg.find('PING :') != -1:
            return self.sendRaw('PONG :pingis')
        else:
            return False

    def getNick(self, msg):
        """Extract nickname string from data recieved via checkMessages()

        Returns substring of msg offset by location of ! literal character"""
        exIndex = msg.find('!')
        return msg[1:exIndex]

    def checkMessages(self):
        """Invoke socket.recv using 2048 buffer.
        Responds to any IRC PINGs found within buffer using checkPing()

        Strips newline and carriage returns before returning buffer"""
        msg = self.sock.recv(2048).decode().strip('\n\r')
        print(msg)
        self.checkPing(msg)
        return msg

    def join(self):
        "Wrapper for IRC JOIN using sendRaw()"
        return self.sendRaw( 'JOIN %s' % self.data["chan"] )

    def connect(self):
        """Connect to socket using data defined during instantiation.

        Sends the following using sendRaw():
            * USER
            * NICK
        before invoking join() if autoJoin is True.
        
        Returns socket object"""
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect( (self.data["serv"], self.data["port"]) )
        self.sendRaw( 'USER {0} {0} {0} :{1}'.format(self.data["nick"], self.data["msg"]) )
        self.sendRaw( 'NICK {0}'.format(self.data["nick"]) )
        if self.autoJoin is True:
            self.join()

        return self.sock
