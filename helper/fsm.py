import sys
import time
import helper.util as util
import helper.mouse as mouse

from helper.config import Config
from helper.context import Context


class Machine:
    blocked = False
    dead = False

    def __init__(self, data):
        self.state = {}
        for k, v in data['fsm'].items():
            self.state[k] = Step(v)
        self.start = data['start']
        self.cur = data['start']
        self.pre = '?'

    def run(self, starter=None):
        if starter:
            self.cur = starter
        else:
            self.cur = self.start

        cur = self.state[self.cur]
        curState = self.cur
        curTime = time.time()
        while cur.next or cur.pixelCheck():
            # check if the loop is potentially stuck
            if curState != self.cur:
                curState = self.cur
                curTime = time.time()
            elif time.time() - curTime > Config.i.data['stuck_timer']:
                print('STUCK?\nCur: <' + self.cur + '> Prev: <' + self.pre + '>\n')
                util.alert()
                util.wait(Config.i.data['stuck_timer'])

            if not cur.function:
                return
            self.execute()
            cur = self.state[self.cur]

    def checkForStates(self, states):
        for name in states:
            if self.checkState(name):
                return name
        return None

    # check if the screen pixels matches any given state
    def checkState(self, name):
        return self.state[name].pixelCheck()

    # waits for a conditional state (xor with invert so it can also wait for a state to go away)
    def waitState(self, name, inverse=False):
        while not (self.checkState(name) ^ inverse):
            util.wait(0.1)

    # used to directly execute a state's action
    def forceRun(self, name):
        if self.state[name].function:
            self.state[name].run()

    def checkNext(self):
        cur = self.state[self.cur]
        nextStep = self.checkForStates(cur.next)
        if nextStep:
            self.pre = self.cur
            self.cur = nextStep
            return True
        return False

    # runs the current step/state
    # wait to enter current pixel state (check if the wait is too long)
    # makes sure that it's still on current state while retrying if needed
    # does the action
    def execute(self):
        if Machine.blocked:
            return
        elif Machine.dead:
            sys.exit()

        cur = self.state[self.cur]

        # if screen has changed, check if new state has been reached
        if not cur.pixelCheck():
            util.wait(0)
            self.checkNext()
            return

        cur.run()

        # check if new state has been entered
        functionData = cur.function['data']
        util.wait(functionData['wait'], 0.15)
        if self.checkNext():
            return

        # retry loop, otherwise notify
        while cur.pixelCheck():
            cur.run()
            util.wait(functionData['retry'], 0.15)
            if self.checkNext():
                return


class Step:
    # Each state/node that can be controlled by the fsm

    # Custom machine function name (for complex steps that can't be described well using json like cv and data stuff)
    # List of Step names (can be empty indicating termination of fsm)
    # List of Pixel ((x, y), (r, g, b))
    # Function (click action, drag action)
    # Timing (initial wait, retry wait, )
    # To/From json

    def __init__(self, data):
        self.pixel = data['pixel']
        self.function = data['function']
        self.next = data['next']

    # this should be modified to a conditional check that allows customization
    # which can give it the ability to check other variables
    # or just allow the controller to pause and do other checks (then the controller will be specific but separate scripts should not need to reimplement the same stuff)
    def pixelCheck(self):
        ret = all([util.matchColor(pix['rgb'], Context.i.getColor(*(pix['pos'])), Config.i.data['pixel_threshold']) for pix in self.pixel])
        # can do some miss checks here
        return ret

    def run(self):
        # does the actual action
        data = self.function['data']
        action = self.function['action']
        if action == 'rect':
            mouse.click(util.irpoint(*data['points']))
        elif action == 'circle':
            mouse.click(util.icpoint(*data['points']))
        elif action == 'middle':
            mouse.middleClick()
        elif action == 'drag':
            mouse.rDrag(*data['points'])
        else:
            pass
