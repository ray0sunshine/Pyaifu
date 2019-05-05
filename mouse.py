import pyautogui as gui
import ctypes

import util

from context import Context

MOUSEEVENTF_MOVE = 0x0001        # mouse move
MOUSEEVENTF_LEFTDOWN = 0x0002    # left button down
MOUSEEVENTF_LEFTUP = 0x0004      # left button up
MOUSEEVENTF_MIDDLEDOWN = 0x0020  # middle button down
MOUSEEVENTF_MIDDLEUP = 0x0040    # middle button up

DRAG_TIME_STEP = 0.005           # time to wait during drag move


def getMousePos():
    # get mouse position relative to context window
    mx, my = gui.position()
    if Context.i.x <= mx <= Context.i.x2 and Context.i.y <= my <= Context.i.y2:
        return mx - Context.i.x, my - Context.i.y
    return None


def getMouseColor():
    # get pixel color at mouse, does bound check
    mp = getMousePos()
    if mp is not None:
        return Context.i.getColor(*mp)
    return None


def mouseTo(p):
    # can only be used to initialize the mouse position
    ctypes.windll.user32.SetCursorPos(int(p[0] + Context.i.x), int(p[1] + Context.i.y))


def click(p):
    # pass in local coords as point tuple
    mouseTo(p)
    ctypes.windll.user32.mouse_event(MOUSEEVENTF_LEFTDOWN | MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)


def mouseMove(p):
    # use this to actually move the mouse, need to shift a bit to actually lock in position
    mouseTo(p)
    ctypes.windll.user32.mouse_event(MOUSEEVENTF_MOVE, 1, 1, 0, 0)


def mouseShift(x, y):
    # mouse shift by 1 pixel
    ctypes.windll.user32.mouse_event(MOUSEEVENTF_MOVE, x, y, 0, 0)


def mouseDown():
    # can be used in conjunction with mouseTo
    ctypes.windll.user32.mouse_event(MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)


def mouseUp():
    # release
    ctypes.windll.user32.mouse_event(MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)


def middleClick():
    # mouse middle click
    p = util.ilerp((Context.i.x, Context.i.y), (Context.i.x2, Context.i.y2))
    mouseTo(p)
    ctypes.windll.user32.mouse_event(MOUSEEVENTF_MIDDLEDOWN | MOUSEEVENTF_MIDDLEUP, 0, 0, 0, 0)


def rDrag(p1a, p1b, p4a, p4b, delay=0.5, hold=0.01):
    p1, p2, p3, p4 = util.cubicRandomPoints(p1a, p1b, p4a, p4b)
    mouseTo(p1)
    mouseDown()
    util.wait(hold, 0)
    t = 0
    while t < delay:
        util.wait(DRAG_TIME_STEP, 0)
        t = min(t + util.normalRange(DRAG_TIME_STEP, DRAG_TIME_STEP / 2), delay)
        mouseMove(util.cubicBezier(p1, p2, p3, p4, t / delay))
    util.wait(hold, 0)
    mouseUp()
