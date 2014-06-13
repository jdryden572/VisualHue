"""
visualhue

Brett Nelson and James Dryden
OSIsoft, LLC

An implementation of Philips Hue as a status indicator.

"Hue Personal Wireless Lighting" is a trademark owned by 
Philips Electronics N.V. See www.meethue.com for more information.
"""

defaultConfig = """'''Configuration file for visualhue'''

# These variables may be adjusted as desired
delayTime = 1					# Seconds between polling the phone status
maxDisconnectTime = 15			# Disconnected time before triggering "noConnect"

# Change "config.manualBridgeIP" if Hue bridge IP is known but cannot be found 
# automatically. Variable "userName" must match the username registered 
# on the the Hue Bridge.
manualBridgeIP = None
userName = 'ositechsupport'

# List of light states. The parameters for each state may be changed if
# desired. If the state names are changed, the "determineState" function 
# must be changed!
red         = {'on': True, 'bri': 150, 'sat': 255, 'transitiontime': 4, 'xy': [0.8, 0.3]}
redYellow   = {'on': True, 'bri': 150, 'sat': 255, 'transitiontime': 4, 'xy': [0.6, 0.4]}
yellow      = {'on': True, 'bri': 150, 'sat': 255, 'transitiontime': 4, 'xy': [0.55, 0.46]}
green       = {'on': True, 'bri': 100, 'sat': 255, 'transitiontime': 4, 'xy': [0.5, 0.8]}
white		= {'on': True, 'bri':  50, 'sat': 255, 'transitiontime': 2, 'ct': 200}
allOn       = {'on': True, 'bri':  50, 'sat': 255, 'transitiontime': 2, 'ct': 250}
noConnect	= {'on': True, 'bri': 150, 'sat': 255, 'transitiontime': 4, 'effect': 'colorloop'}
allOff      = {'on': False}
"""

import urllib.request
import atexit
import time
import re
import sys
import json
import warnings
try:
	import requests
except:
	warnings.warn('The requests module must be installed. Try "pip install requests"')
	exit()
try: 
	import phue
except:
	warnings.warn('The phue module must be installed. Visit https://github.com/studioimaginaire/phue')
	exit()
try:
	import config
except:
	warnings.warn('Config file could not be found. Creating default config file, config.py')
	with open('config.py', 'w') as f:
		f.write(defaultConfig)
	import config
	
pageURL = 'http://osi-cc100:9080/stats'
callPattern = r'(\d*) CALLS WAITING FOR (\d*):(\d*)'  # define RegEx search pattern
callPatternCompiled = re.compile(callPattern)				# compile pattern into RegEx object
ipPattern = r'(\d+\.\d+\.\d+\.\d+)'
ipPatternCompiled = re.compile(ipPattern)	


try:													
	DEBUG = sys.argv[1] == '-d'
except IndexError:
	DEBUG = False


def MainLoop():
	"""Loops forever to continually run the program."""
	connectFailCount = 0	
	points = 0
	state = config.allOff

	while True:
		thisTime = time.time()						# record time when entering loop
		if isOperatingHours():	
			[newCallsWaiting, newTimeSeconds, connectFail] = getPhoneData(pageURL)
			if connectFail:
				connectFailCount += 1
			else:
				callsWaiting = newCallsWaiting
				timeSeconds = newTimeSeconds
				points = calcPoints(int(callsWaiting), timeSeconds)
				connectFailCount = 0

			connectionFailure = connectFailCount * config.delayTime >= config.maxDisconnectTime
			newState = determineState(points, connectionFailure)
			if newState != state:
				state = newState
				setState(state)
#				fileWrite(points)	#out for now
		else:
			if DEBUG: print('Not during office hours. Lights off.')
			setState(allOff)
			time.sleep(10)
		elapsedTime = time.time() - thisTime		# check time elapsed fetching data
		if elapsedTime > config.delayTime:					# proceed if fetching took longer than 5 sec
			pass
		else:										# otherwise delay the remainder of 5 sec
			time.sleep(config.delayTime - elapsedTime)

			
