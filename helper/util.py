import pytesseract as ts
import re
import numpy
import time
import math
import winsound

from desktopmagic.screengrab_win32 import getRectAsImage
from datetime import datetime


def iround(n):
    return int(round(n))


def normalRange(lo, hi):
    # the ordering for bounds don't actually matter
    if lo > hi:
        lo, hi = hi, lo

    # takes the lower and upper bounds
    if hi - lo == 0:
        return hi

    # instead of clipping which can create a border pattern, just redo until bounds met
    mean, dev = (lo + hi) / 2, (hi - lo) / 6
    ret = numpy.random.normal(mean, dev)
    while not lo <= ret <= hi:
        ret = numpy.random.normal(mean, dev)
    return ret


def normalRange2(mean, dev=0):
    # takes the center and deviation
    if dev == 0:
        return mean
    return normalRange(mean - dev, mean + dev)


def lerp(p1, p2, ratio=0.5):
    # linear interpolation to a single decimal, ratio is progress from p1 to p2
    inverse = 1 - ratio
    return tuple(round(p1[i] * inverse + p2[i] * ratio, 1) for i in range(2))


def ilerp(p1, p2, ratio=0.5):
    # rounds the linear interpolation to nearest int
    return tuple(iround(v) for v in lerp(p1, p2, ratio))


def dist(p1, p2):
    # linear distance between 2 points
    dx = p1[0] - p2[0]
    dy = p1[1] - p2[1]
    return math.sqrt(dx * dx + dy * dy)


def idist(p1, p2):
    # integer distance
    return iround(dist(p1, p2))


def rpoint(p1, p2):
    # random point in a rectangular area defined by p1 and p2 as opposing corners
    return tuple(normalRange(p1[i], p2[i]) for i in range(2))


def irpoint(p1, p2):
    return tuple(iround(v) for v in rpoint(p1, p2))


def cpoint(p1, p2):
    # random point in a circular area defined with p1 -> p2 as the diameter
    r = dist(p1, p2) / 2
    c = lerp(p1, p2)
    ret = tuple(normalRange2(c[i], r) for i in range(2))
    while dist(ret, c) > r:
        ret = tuple(normalRange2(c[i], r) for i in range(2))
    return ret


def icpoint(p1, p2):
    return tuple(iround(v) for v in cpoint(p1, p2))


def matchColor(c1, c2, deviance=0):
    # try to match 2 color tuples, with optional allowance for difference
    return max(abs(a - b) for a, b in zip(c1, c2)) <= deviance


def cubicRandomPoints(p1a, p1b, p4a, p4b):
    # create 4 cubic bezier control points from a starting area and end area
    e = 0.7
    p1 = irpoint(p1a, p1b)
    p4 = irpoint(p4a, p4b)
    p2 = icpoint(ilerp(p1, p4, (1 - e) / 3), ilerp(p1, p4, (1 + e) / 3))
    p3 = icpoint(ilerp(p1, p4, (2 - e) / 3), ilerp(p1, p4, (2 + e) / 3))
    return p1, p2, p3, p4


def cubicBezier(p1, p2, p3, p4, t):
    # return position based on 4 points and t
    t = numpy.clip(t, 0, 1)
    ivt = 1 - t
    xa = [p1[0], 3 * p2[0], 3 * p3[0], p4[0]]
    ya = [p1[1], 3 * p2[1], 3 * p3[1], p4[1]]
    tm = t
    ivtm = ivt
    for i in range(1, 4):
        xa[i] *= tm
        ya[i] *= tm
        tm *= t
    for i in range(2, -1, -1):
        xa[i] *= ivtm
        ya[i] *= ivtm
        ivtm *= ivt
    return sum(xa), sum(ya)


def wait(t, dev=-1):
    if dev < 0:
        # undefined deviance to automically add a bit of random
        # the deviation of a predefined time is scaled up to a max of 1.5s (3 second range for any length of time)
        t = max(normalRange(0.05, 0.15), normalRange2(t, min(1.5, t * 0.2)))
    elif dev > 0:
        # defined non zero deviance
        t = max(0.001, normalRange2(t, dev))
    time.sleep(t)
    return t


def timestamp():
    # gets the epoch time in miliseconds
    return str(round(1000 * datetime.timestamp(datetime.now())))


def getScreen(area, filename):
    img = getRectAsImage(area)
    if filename:
        img.save(filename + timestamp() + '.png', format='png')
    return img


def alert():
    winsound.PlaySound('helper/config/alert.wav', winsound.SND_FILENAME | winsound.SND_ASYNC)


def getScreenText(area):
    # screenshot and convert to string (Doesn't really work on a non-mainscreen)
    ret = ts.image_to_string(getRectAsImage(area))
    return ret.strip()


def getTimer(t):
    # determines if the string matches a regex for time and returns result in seconds
    if re.match('\d{2}:\d{2}:\d{2}', t):
        return sum(s * d for s, d in zip([3600, 60, 1], map(int, t.split(':'))))
    return None
