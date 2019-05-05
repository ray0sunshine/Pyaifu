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


def getData(jsonPath):
    o = {}
    with open(jsonPath, 'r') as config:
        o = json.load(config)
    return o


config = config.Config()
data = config.data
Context(data['window'])

files = sys.argv[1:]
scripts = {}
for f in files:
    name, path = f.split('=')
    scripts[name] = Machine(getData(path)) if os.path.exists(path) else path
print(scripts)