def getBridgeIP():
	"""Finds Hue Bridge IP address using http://www.meethue.com/api/nupnp. 
	Returns a string containing the IP address, or None if unable to locate 
	an address.
	"""
	with urllib.request.urlopen('http://www.meethue.com/api/nupnp') as connection:
		data = str(connection.read())
	match = ipPatternCompiled.search(data)
	if match is None:
		print('Could not find Bridge IP address automatically')
		return None
	else: 
		return match.group(1)


def getPhoneData(address):
	"""Get the state of the Cisco phone system, at given address.
	
	Returns [calls, timeSeconds, connectFail]. 
	"""
	try:
		with urllib.request.urlopen(address, timeout = 2) as connection:
			data = str(connection.read())  # fetch CISCO phone data
		connectFail = 0					# reset error counter
		extracted = callPatternCompiled.search(data)  # extract desired values from data
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
	"""Determine call system priority points based on # of calls waiting
	and wait time of longest waiting call.
	"""
	callPoints = calls
	timePoints = waitTime // 60
	points = callPoints + timePoints
	return points


def determineState(points, connectionFailure):
	"""Choose the Hue light state based on the point count and whether the 
	connection has been lost.
	"""
	if connectionFailure:
		return config.noConnect
	elif points == 0:
		return config.white
	elif points >= 0 and points < 4:
		return config.green
	elif points >= 4 and points < 7:
		return config.yellow
	elif points >= 7 and points < 9:
		return config.redYellow
	elif points >= 9:
		return config.red

		
def setState(state):
	"""Set the state of the Hue lights."""
	try:
		hue.set_group(0, state)
	except:
		print('Could not connect to Hue Bridge. Check network connections.')

	
def fileWrite(points):
	"""Write the current priority points to a .txt file."""
	text = str(time.time()) + ' points: ' + str(points)
	file = open('../webServer/currentLightState.txt', 'w')
	file.write(text)
	file.close()

	
def getNewLights(IP):
	"""Instructs the Hue Bridge to search for new Hue lights.
	
	The 'find new lights' function needs to be called manually, 
	because this feature appears to be unsupported by the phue module. 
	This will instruct the bridge to search for and add any new hue lights. 
	Searching continues for 1 minute and is only capable of locating up 
	to 15 new lights. To add additional lights, the command must be run again.
	"""
	connection = requests.post('http://' + IP + '/api/' + config.userName + '/lights')
	if DEBUG: print(connection.text)
	connection.close()
	

def isOperatingHours():
	"""Determines whether the the time is currently during office hours.
	
	Returns boolean True or False.
	"""
	isWeekday 		= (0 <= time.localtime()[6] <=  4)	# checks if today is a weekday
	isOfficeHours 	= (7 <= time.localtime()[3] <= 17)	# checks if currently during office hours
	return (isWeekday and isOfficeHours)


	
def resetLights():
	"""Defines action to be taken to reset the Hue lights."""
	setState(config.allOff)

def runProgram():
	# First try to connect to Hue Bridge automatically. If this fails, attempt
	# to connect with the config.manualBridgeIP. Exit if both fail.
	IP = getBridgeIP()
	try:
		global hue
		hue = phue.Bridge(ip=IP, username=config.userName)
	except:
		print('Failed to automatically connect to Hue Bridge.')
		print('Attempting to use manual IP.')
		IP = config.manualBridgeIP
		try: 
			hue = phue.Bridge(ip=IP, username=config.userName)
		except:
			print('Manual IP failed. Make sure initial Bridge configuration is complete.')
			print('Exiting.')
			exit()
	
	# Create the Bridge instance, set the lights to allOn, instruct Bridge
	# to check for new Hue lights, register exit action (turns off lights) 
	# and run the main loop.
	hue = phue.Bridge(ip = IP, username = config.userName)
	setState(config.allOn)
	getNewLights(IP)
	atexit.register(resetLights)
	MainLoop()
	
if __name__ == '__main__':
	runProgram()
