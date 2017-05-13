import time
import math
from collections import namedtuple
from itertools import product
import random
import arduino_lights as al
from arduino_lights import LED_SIZE, Size

ser = al.connect()

Viewport = namedtuple('Viewport', 'bl tr')

view = Viewport(-2 -2j, 2 + 2j)
max_iterations = 2600
palette = [
  (20, 10, 64),
  (128, 128, 255),
  # (255, 16, 100)
]


def pix_to_cmp(x, y):
  size = (view.tr - view.bl)
  inc = size.real / LED_SIZE.w + size.imag / LED_SIZE.h * 1j
  return view.bl + ((x + .5) * inc.real + (y + .5) * inc.imag * 1j)


def sample_palette(alpha):
  '''Maps floats in the range (0.0, 1.0) into a smooth, linear gradient
  palette'''
  idx = int((len(palette) - 1) * alpha)
  color1 = palette[idx]
  color2 = palette[idx + 1]
  # linearly interpolate between these two
  return tuple(int(color1[c] + abs(color2[c] - color1[c]) * alpha)
               for c in range(3))


def set_pixels(pix):
  histogram = list(0 for i in xrange(max_iterations))
  for i in range(LED_SIZE.w):
    for j in range(LED_SIZE.h):
      c = pix_to_cmp(i, j)
      k = escape_time(c)

      if k >= 0:
        histogram[k] += 1
        pix[i, j] = k
        print "[%d,%d] => (%.25f,%.25f) escaped in %d" % (i, j, c.real, c.imag,
                                                        k)
      else:
        pix[i, j] = -1

  total = sum(histogram)
  color = None
  for i in range(LED_SIZE.w):
    for j in range(LED_SIZE.h):
      k = pix[i, j]
      if k >= 0:
        alpha = sum(histogram[0:k]) * 1.0 / total
        color = sample_palette(alpha)
      else:
        color = (0, 0, 0)
      pix[i, j] = color


def escape_time(c):
  '''Return how many iterations it takes the given complex number c to
  diverge enough that we know it's not in the Mandelbrot set.
  Return -1 when it doesn't diverge within max_iterations.'''
  z = c
  for k in range(max_iterations):
    z = z**2 + c
    if z.real**2 + z.imag**2 >= 4.0:
      return k
  else:
    return -1


def zoom_viewport(factor, target):
  global view
  center = view.bl + (view.tr - view.bl) / 2
  # move the center a small step towards the target point
  newcenter = center + (target - center) * (factor - 1.0)
  # calculate the new viewport from the new center by
  # reducing the distance to bl and tr by factor
  view = Viewport(newcenter + (view.bl - center) / factor,
                  newcenter + (view.tr - center) / factor)


def randomize_colors():
  global palette

  palette = [(random.randint(0, 100),
              random.randint(0, 100),
              random.randint(0, 100)),
             (random.randint(100, 255),
              random.randint(100, 255),
              random.randint(100, 255))]


pix = {xy: (0, 0, 0)
       for xy in product(xrange(LED_SIZE.w), xrange(LED_SIZE.h))}

INTERESTING_POINTS = [
  1.257368028466541028848 + 0.378730831028625370052j,
  -0.70334402671161810883 + 0.24717876921242826205j,
  -1.985540371654130485531439267191269851811165434636382820704394766801377 +
    0.000000000000000000000000000001565120217211466101983496092509512479178j,
  -1.25736802846652839265383159384773654166836713857126000896912753375688559878664765114255696457015368246531973104439755978333044015506759938503739206829441575363669402497147343368904702066174408250247081855416385744218741909521990441308969603994513271641284298225323509381146075334937409491188 +
    0.37873083102862491151257052392242106932532193327534173605649141946411779667848532042309666819671311329800095959763206221251386819369531602358854394169140220049675504811341950346171196600590463661845947574424944950533273158558278821586333530950155398785389980291835095955110139525825547062070j,
  -1.77810334274064037110522326038852639499207961414628307584575173232969154440
    + 0.00767394242121339392672671947893471774958985018535019684946671264012302378j
]

randomize_colors()
while True:
  set_pixels(pix)
  # zoom towards brightest pixel
  # maxx, maxy = max(pix.iteritems(), key=lambda kv: sum(kv[1]))[0]
  # zoom_viewport(1.1, pix_to_cmp(maxx, maxy))
  zoom_viewport(1.1, INTERESTING_POINTS[4])
  al.draw_pixel_map(ser, pix)
  time.sleep(0.1)
