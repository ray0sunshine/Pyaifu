# Job specific code, managing the low level state machines, custom actions and such

import util


class Runner:
    def __init__(self, controller):
        self.controller = controller

    def play(self):
        m0 = self.controller.scripts['enter']
        m = self.controller.scripts['battle']
        m2 = self.controller.scripts['ending']
        for _ in range(1):
            m0.run()
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
        util.alert()
