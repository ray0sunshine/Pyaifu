# Universal helper functions: Logistics, Micro...etc
# Player state: Timing, Loops, Pause/Play status etc

# Possibly: Statistics like delay increase and such

from fsm import Machine
from context import Context
from fsm import Machine

import config
import sys
import os
import json
import util
import keyboard
import importlib
import threading


class Controller:
    def __init__(self, files):
        self.state = {
            'playing': False
        }
        self.scripts = {}
        for f in files:
            name, path = f.split('=')
            self.scripts[name] = Machine(self.getData(path)) if os.path.exists(path) else path
        runner = importlib.import_module(self.scripts['runner'], package=None)
        self.runner = runner.Runner(self)

    def getData(self, jsonPath):
        o = {}
        with open(jsonPath, 'r') as cfg:
            o = json.load(cfg)
        return o

    def play(self):
        tr = threading.Thread(None, self.runner.play, 'play')
        tr.start()
        print('PLAY')

    def pauseToggle(self):
        # this only works while a fsm is being run normally though (not forced)
        Machine.blocked = not Machine.blocked
        print('PAUSE' if Machine.blocked else 'RESUME')
