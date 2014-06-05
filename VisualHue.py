import urllib.request
import contextlib
import atexit
import time
import re
import sys
import phue
import json

pageURL = 'http://osi-cc100:9080/stats'
pattern = '(\d*) CALLS WAITING FOR (\d*):(\d*)'  # define RegEx search pattern
searchPattern = re.compile(pattern)				# compile pattern into RegEx object
delayTime = 1
maxDisconnectTime = 15

# List of light states
red         = ['xy', [  0, 0.8]]
redYellow   = ['xy', [  0, 0.2]]
yellow      = ['xy', [  0, 0.4]]
yellowGreen = ['xy', [0.4, 0.4]]
green       = ['xy', [0.6, 0.6]]
allOn       = ['on', True]
allOff      = ['on', False]

userName = 'newdeveloper'

try:																	# check for DEBUG argument
	DEBUG = sys.argv[1] == '-d'
except IndexError:
	DEBUG = False
#lightTower = LightTower.Tower(DEBUG)


def MainLoop():
	connectFailCount = 0		# create error counter
	points = 0
	state = allOff

	while True:
		thisTime = time.time()						# record time when entering loop
		[newCallsWaiting, newTimeSeconds, connectFail] = getData(pageURL)
		if connectFail:
			connectFailCount += 1
		else:
			callsWaiting = newCallsWaiting
			timeSeconds = newTimeSeconds
			points = calcPoints(int(callsWaiting), timeSeconds)
			connectFailCount = 0

		connectionFailure = connectFailCount * delayTime >= maxDisconnectTime
		newState = determineState(points, connectionFailure)
		if newState != state:
			state = newState
			setState(state)
#			fileWrite(state)	#out for now
		elapsedTime = time.time() - thisTime		# check time elapsed fetching data
		if elapsedTime > delayTime:					# proceed if fetching took longer than 5 sec
			pass
		else:										# otherwise delay the remainder of 5 sec
			time.sleep(delayTime - elapsedTime)

			
def getBridgeIP():
	# with urllib.request.urlopen('http://www.meethue.com/api/nupnp') as connection:
		# data = str(connection.read())
	# try:
		# IP = json.loads(data).get('internalipaddress')
	# except:
		# print('Could not find Bridge IP address automatically')
	# else: 
		# return IP
	return 'localhost:80'

	
def getData(address):
	try:
		with urllib.request.urlopen(address, timeout = 2) as connection:
			data = str(connection.read())  # fetch CISCO phone data
		connectFail = 0					# reset error counter
		extracted = searchPattern.search(data)  # extract desired values from data
		[calls, minutes, seconds] = [
			extracted.group(1), extracted.group(2), extracted.group(3)]
		if DEBUG:
			print('{0:2s} calls waiting for {1:s}:{2:2s}'.format(calls, minutes,	seconds))
		timeSeconds = int(seconds) + int(minutes) * 60
		return [calls, timeSeconds, connectFail]
	except:				# print error if network lost
		print('CANNOT CONNECT TO CISCO PHONE STATUS PAGE')
		connectFail = 1					# step fail counter up by 1
		return [None, None, connectFail]


def calcPoints(calls, waitTime):
	callPoints = calls
	timePoints = waitTime // 60
	points = callPoints + timePoints
	return points


def determineState(points, connectionFailure):
	if connectionFailure:
		return allOn
	elif points == 0:
		return green
	elif points >= 0 and points < 4:
		return yellowGreen
	elif points >= 4 and points < 7:
		return yellow
	elif points >= 7 and points < 9:
		return redYellow
	elif points >= 9:
		return red

def setState(state):
	hue.set_group(0, state[0], state[1])

def fileWrite(state):
	text = str(time.time()) + ' ' + str(state)
	file = open('../webServer/currentLightState.txt', 'w')
	file.write(text)
	file.close()



def resetLights():
	setState(allOff)


atexit.register(resetLights)


if __name__ == '__main__':
	hue = phue.Bridge(ip = getBridgeIP(), username = userName)
	setState(allOn)
	MainLoop()
