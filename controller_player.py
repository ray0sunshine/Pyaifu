# Universal helper functions: Logistics, Micro...etc
# Player state: Timing, Loops, Pause/Play status etc

# Possibly: Statistics like delay increase and such

from fsm import Machine
from context import Context

import config
import sys
import os
import json
import util
import keyboard
import importlib


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
        self.runner.play()
