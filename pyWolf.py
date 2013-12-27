# Import modules
import socket

# Functions to check for different user inputs
# ---------------------------------------------------------------------------------- #

# Respond to pings
def checkPing():
	if MSG.find('PING :') != -1:
		IRC_SOCK.send('PONG :pingis\n')

# Sends messages..
def sendMsg(TARGET, MSG):
	IRC_SOCK.send('PRIVMSG '+ TARGET +' :'+ MSG +'\n')

# Checks for new messages
def checkMessages():
	IRC_MSG = IRC_SOCK.recv(2048)
	IRC_MSG = IRC_MSG.strip('\n\r')
	print(IRC_MSG)
	return IRC_MSG

def getNick(MSG):
	EX_INDEX = MSG.find('!')
	NICK_NAME = MSG[1:EX_INDEX]
	return NICK_NAME

# Check if someone wants to join
def checkJoin(MSG):
	if MSG.find(COMMANDS[2]) != -1:
		JOINING_USER = getNick(MSG)
		if not JOINING_USER in JOINED_USERS:
			JOINED_USERS.append(JOINING_USER)
			sendMsg(CHANNEL, '%s has joined!' % JOINING_USER)

# Check if someone wants to leave		
def checkLeave(MSG):
	if MSG.find(COMMANDS[3]) != -1:
		LEAVING_USER = getNick(MSG)
		if LEAVING_USER in JOINED_USERS:
			JOINED_USERS.remove(LEAVING_USER)
			sendMsg(CHANNEL, '%s has left!' % LEAVING_USER)

# Check to see if a joined user has changed their nickname			
def checkNick(MSG):
	if MSG.find('NICK') != -1:
		LAST_NICK = getNick(MSG)
		NICK_POSITION = MSG.find('NICK :') + 6
		NEW_NICK = MSG[NICK_POSITION:len(MSG)]
		if LAST_NICK in JOINED_USERS:
			sendMsg(CHANNEL, 'Joined user, %s, has changed their nick. New nick, %s, added to paticipants.' % (LAST_NICK, NEW_NICK))
			JOINED_USERS.remove(LAST_NICK).append(NEW_NICK)

# Check to see if someone has requested a list of players			
def checkList(MSG):
	if MSG.find(COMMANDS[1]) != -1:
		PLAYER_LIST = ', '.join(JOINED_USERS)
		sendMsg(CHANNEL, 'Players: ' + PLAYER_LIST)

# Check if someone has requested help		
def checkHelp(MSG):
	if MSG.find(COMMANDS[4]) != -1:
		SORTED_COMMANDS = sorted(COMMANDS)
		COMMAND_LIST = ' '.join(SORTED_COMMANDS)
		HELP_USER = getNick(MSG)
		sendMsg(HELP_USER, COMMAND_LIST)
# -------------------------------------------------------------------------------------------------- #

# Sets up the game waiting for someone to start it
def initialize():
	while 1:
		MESSAGE = checkMessages()
		
		checkPing()
		
		# Check to see if someone is attempting to start a new game
		# If more than three people have joined, start the game. Otherwise, send a message to the channel.
		if MESSAGE.find(COMMANDS[0]) != -1:
			if len(JOINED_USERS) <= 3:
				sendMsg(CHANNEL, 'Not enough players (%i) to start a new game' % len(JOINED_USERS))
			else:
				newGame(len(JOINED_USERS))
		
		checkJoin(MESSAGE)

		checkLeave(MESSAGE)
		
		checkNick(MESSAGE)
		
		checkList(MESSAGE)
		
		checkHelp(MESSAGE)
		
#def nightRound():

#def dayRound():

def newGame(playercount):
	# TODO: START A NEW GAME
	sendMsg(CHANNEL, 'This is where I would start the game...')

# Channel and Nick settings
SERVER = 'irc.freenode.net'
CHANNEL = '#TimeWastePool'
BOT_NICK = 'TWP_Wolf'

# Connect to channel 
IRC_SOCK = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
IRC_SOCK.connect((SERVER, 6667))
IRC_SOCK.send('USER '+ BOT_NICK +' '+ BOT_NICK +' '+ BOT_NICK +' :This bot moderates games of Werewolf\n')
IRC_SOCK.send('NICK '+ BOT_NICK +'\n')
IRC_SOCK.send('JOIN '+ CHANNEL +'\n')
sendMsg(CHANNEL, 'Hi, I\'m ' + BOT_NICK + '. I moderate games of Werewolf! If you want to join the game, say "!join". For a list of commands, say "!helpme"')

# List of commands available to channel
COMMANDS = ['!startwolf','!list','!join','!leave','!helpme','!quit']

# List of joined users
JOINED_USERS = []

initialize()