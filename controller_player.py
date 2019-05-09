# Universal helper functions: Logistics, Micro...etc
# Player state: Timing, Loops, Pause/Play status etc
# loads in a generic state implicitly for things like home menu state and common

# Possibly: Statistics like delay increase and such function

from helper.fsm import Machine
from helper.context import Context

import os
import json
import helper.util as util
import importlib
import threading

config_path = 'helper/config/'


class Controller:
    def __init__(self, files):
        self.state = {
            'playing': False,
            'logistic': [0, 0, 0, 0]
        }
        self.scripts = {}

        for f in files:
            name, path = f.split('=')
            self.scripts[name] = Machine(self.getData(path)) if os.path.exists(path) else path
        self.scripts['common'] = Machine(self.getData(config_path + 'common.json'))
        self.scripts['seq1'] = Machine(self.getData(config_path + 'teamSelectSeq1.json'))
        self.scripts['seq2'] = Machine(self.getData(config_path + 'teamSelectSeq2.json'))

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

    def openLogi(self):
        m = self.scripts['common']
        while not m.checkState('logi opened'):
            m.forceRun('open logi')
            util.wait(2)

    def closeLogi(self):
        m = self.scripts['common']
        while not m.checkState('home'):
            m.forceRun('logi opened')
            util.wait(2)

    def getLogisticTimer(self):
        # maybe make this mult
        m = self.scripts['common']
        m.waitState('home')
        self.openLogi()

        # do ocr
        coord = [833, 148, 998, 187]    # TL and BR of first box
        offset = [0, 113, 225, 338]     # y offsets from top location
        for i in range(4):
            xoff = Context.i.x
            yoff = Context.i.y + offset[i]
            convertedRegion = (
                coord[0] + xoff,
                coord[1] + yoff,
                coord[2] + xoff,
                coord[3] + yoff
            )
            remaining = util.getTimer(util.getScreenText(convertedRegion))
            while remaining is None:
                self.openLogi()
                remaining = util.getTimer(util.getScreenText(convertedRegion))
            self.state['logistic'][i] = remaining
        print(self.state['logistic'])

        self.closeLogi()
