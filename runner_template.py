# Job specific code, managing the low level state machines

import util


class Runner:
    def __init__(self, controller):
        print('TEMPLATE LOADED')
        self.controller = controller

    def play(self):
        # Get references to the state machines from controller
        # Run through state machines and use helpers from controller
        print('TEMPLATE PLAYED')
