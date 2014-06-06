import phue, time

userName = 'newdeveloper'
hue = phue.Bridge('192.168.132.120', username = userName)

x = 0.4
y = 0
while x < 1.0:
	while y < 1.0:
		hue.set_group(0, 'xy', [x,y])
		print('['+str(x)+', '+str(y)+']')
		input()
		y = y + 0.1
	y = 0
	x = x + 0.1

	