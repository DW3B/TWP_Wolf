# Import modules
import random
import minipyIRC as IO

# Functions to check for different user inputs
# ---------------------------------------------------------------------------------- #

# Check if someone wants to join
def checkJoin(msg):
	if msg.find(commands[2]) != -1:
		joiningUser = ioh.getNick(msg)
		if not joiningUser in joinedUsers:
			joinedUsers.append(joiningUser)
			ioh.sendMsg(channel, '%s has joined!' % joiningUser)

# Check if someone wants to leave		
def checkLeave(msg):
	if msg.find(commands[3]) != -1:
		leavingUser = ioh.getNick(msg)
		if leavingUser in joinedUsers:
			joinedUsers.remove(leavingUser)
			ioh.sendMsg(channel, '%s has left!' % leavingUser)

# Check to see if a joined user has changed their nickname			
def checkNick(msg):
	if msg.find('NICK') != -1:
		lastNick = ioh.getNick(msg)
		nickPosition = msg.find('NICK :') + 6
		newNick = msg[nickPosition:len(msg)]
		if lastNick in joinedUsers:
			ioh.sendMsg(channel, 'Joined user, %s, has changed their nick. New nick, %s, added to paticipants.' % (lastNick, newNick))
			joinedUsers.remove(lastNick).append(newNick)

# Check to see if someone has requested a list of players			
def checkList(msg):
	if msg.find(commands[1]) != -1:
		playerList = ', '.join(joinedUsers)
		ioh.sendMsg(channel, 'Players: ' + playerList)

# Check if someone has requested help		
def checkHelp(msg):
	if msg.find(commands[4]) != -1:
		sortedCommands = sorted(commands)
		commandList = ' '.join(sortedCommands)
		helpUser = ioh.getNick(msg)
		ioh.sendMsg(helpUser, commandList)
# -------------------------------------------------------------------------------------------------- #

# Sets up the game waiting for someone to start it
def initialize():
	while 1:
		message = ioh.checkMessages()
		
		# Check to see if someone is attempting to start a new game
		# If more than three people have joined, start the game. Otherwise, send a message to the channel.
		if message.find(commands[0]) != -1:
			if len(joinedUsers) <= 3:
				ioh.sendMsg(channel, 'Not enough players (%i) to start a new game' % len(joinedUsers))
			else:
				return len(joinedUsers)
				
		checkJoin(message)
		checkLeave(message)	
		checkNick(message)	
		checkList(message)
		checkHelp(message)
		
def nightRound(werewolves, villagers):
	for wolf in werewolves:
		ioh.sendMsg(wolf, 'Choose your victim...')

	wolfVotes = {}
		
	while 1:
		message = ioh.checkMessages()
		
		for wolf in werewolves:
			if ioh.getNick(message) == wolf and message.find('PRIVMSG TWP_Wolf :')!= -1:
				if not wolf in wolfVotes:
					killIndex = message.index('PRIVMSG TWP_Wolf :') + 18
					killedUser = message[killIndex:len(message)]
					if killedUser in villagers:
						if len(werewolves) == 1:
							return killedUser
						else:
							wolfVotes[wolf] = killedUser
					else:
						ioh.sendMsg(wolf, 'User is already dead!')
				else:
					ioh.sendMsg(wolf, 'You have already picked!')
		
		if len(wolfVotes) == 2:
			if wolfVotes[werewolves[0]] == wolfVotes[werewolves[0]]:
				return wolfVotes[werewolves[0]]
		else:
			wolfVotes = {}
			for wolf in werewolves:
				ioh.sendMsg(wolf, 'Your votes were different! Try Again.')
		
		checkNick(message)
		checkHelp(message)
		
def dayRound(killedUser):
	ioh.sendMsg(channel, 'The sun has risen and the wolves are away, but one unlucky person is no loger with us.')
	ioh.sendMsg(channel, 'RIP %s' % killedUser)
	while 1:
		message = ioh.checkMessages()

def newGame(playercount):
	# Create empty wolf list
	werewolves = []
	villagers = joinedUsers
	
	def getWolves(wolfCount):
		ioh.sendMsg(channel, '    WEREWOLVES: 1    VILLAGERS: %i' % (int(playercount) - 1))
		for player in random.sample(joinedUsers, wolfCount):
			villagers.remove(player)
			werewolves.append(player)
	
	# Send starting message and get werewolves
	ioh.sendMsg(channel, '--- STARTING NEW GAME OF WEREWOLF! ---')
	if playercount <= 6:
		getWolves(1)
	elif playercount > 6:
		getWolves(2)
	elif playercount > 12:
		getWolves(3)
		
	wolfList = ' '.join(werewolves)
		
	ioh.sendMsg(channel, 'It grows dark outside. The werewolves are on the hunt!')
	
	for wolf in werewolves:
		ioh.sendMsg(wolf, 'You are a werewolf! Use /msg to whisper with the other werewolves (if any) to choose who to kill. After you decide, whisper the nickname of the player you want to kill back to me.')
		ioh.sendMsg(wolf, 'List of wolves: ' + wolfList)
	
	return werewolves

# channel and Nick settings
SERVER = 'irc.freenode.net'
channel = '#TimeWastePool'
botNick = 'TWP_Wolf'

# Connect to channel 
ioh = IO.pyIRC(serv=SERVER, autojoin=1, chan=channel, nick=botNick, msg='This bot moderates games of Werewolf')
ioh.sendMsg(channel, 'Hi, I\'m ' + botNick + '. I moderate games of Werewolf! If you want to join the game, say "!join". For a list of commands, say "!helpme"')

# List of commands available to channel
commands = ['!startwolf','!list','!join','!leave','!helpme','!quit']

# List of joined users
joinedUsers = [] 

playerCount = initialize()
werewolves = newGame(playerCount)
killedUser = nightRound(werewolves, joinedUsers)
dayRound(killedUser)
