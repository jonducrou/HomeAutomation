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
#  elif isFull: #bad reads on full - dropping for now
#    print "Full!"
#    return -2
  elif isOff:
    print "Off!"
    return 0
  else:
    print "On!"
    return 1

def read_state_pwm(x):
  global tx,isOn,isOff,isFail
  d = time.time() - tx
  print d
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

f = urllib.urlopen("http://data.sparkfun.com/input/0lJKr0NxrDtLlgaE7OvV?private_key=" + key + "&ac_status=" + str(state) + "&temp=" + str(temp))
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

if (state == 1) or (state == 0 ): #not in error
  if not sunny() and temp < 25: # don't run now, no solar
    print "It's not sunny..."
    turn_off()
  else:
    if (state == 0):
      if temp > 25 and not sunny():
        print "It's too hot... even without the sun."
        turn_on()
      elif temp > 24 and sunny():
        print "It's too hot... and the power is free during the day"
        turn_on()
    elif (temp < 22 and state == 1):
      print "It's cool..."
      turn_off()

GPIO.cleanup()
