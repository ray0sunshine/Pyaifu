# Main ui and controls for the player

from helper.context import Context
from helper.controller_player import Controller

import helper.config as config
import sys
import helper.util as util
import keyboard
import queue

from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

q = queue.Queue()


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

        self.controller = Controller(sys.argv[1:])

        self.initKeys()

    def initKeys(self):
        self.keymap = {}

        self.hotkey('f1', util.alert)
        self.hotkey('f2', self.kill)
        self.hotkey('f3', self.controller.getLogisticTimer)

        self.hotkey('f5', self.controller.play)
        self.hotkey('f6', self.controller.pauseToggle)

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

    def paintEvent(self, e):
        self.processKey()
        qp = QPainter()
        qp.begin(self)
        qp.setBrush(QColor(0, 0, 0, 128))
        qp.drawRect(0, 0, 250, 500)
        qp.end()

    def kill(self):
        self.controller.kill()
        sys.exit()


app = QApplication(sys.argv)
w = Widget()
w.show()
app.exec_()
