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
    'Small cycle (F5, F6)': lambda: str(Controller.state['smallLoopComplete']) + ' / ' + str(Controller.state['smallLoop']),
    'Big cycle (F7, F8)': lambda: str(Controller.state['bigLoopComplete']) + ' / ' + str(Controller.state['bigLoop']),
    'Repair (ctrl+F7, ctrl+F8)': lambda: str(Controller.state['repairLoopComplete']) + ' / ' + str(Controller.state['repairLoop']),
    'Runtime': lambda: str(Controller.state['runtime']),
    'Running (F2)': lambda: 'PAUSED' if Machine.blocked else 'RUNNING',
    'Waiting': lambda: str(Controller.state['waiting']),
    'Logistics (F3)': lambda: '\n' + '\n'.join(str(round(t)) + 's (' + str(round(t / 60, 1)) + ' min)' for t in [remain - time.time() for remain in Controller.state['logistic']])
}


class Widget(QWidget):
    def __init__(self, parent=None):
        QWidget.__init__(self, parent)
        self.config = config.Config()
        self.data = self.config.data
        Context(self.data['window'])

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

        self.hotkey('f1', self.controller.play)
        self.hotkey('f2', self.controller.pauseToggle)
        self.hotkey('f3', self.getLogiTimer)

        self.hotkey('f12', self.kill)

        timer = QTimer(self)
        timer.setSingleShot(False)
        timer.timeout.connect(self.update)
        timer.start(40)

    def hotkey(self, seq, fn):
        keyboard.add_hotkey(seq, q.put, [seq])
        self.keymap[seq] = fn

    def processKey(self):
        while not q.empty():
            seq = q.get(False)
            if(seq):
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
