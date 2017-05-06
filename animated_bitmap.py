import serial, Image
import time, math
from arduino_lights import ledutils

ser = serial.Serial(
    port='/dev/ttyUSB0',
    baudrate=115200
)

# So! Apparently when you connect to the arduino serial port, the bootloader
# kicks in, resets the arduino and waits a second for a new program to be loaded
# before running the actual already stored code
time.sleep(2)

def render_image(image_path):
  img = Image.open("images/" + image_path)
  rgb_im = img.convert('RGB')
  size = 12,12
  sleep_time = 0.002

  ledutils.end_frame(ser)

  print "time per frame: " + str(sleep_time * 144) + "s"

  for x in range(12):
    for y in range(12):
      r,g,b = rgb_im.getpixel((x,y))
      ledutils.set_pixel(ser, x, y, r, g, b)

test = True
baseball = False 
cat = False 
dude = False 

while(True):
  if test:
    for n in range(25):
      render_image("testy_test/"+str(n)+".bmp")
      time.sleep(0.5)

  if baseball:
    for n in range(10):
      render_image("baseball/baseball-"+str(n)+".bmp")
      time.sleep(0.1)

  if cat:
    for n in range(4):
      render_image("cat/cat-"+str(n)+".bmp")
      time.sleep(0.2)

  if dude:
    for n in range(28):
      render_image("tiny_dude/tiny_dude-"+str(n)+".bmp")
      time.sleep(0.05)
