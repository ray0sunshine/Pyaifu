# This is the controller for multiple FSMs defined in json files
# There is custom defined and is responsible for handling:
#   -UI (controls)
#   -Custom functions (OCR etc)
#   -Functionality external to FSM (stat/time tracking, flow control)
#   -Managing multiple FSMs
# This can be called from different batch files with the necessary FSM json files locations in execution sequence

from fsm import Machine
from context import Context

import config
import sys
import os
import json
import util
import winsound


def getData(jsonPath):
    o = {}
    with open(jsonPath, 'r') as config:
        o = json.load(config)
    return o


def alert():
    winsound.PlaySound('alert.wav', winsound.SND_FILENAME | winsound.SND_ASYNC)


config = config.Config()
data = config.data
Context(data['window'])

files = sys.argv[1:]
scripts = {}
for f in files:
    name, path = f.split('=')
    scripts[name] = Machine(getData(path)) if os.path.exists(path) else path
print(scripts)

m = scripts['battle']
m2 = scripts['ending']
for _ in range(7):
    scripts['enter'].run()
    for i in range(4):
        m.waitState('battle')
        m.waitState('battle', inverse=True)
        util.wait(2.5)
        while not m.checkState('loading'):
            m.forceRun('clicks')
            util.wait(0.2, 0.2)

    m2.waitState('ending')
    while not m2.checkState('stats'):
        m2.forceRun('ending')
        util.wait(10)

    while not m.checkState('loading'):
        m2.forceRun('stats')
        util.wait(0.2, 0.2)

alert()
