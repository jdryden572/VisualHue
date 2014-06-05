import phue, time

userName = 'newdeveloper'
hue = phue.Bridge('localhost:80', username = userName)

x = 0
y = 0
while x < 1.0:
	while y < 1.0:
		hue.set_group(0, 'xy', [x,y])
		input()
		y = y + 0.1
	y = 0
	x = x + 0.1

	