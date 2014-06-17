'''Configuration file for visualhue.'''

# These variables may be adjusted as desired
delayTime = 2					# Seconds between polling the phone status
maxDisconnectTime = 15			# Disconnected time before triggering "noConnect"

# Change "manualBridgeIP" if Hue bridge IP is known but cannot be found 
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