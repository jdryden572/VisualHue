import requests
import json
import socket

socket.setdefaulttimeout(10)
error = 'NUPnP unable to locate local Hue Bridge'
deviceType = 'OSIVisualAlert'
userName = 'newdeveloper'

def getNUPnPInfo():
  response = requests.get('http://www.meethue.com/api/nupnp')
  NUPnP = json.loads(response.text)
  response.close()
  return NUPnP

def getIPAddress(deviceIndex = 0):
  try:
    info = getNUPnPInfo()
    IP = info[deviceIndex].get('internalipaddress')
    return str(IP)
  except:
    print(error)
    IP = 'localhost:80'
    return IP

def getHue():
  try:
    from visualhue import Hue
    IP = getIPAddress()
    return Hue(IP, userName, deviceType)
