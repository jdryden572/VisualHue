import requests
import json

class Request:
  def request(self, method = 'GET', url = '', data = {}):
    url = 'http://{0}/api/{1}{2}'.format(self.IP, self.userName, url)
    response = requests.request(method, url, data)
    toReturn = json.loads(response.content)
