import util
import mouse

from config import Config
from context import Context
# multiple machines can be kept at the highest level and swapped between
# these can be controlled by another config that can tell what states scripts to load


class Machine:
    # The driver for the states

    # Map of custom functions
    # Map of names to states (this owns all steps)
    # Current/Previous state kept and updating
    # Check the current pixels to match against state
    # executes step functionality
    # supports pause
    # To/From json
    def __init__(self, data):
        self.state = {}
        for k, v in data['fsm'].items():
            self.state[k] = Step(v)
        self.cur = self.state[data['start']]
        self.pre = None

    def run(self):
        while self.cur.next:
            self.execute(self.cur)

    def checkForStates(self, states):
        for name in states:
            if self.state[name].pixelCheck():
                return name
        return None

    # runs the current step/state
    # wait to enter current pixel state (check if the wait is too long)
    # makes sure that it's still on current state while retrying if needed
    # does the action
    def execute(self):
        if self.checkForStates(self.cur.next):
            self.cur = self.checkForStates(self.cur.next)
            return

        while not self.cur.pixelCheck():
            util.wait(0)

        self.cur.run()

        functionData = self.cur.function['data']
        util.wait(functionData['wait'], 0.15)

        # retry loop, otherwise notify
        while self.cur.pixelCheck():
            self.cur.run()
            util.wait(functionData['retry'], 0.15)


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
        return all([util.matchColor(pix['rgb'], Context.i.getColor(*(pix['pos'])), Config.i.data['pixel_threshold']) for pix in self.pixel])

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
