import urllib.request
import LightTower
import atexit
import time
import re


pageURL = 'http://osi-cc100:9080/stats'
pattern = '(\d*) CALLS WAITING FOR (\d*):(\d*)'  # define RegEx search pattern
searchPattern = re.compile(pattern)				# compile pattern into RegEx object
delayTime = 1
maxDisconnectTime = 15
lightTower = LightTower.Tower()


def MainLoop():
	connectFailCount = 0		# create error counter
	points = 0

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
		state = determineState(points, connectionFailure)
		lightTower.setState(state)
		fileWrite(state)
		elapsedTime = time.time() - thisTime		# check time elapsed fetching data
		if elapsedTime > delayTime:					# proceed if fetching took longer than 5 sec
			pass
		else:										# otherwise delay the remainder of 5 sec
			time.sleep(delayTime - elapsedTime)


def getData(address):
	try:
		data = str(urllib.request.urlopen(address).read())  # fetch CISCO phone data
		connectFail = 0					# reset error counter
		extracted = searchPattern.search(data)  # extract desired values from data
		[calls, minutes, seconds] = [
			extracted.group(1), extracted.group(2), extracted.group(3)]
		print('{0:2s} calls waiting for {1:s}:{2:2s}'.format(calls, minutes, seconds))
		timeSeconds = int(seconds) + int(minutes) * 60
		return [calls, timeSeconds, connectFail]
	except urllib.error.URLError:				# print error if network lost
		print('CANNOT CONNECT TO CISCO PHONE STATUS PAGE')
		connectFail = 1					# step fail counter up by 1
		return [None, None, connectFail]


def calcPoints(calls, waitTime):
	callPoints = calls
	timePoints = waitTime // 60
	points = callPoints + timePoints
	return points


def determineState(points, connectionFailure):

	# Lis of States
	# array elements map to lights : [red, yellow, green]
	red         = [1, 0, 0]
	redYellow   = [1, 1, 0]
	yellow      = [0, 1, 0]
	yellowGreen = [0, 1, 1]
	green       = [0, 0, 1]

	allOn       = [1, 1, 1]
	allOff      = [0, 0, 0]
	# Aliases
	conLost     = allOn
	greenYellow = yellowGreen
	yellowRed   = redYellow

	if connectionFailure:
		return conLost
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
