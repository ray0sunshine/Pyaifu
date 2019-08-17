# Main ui and controls for the player

from helper.context import Context
from helper.controller_player import Controller
from helper.fsm import Machine

import helper.config as config
import sys
import helper.util as util
import keyboard
import queue
import time
import threading

from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

q = queue.Queue()

labelTemplate = {
    'time': lambda: str(time.ctime()),
    'Small cycle (F5, F6)': lambda: str(round(Controller.state['smallLoopComplete'], 1)) + ' / ' + str(Controller.state['smallLoop']),
    'Big cycle (F7, F8)': lambda: str(Controller.state['bigLoopComplete']) + ' / ' + str(Controller.state['bigLoop']),
    'Repair (ctrl+[F7, F8])': lambda: str(Controller.state['repairLoopComplete']) + ' / ' + str(Controller.state['repairLoop']),
    'Runtime': lambda: str(round(time.time() - Controller.state['runtime'])) + 's (' + str(round((time.time() - Controller.state['runtime']) / 60, 1)) + ' min)',
    'Running (F2)': lambda: 'PAUSED' if Machine.blocked else 'RUNNING',
    'Sequence (F4)': lambda: str(Controller.state['sequence']),
    'Restart (shift+[F7, F8])': lambda: str(Controller.state['restart']),
    'Waiting': lambda: str(Controller.state['waiting']),
    'Logistics (F3)': lambda: '\n' + '\n'.join(str(round(t)) + 's (' + str(round(t / 60, 1)) + ' min)' for t in [remain - time.time() for remain in Controller.state['logistic']])
}


class Widget(QWidget):
    def __init__(self, parent=None):
        QWidget.__init__(self, parent)
        self.config = config.Config()
        self.data = self.config.data
        Context(self.data['window'], self.data['window2'])

        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.setAttribute(Qt.WA_TransparentForMouseEvents, True)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setFixedSize(250, 500)
        self.move(Context.i.x, Context.i.y)
        self.font = QFont('Arial', 12, 2)
        self.style = 'color: yellow'

        self.vbox = QVBoxLayout()
        self.vbox.setAlignment(Qt.AlignTop)
        QWidget.setLayout(self, self.vbox)

        self.labels = {}
        for name in labelTemplate:
            self.labels[name] = self.addLabel()
        self.updateLabel()

        self.controller = Controller(sys.argv[1:])
        self.initKeys()

    def initKeys(self):
        self.keymap = {}
        self.argmap = {}

        self.hotkey('f1', self.controller.play)
        self.hotkey('f2', self.controller.pauseToggle)
        self.hotkey('f3', self.getLogiTimer)
        self.hotkey('f4', self.controller.toggleSequence)

        self.hotkey('f5', self.controller.decrement, ['smallLoop'])
        self.hotkey('f6', self.controller.increment, ['smallLoop'])
        self.hotkey('shift+f5', self.controller.decrement, ['smallLoop', 0.5])
        self.hotkey('shift+f6', self.controller.increment, ['smallLoop', 0.5])
        self.hotkey('f7', self.controller.decrement, ['bigLoop'])
        self.hotkey('f8', self.controller.increment, ['bigLoop'])
        self.hotkey('ctrl+f7', self.controller.decrement, ['repairLoop'])
        self.hotkey('ctrl+f8', self.controller.increment, ['repairLoop'])
        self.hotkey('shift+f7', self.controller.decrement, ['restart'])
        self.hotkey('shift+f8', self.controller.increment, ['restart'])

        self.hotkey('f10', self.controller.login)
        self.hotkey('ctrl+f10', self.controller.restart)
        self.hotkey('shift+f10', self.controller.restartRunner)
        self.hotkey('f12', self.kill)

        self.hotkey('a', self.controller.customFunction, [0])
        self.hotkey('s', self.controller.customFunction, [1])
        self.hotkey('d', self.controller.customFunction, [2])
        self.hotkey('f', self.controller.customFunction, [3])

        timer = QTimer(self)
        timer.setSingleShot(False)
        timer.timeout.connect(self.update)
        timer.start(40)

    def hotkey(self, seq, fn, args=None):
        keyboard.add_hotkey(seq, q.put, [seq])
        self.keymap[seq] = fn
        self.argmap[seq] = args

    def processKey(self):
        while not q.empty():
            seq = q.get(False)
            if(seq):
                if self.argmap[seq]:
                    self.keymap[seq](*(self.argmap[seq]))
                else:
                    self.keymap[seq]()

    def addLabel(self):
        label = QLabel()
        label.setStyleSheet(self.style)
        label.setFont(self.font)
        self.vbox.addWidget(label)
        return label

    def updateLabel(self):
        for name, fn in labelTemplate.items():
            self.labels[name].setText(name + ': ' + fn())

    def paintEvent(self, e):
        qp = QPainter()
        qp.begin(self)
        self.processKey()
        self.updateLabel()
        qp.setBrush(QColor(0, 0, 0, 128))
        qp.drawRect(0, 0, 250, 500)
        qp.end()

    def getLogiTimer(self):
        tr = threading.Thread(None, self.controller.getLogisticTimer, 'logiGet')
        tr.start()

    def kill(self):
        self.controller.kill()
        sys.exit()


app = QApplication(sys.argv)
w = Widget()
w.show()
app.exec_()
