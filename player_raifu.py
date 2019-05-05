# This is the controller for multiple FSMs defined in json files
# There is custom defined and is responsible for handling:
#   -UI (controls)
#   -Custom functions (OCR etc)
#   -Functionality external to FSM (stat/time tracking, flow control)
#   -Managing multiple FSMs
# This can be called from different batch files with the necessary FSM json files locations in execution sequence

import sys
import json

print(sys.argv[1:])
