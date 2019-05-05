# This is the controller for multiple FSMs defined in json files
# There is custom defined and is responsible for handling:
#   -UI (controls)
#   -Custom functions (OCR etc)
#   -Functionality external to FSM (stat/time tracking, flow control)
#   -Managing multiple FSMs
# This can be called from different batch files with the necessary FSM json files locations in execution sequence

from jsonSerializer import jsonSerialize
from fsm import Machine
from context import Context

import config
import sys
import json

config = config.Config()
data = config.data
Context(data['window'])

files = sys.argv[1:]
for f in files:
    with open(f, 'r') as config:
        o = json.load(config)
        machine = Machine(o)
        for k in machine.state:
            v = machine.state[k]
        machine.run()
