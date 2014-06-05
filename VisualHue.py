import urllib.request
import LightTower
import contextlib
import atexit
import time
import re
import sys

pageURL = 'http://osi-cc100:9080/stats'
pattern = '(\d*) CALLS WAITING FOR (\d*):(\d*)'  # define RegEx search pattern
searchPattern = re.compile(pattern)				# compile pattern into RegEx object
delayTime = 1
maxDisconnectTime = 15

# List of light states
red         = [1, 0, 0]
redYellow   = [1, 1, 0]
yellow      = [0, 1, 0]
yellowGreen = [0, 1, 1]
green       = [0, 0, 1]
allOn       = [1, 1, 1]
allOff      = [0, 0, 0]


try:																	# check for DEBUG argument
	DEBUG = sys.argv[1] == '-d'
except IndexError:
	DEBUG = False
lightTower = LightTower.Tower(DEBUG)


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
			lightTower.setState(state)
			fileWrite(state)
		elapsedTime = time.time() - thisTime		# check time elapsed fetching data
		if elapsedTime > delayTime:					# proceed if fetching took longer than 5 sec
			pass
		else:										# otherwise delay the remainder of 5 sec
			time.sleep(delayTime - elapsedTime)


def getData(address):
	try:
		connection = urllib.request.urlopen(address)
		data = str(connection.read())  # fetch CISCO phone data
		connectFail = 0					# reset error counter
		extracted = searchPattern.search(data)  # extract desired values from data
		[calls, minutes, seconds] = [
			extracted.group(1), extracted.group(2), extracted.group(3)]
		if DEBUG:
			print('{0:2s} calls waiting for {1:s}:{2:2s}'.format(calls, minutes, seconds))
		timeSeconds = int(seconds) + int(minutes) * 60
		return [calls, timeSeconds, connectFail]
	except urllib.error.URLError:				# print error if network lost
		print('CANNOT CONNECT TO CISCO PHONE STATUS PAGE')
		connectFail = 1					# step fail counter up by 1
		return [None, None, connectFail]
	finally:
		connection.close()


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


def fileWrite(state):
	text = str(time.time()) + ' ' + str(state)
	file = open('../webServer/currentLightState.txt', 'w')
	file.write(text)
	file.close()



def resetLights():
	lightTower.setState([0, 0, 0])


atexit.register(resetLights)


if __name__ == '__main__':
	MainLoop()
