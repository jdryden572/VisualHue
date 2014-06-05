import urllib.request
import json

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