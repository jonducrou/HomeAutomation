import smbus
import time
import urllib
bus = smbus.SMBus(1)
address = 0x48
with open('/home/pi/apiKey', 'r') as key_file:
    key = key_file.read().strip()

def read():
  data = bus.read_i2c_block_data(address, 0)
  msb = data[0]
  lsb = data[1]
  t = (msb<<8) | lsb
  return (t>>4) * 0.0625


t = read()
print t
f = urllib.urlopen("http://www.devicehub.net/io/537/?apiKey=" + key + "&WineRoom=" + str(t))
s = f.read()
print s
