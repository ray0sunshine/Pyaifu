from context import Context
import mouse
import util
import numpy

from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *


CLICK_SIMS = 1000
DRAG_SIMS = 50


class Controller:
    def __init__(self):
        self.count = 0
        self.cur = None
        self.idx = 0
        self.steps = []

    def addPixel(self):
        if self.cur:
            pos = mouse.getMousePos()
            c = mouse.getMouseColor()
            cinv = tuple(255 - v for v in c)
            self.cur['marks'].append((c, cinv, pos))
            self.cur['pixel'].append({
                'pos': pos,
                'rgb': c
            })

    def removePixel(self):
        if self.cur and len(self.cur['marks']) > 0:
            self.cur['marks'].pop()
            self.cur['pixel'].pop()

    def makeClick(self, action):
        if self.cur and len(self.cur['pixel']) >= 2:
            self.cur['function'] = {
                'action': action,
                'data': {
                    'wait': self.cur['function']['data']['wait'] if self.cur['function'] else 0.75,
                    'retry': self.cur['function']['data']['retry'] if self.cur['function'] else 1.5,
                    'points': []
                }
            }

            for _ in range(2):
                self.cur['marks'].pop()
                self.cur['function']['data']['points'].append(self.cur['pixel'].pop()['pos'])

            img = QImage(Context.i.w, Context.i.h, QImage.Format_ARGB4444_Premultiplied)
            painter = QPainter(img)
            painter.setPen(QPen(Qt.red, 2, Qt.SolidLine))
            for _ in range(CLICK_SIMS):
                if action == 'rect':
                    pt = util.irpoint(*self.cur['function']['data']['points'])
                    painter.drawPoint(*pt)
                elif action == 'circle':
                    pt = util.icpoint(*self.cur['function']['data']['points'])
                    painter.drawPoint(*pt)
            painter.end()
            self.cur['pmap'] = QPixmap.fromImage(img)

    def makeMiddleClick(self):
        if self.cur:
            self.cur['function'] = {
                'action': 'middle',
                'data': {
                    'wait': 0.75,
                    'retry': 1.5
                }
            }

    def makeDrag(self):
        if self.cur and len(self.cur['pixel']) >= 4:
            self.cur['function'] = {
                'action': 'drag',
                'data': {
                    'wait': 0.75,
                    'retry': 1.5,
                    'points': []
                }
            }

            for _ in range(4):
                self.cur['marks'].pop()
                self.cur['function']['data']['points'].append(self.cur['pixel'].pop()['pos'])

            # this last point popped was the first placed hence it should be the start
            self.cur['function']['data']['points'].reverse()

            img = QImage(Context.i.w, Context.i.h, QImage.Format_ARGB4444_Premultiplied)
            painter = QPainter(img)
            painter.setPen(QPen(Qt.red, 2, Qt.SolidLine))
            painter.setOpacity(0.3)
            for _ in range(DRAG_SIMS):
                p1, p2, p3, p4 = util.cubicRandomPoints(*self.cur['function']['data']['points'])
                path = QPainterPath()
                path.moveTo(*p1)
                for t in numpy.arange(0, 1, 0.05):
                    path.lineTo(*util.cubicBezier(p1, p2, p3, p4, t))
                painter.drawPath(path)
            painter.end()
            self.cur['pmap'] = QPixmap.fromImage(img)

    def prevState(self):
        if self.cur:
            self.idx = max(0, self.idx - 1)
            self.cur = self.steps[self.idx]

    def nextState(self):
        if self.cur:
            self.idx = min(len(self.steps) - 1, self.idx + 1)
            self.cur = self.steps[self.idx]

    def newState(self):
        step = {
            'name': 'state ' + str(self.count),
            'pixel': [],
            'marks': [],
            'function': {},
            'next': [],
            'pmap': None
        }
        self.count += 1

        if self.cur:
            self.idx += 1
            for s in self.steps:
                s['next'] = [n + 1 if n >= self.idx else n for n in s['next']]
            self.cur['next'].append(self.idx)
        self.steps.insert(self.idx, step)
        self.cur = self.steps[self.idx]
        return self.idx, self.cur

    def removeState(self):
        if self.cur:
            oldRow = self.idx
            for s in self.steps:
                if self.idx in s['next']:
                    s['next'].remove(self.idx)
                s['next'] = [n - 1 if n >= self.idx else n for n in s['next']]
            self.steps.remove(self.cur)
            if not self.steps:
                self.cur = None
                self.idx = 0
            else:
                if self.idx > 0:
                    self.idx -= 1
                self.cur = self.steps[self.idx]
            return oldRow
        return None

    def load(self, o):
        self.steps = list(o['fsm'].values())
        self.count = len(self.steps)
        names = [self.steps[i]['name'] for i in range(self.count)]
        for i in range(len(self.steps)):
            step = self.steps[i]
            step['next'] = [names.index(name) for name in step['next']]
            step['marks'] = []
            step['pmap'] = None
            allpix = step['pixel']
            if step['function'] and step['function']['action'] != 'middle':
                for pix in step['function']['data']['points']:
                    allpix.append({
                        'pos': pix,
                        'rgb': [0, 0, 0]
                    })
            for pix in allpix:
                pix['pos'] = tuple(pix['pos'])
                pix['rgb'] = tuple(pix['rgb'])
                cinv = tuple(255 - v for v in pix['rgb'])
                step['marks'].append((pix['rgb'], cinv, pix['pos']))

            self.cur = step
            self.idx = i
            if self.cur['function']:
                action = self.cur['function']['action']
                if action == 'drag':
                    self.makeDrag()
                elif action != 'middle':
                    self.makeClick(action)
