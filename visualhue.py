import requests
import json

### Attempt to find IP using nupnp site ###
# note: this function may not work if we have more than one Bridge installed
def getBridgeIP():
  data = requests.get('http://www.meethue.com/api/nupnp')
  if data.text != '[]':
    return json.loads(data.text).get('internalipaddress')
  else:
    print('Could not locate Bridge automatically.')
    return None



class Hue:
  def __init__(self, IP, userName, deviceType)
    self.IP = IP
    self.userName = userName
    self.deviceType = deviceType

  def getLights(self):
