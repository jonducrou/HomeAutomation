import smbus
import time
import urllib
import RPi.GPIO as GPIO

bus = smbus.SMBus(1)
address = 0x48

GPIO.setmode(GPIO.BOARD)
GPIO.setup(7, GPIO.OUT)
GPIO.output(7, GPIO.LOW)
GPIO.setup(11, GPIO.IN, pull_up_down = GPIO.PUD_DOWN)
isOff = False
isOn = False
isFail = False
tx = time.time()

with open('/home/pi/apiKey', 'r') as key_file:
    key = key_file.read().strip()

print str(time.localtime())

## Returns 1 for on, 0 for off, -1 for water full/fail
def read_state():
  tx = time.time()
  GPIO.add_event_detect(11, GPIO.RISING, callback=read_state_pwm, bouncetime=1)
  t = time.time()
  while time.time() - t < 4:
    1
  GPIO.remove_event_detect(11)
  isFull = (isOn and isOff)
  isFail = not isOn and not isOff

  #print "off / on / fail"
  if isFail:
    print "Fail!"
    return -1
  elif isFull:
    print "Full!"
    return -1
  elif isOff:
    print "Off!"
    return 0
  else:
    print "On!"
    return 1

def read_state_pwm(x):
  global tx,isOn,isOff,isFail
  d = time.time() - tx
  if d > .0400:
    isOff = True
  else:
    isOn = True
  tx = time.time()
  
def read_temp():
  data = bus.read_i2c_block_data(address, 0)
  msb = data[0]
  lsb = data[1]
  t = (msb<<8) | lsb
  return (t>>4) * 0.0625



state = read_state()
temp = read_temp()

print temp
print state

f = urllib.urlopen("http://www.devicehub.net/io/537/?apiKey=" + key + "&WineRoom=" + str(temp))
s = f.read()
print s

f = urllib.urlopen("http://www.devicehub.net/io/537/?apiKey=" + key + "&ACUnit=" + str(state))
s = f.read()
print s

def flip_state():
  GPIO.output(7, GPIO.HIGH)
  time.sleep (1)
  GPIO.output(7, GPIO.LOW)

def sunny():
  now_hour = time.localtime().tm_hour
  return now_hour > 6 and now_hour < 18

def turn_off():
  if not (state == 0):
    print "Turning off"
    flip_state()

def turn_on():
  if not (state == 1):
    print "Turning on"
    flip_state()

if not (state == -1 ): #it's on or off
  if not sunny(): # don't run now, no solar
    print "It's not sunny..."
    turn_off()
  else:
    if (temp > 25 and state == 0):
      print "It's too hot..."
      turn_on()
    elif (temp < 23 and state == 1):
      print "It's cool..."
      turn_off()

GPIO.cleanup()
