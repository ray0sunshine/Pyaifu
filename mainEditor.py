import sys
import re
import json
import queue
import keyboard

from context import Context
from controller_editor import Controller
from jsonSerializer import jsonSerialize
import config
import util

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
        self.controller = Controller()

        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.setAttribute(Qt.WA_TransparentForMouseEvents, True)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setFixedSize(Context.i.w, Context.i.h)
        self.move(Context.i.x, Context.i.y)

        self.marks = []
        self.pen = QPen()
        self.brush = QBrush()
        self.painter = QPainter()

        self.initKeys()

        self.filename = None
        self.labels = []
        self.form = QFormLayout()
        gbox = QGroupBox()
        gbox.setLayout(self.form)

        scroll = QScrollArea()
        scroll.setStyleSheet("background-color:rgba(0,0,0,0.3)")
        scroll.setWidget(gbox)
        scroll.setWidgetResizable(True)
        scroll.setFixedHeight(Context.i.h)
        scroll.setFixedWidth(250)
        scroll.setParent(self)

    def paintEvent(self, e):
        self.painter.begin(self)
        if self.controller.cur and self.controller.cur['pmap']:
            self.painter.drawPixmap(self.rect(), self.controller.cur['pmap'])
        if self.controller.cur:
            for mark in self.controller.cur['marks']:
                self.mark(*mark)
        self.painter.end()

    def initKeys(self):
        self.keymap = {}

        self.hotkey('f1', self.addPixel)
        self.hotkey('ctrl+f1', self.removePixel)
        self.hotkey('f2', self.makeRectClick)
        self.hotkey('ctrl+f2', self.makeMiddleClick)
        self.hotkey('f3', self.makeCircleClick)
        self.hotkey('ctrl+f3', self.getWait)
        self.hotkey('f4', self.makeDrag)
        self.hotkey('ctrl+f4', self.getRetry)

        self.hotkey('f5', self.prevStep)
        self.hotkey('f6', self.nextStep)
        self.hotkey('f7', self.newStep)
        self.hotkey('f8', self.removeStep)

        self.hotkey('f10', self.screenshotFile)

        self.hotkey('ctrl+o', self.loadFile)
        self.hotkey('ctrl+s', self.saveFile)
        self.hotkey('ctrl+shift+s', self.saveFileAs)

        timer = QTimer(self)
        timer.setSingleShot(False)
        timer.timeout.connect(self.processKey)
        timer.start(40)

    def hotkey(self, seq, fn):
        keyboard.add_hotkey(seq, q.put, [seq])
        self.keymap[seq] = fn

    def processKey(self):
        while not q.empty():
            seq = q.get(False)
            if(seq):
                self.keymap[seq]()

    def addPixel(self):
        self.controller.addPixel()
        self.update()

    def removePixel(self):
        self.controller.removePixel()
        self.update()

    def makeRectClick(self):
        self.controller.makeClick('rect')
        self.updateLabels()
        self.update()

    def makeCircleClick(self):
        self.controller.makeClick('circle')
        self.updateLabels()
        self.update()

    def makeMiddleClick(self):
        self.controller.makeMiddleClick()
        self.updateLabels()
        self.update()

    def makeDrag(self):
        self.controller.makeDrag()
        self.updateLabels()
        self.update()

    def getDelay(self, kind):
        if self.controller.cur and self.controller.cur['function']:
            Context.i.setFocus()
            cur = self.controller.cur
            cur['function']['data'][kind] = QInputDialog.getDouble(
                self, 'Set ' + kind + ' time', 'Seconds:',
                cur['function']['data'][kind],
                0, 180, 2)[0]
            self.updateLabels()
            self.update()

    def getWait(self):
        self.getDelay('wait')

    def getRetry(self):
        self.getDelay('retry')

    def screenshotFile(self):
        util.getScreen((Context.i.x, Context.i.y, Context.i.x2, Context.i.y2), 'out/ss_')

    def updateLabels(self):
        encounteredNames = set()
        for i in range(len(self.labels)):
            ql = self.labels[i]
            cur = self.controller.steps[i]
            name = ''
            if not ql.text() == '':
                name = re.search('<(.+?)>', ql.text()).group(1)
                cur['name'] = name
            else:
                name = cur['name']

            # do unique check
            if name in encounteredNames:
                print('"' + name + '" is a dupe: i=' + str(i))
            else:
                encounteredNames.add(name)

            appendix = ''
            if cur['function']:
                appendix += ' {' + str(cur['function']['data']['wait']) + ', ' + str(cur['function']['data']['retry']) + '}'
                if cur['function']['action'] == 'middle':
                    appendix += ' |MID|'

            ql.setText(str(i) + ' - <' + cur['name'] + '> ' + str(cur['next']) + appendix)
            if self.controller.idx == i:
                ql.setStyleSheet("color: white; background-color:rgba(0,255,0,0.3)")
            else:
                ql.setStyleSheet("color: white; background-color:rgba(255,0,0,0.3)")

    def prevStep(self):
        self.controller.prevState()
        self.updateLabels()
        self.update()

    def nextStep(self):
        self.controller.nextState()
        self.updateLabels()
        self.update()

    def newStep(self):
        idx, cur = self.controller.newState()
        ql = QLineEdit(str(idx) + ' - <' + cur['name'] + '> []')
        ql.setStyleSheet("color: white; background-color:rgba(255,0,0,0.3)")
        self.labels.insert(idx, ql)
        self.form.insertRow(idx, ql)
        self.updateLabels()
        self.update()

    def removeStep(self):
        res = self.controller.removeState()
        if res is not None:
            self.form.removeRow(self.labels.pop(res))
        self.updateLabels()
        self.update()

    def loadFile(self):
        loadFilename = QFileDialog.getOpenFileName(self, 'Save json', '', 'JSON (*.json)')[0]
        if loadFilename:
            with open(loadFilename, 'r') as config:
                o = json.load(config)
                self.controller.load(o)
                self.labels = []
                while not self.form.isEmpty():
                    self.form.removeRow(0)
                for _ in range(len(o['fsm'].keys())):
                    ql = QLineEdit('')
                    self.labels.append(ql)
                    self.form.addRow(ql)
                self.updateLabels()
                self.update()

    def saveFileAs(self):
        self.filename = QFileDialog.getSaveFileName(self, 'Save json', '', 'JSON (*.json)')[0]
        if self.filename:
            self.save()

    def saveFile(self):
        if self.filename:
            self.save()
        else:
            self.saveFileAs()

    def save(self):
        self.updateLabels()
        steps = self.controller.steps
        o = {
            'start': steps[0]['name'],
            'fsm': {}
        }
        for step in steps:
            o['fsm'][step['name']] = {
                'name': step['name'],
                'pixel': step['pixel'],
                'function': step['function'],
                'next': [steps[i]['name'] for i in step['next']]
            }

        with open(self.filename, 'w') as config:
            config.write(jsonSerialize(o))

    def mark(self, color, inverse, pos):
        self.pen.setColor(QColor(*inverse))
        self.pen.setWidth(3)
        self.painter.setBrush(QColor(*color))
        self.painter.setPen(self.pen)
        self.painter.drawEllipse(QPoint(*pos), 6, 6)


app = QApplication(sys.argv)
w = Widget()
w.show()
app.exec_()
