import requests, time
url = 'http://localhost:80/api/newdeveloper/groups/0/action'

def cycleColors():
  color = 0
  while color < 65500:
    data = '{hue:' + str(color) + '}'
    r = requests.put(url, data)
    r.close()
    print(color)
    time.sleep(1)
    color += 1000

while True:
  print('begin cycle')
  cycleColors()
  print('cycle end')
  time.sleep(5)
