import win32ui as win
import win32gui as wgui
import win32com.client
import threading


class Context:
    i = None

    def __init__(self, windowName, windowName2=''):
        Context.i = self
        self.lock = threading.Lock()
        try:
            self.window = win.FindWindow(None, windowName)
        except:
            if windowName2 != '':
                windowName = windowName2
            else:
                windowName = self.getForegroundWindow()
            self.window = win.FindWindow(None, windowName)

        print('context:', windowName)
        self.x, self.y, self.x2, self.y2 = wgui.GetWindowRect(wgui.FindWindow(None, windowName))
        self.w = self.x2 - self.x
        self.h = self.y2 - self.y

    def getColor(self, x, y):
        self.lock.acquire()
        SUCCESS = False
        while not SUCCESS:
            try:
                self.context = self.window.GetWindowDC()
                c = self.context.GetPixel(x, y)
                SUCCESS = True
            except:
                print('get pixel (%s, %s) fail' % (x, y))
            self.context.DeleteDC()
        self.lock.release()
        return (c & 0xff), ((c >> 8) & 0xff), ((c >> 16) & 0xff)

    # sets the python app as the focus...I don't know why it works this way lol
    def setFocus(self):
        handle = wgui.FindWindow(None, 'python')
        if handle:
            win32com.client.Dispatch("WScript.Shell").SendKeys('')
            wgui.SetForegroundWindow(handle)

    def getForegroundWindow(self):
        print(wgui.GetWindowText(wgui.GetForegroundWindow()))
