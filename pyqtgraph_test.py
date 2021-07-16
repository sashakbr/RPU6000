from PyQt5.QtCore import QDate, QFile, Qt, QTextStream
from PyQt5 import QtGui
from PyQt5.QtPrintSupport import QPrintDialog, QPrinter
from PyQt5.QtWidgets import (QAction, QApplication, QDialog, QDockWidget,
                             QFileDialog, QListWidget, QMainWindow, QProgressBar,QMessageBox, QSlider,QAbstractSlider, QTextEdit, QLabel, QGraphicsLineItem, QCheckBox, QSpinBox, QWidget, QVBoxLayout, QHBoxLayout, QBoxLayout, QPushButton, QComboBox)
from PyQt5.QtCore import QThread, pyqtSignal
import pyqtgraph as pg
import numpy as np
import pyqtgraph.ptime as ptime
import socket

buf_size = 4096     # размер буфера для отображения
HOST_client = '192.168.1.21'
PORT_client = 2000
HOST_server = '192.168.1.22'
PORT_server = 2000

class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.creat_Menu()
        self.createStatusBar()
        self.create_Dock_Spectrum()
        self.create_Dock_Waterfall()
        self.create_Dock_Histogram()
        self.counter = 0

        # self.freq = self.frequencyArray(40000000, 30000000, 9500)
        # self.historyBuffer = HistoryBuffer(9500, 50, int)
        # self.randData = dataGenerator(9500)
        # self.randData.genData.connect(self.updateDataPlote)
        # self.randData.threadRun = True
        # self.randData.start()

        self.freq = self.frequencyArray2(0, 22000, buf_size)
        self.historyBuffer = HistoryBuffer(buf_size, 50, int)
        self.data_tread = UdpClient(HOST_client, PORT_client, HOST_server, PORT_server, buf_size)
        self.data_tread.signalData.connect(self.updateDataPlote)
        self.data_tread.threadRun = True
        self.data_tread.start()

        self.ptr = 0
        self.lastTime = ptime.time()
        self.fps = None

    def creat_Menu(self):
        self.viewMenu = self.menuBar().addMenu("&View")

    def createStatusBar(self):
        self.statusBar().showMessage("Ready")
        self.lb_fps = QLabel()
        self.statusBar().addPermanentWidget(self.lb_fps)
        self.lb_fps.setAlignment(Qt.AlignRight)

    def create_Dock_Spectrum(self):
        self.dock = QDockWidget("Channel 1", self)
        self.dock.GraphicsWindow = pg.GraphicsLayoutWidget(title="Basic plotting examples")
        self.plotSpectrum = self.dock.GraphicsWindow.addPlot(title="Basic Spectrum")
        self.curve_plotSpectrum = self.plotSpectrum.plot(pen=(0, 255, 255), name="Channel 1")
        self.plotSpectrum.setLabel('left', "Amplitude", units='dBm')
        self.plotSpectrum.setLabel('bottom', "Frequency", units='Hz', unitPrefix='M')
        self.plotSpectrum.addLegend(offset=(5, 5))
        #self.plotSpectrum.setYRange(-20, 100)
        #self.plotSpectrum.setMouseEnabled(x=False, y=False)

        self.dock.setWidget(self.dock.GraphicsWindow)
        self.addDockWidget(Qt.LeftDockWidgetArea, self.dock)
        self.viewMenu.addAction(self.dock.toggleViewAction())

    def create_Dock_Waterfall(self):
        self.dock2 = QDockWidget("Waterfall", self)
        self.dock2.win = pg.GraphicsLayoutWidget()
        self.dock2.img = pg.ImageItem()
        self.dock2.plot = self.dock2.win.addPlot()
        self.dock2.plot.addItem(self.dock2.img)
        self.dock2.setWidget(self.dock2.win)

        self.addDockWidget(Qt.LeftDockWidgetArea, self.dock2)
        self.viewMenu.addAction(self.dock2.toggleViewAction())

    def create_Dock_Histogram(self):
        self.dock4 = QDockWidget("Histogram", self)
        self.dock4.win = pg.GraphicsLayoutWidget()
        self.dock4.img = pg.HistogramLUTItem()
        self.dock4.win.addItem(self.dock4.img)
        self.dock4.setWidget(self.dock4.win)
        self.dock4.img.setImageItem(self.dock2.img)
        self.addDockWidget(Qt.RightDockWidgetArea, self.dock4)
        self.dock4.img.gradient.loadPreset("flame")
        self.viewMenu.addAction(self.dock4.toggleViewAction())

    def benchmark(func):
        """
        ...     Декоратор, выводящий время, которое заняло
        ...     выполнение декорируемой функции.
        """
        import time
        def wrapper(*args, **kwargs):
            t = time.clock()
            res = func(*args, **kwargs)
            print(func.__name__, 1/(time.clock() - t))

            return res

        return wrapper

    def frequencyArray(self, centralFreq, span, amountOfPoints):
        return np.arange(centralFreq - span/2, centralFreq + span/2, span/amountOfPoints)

    def frequencyArray2(self, start, stop, amountOfPoints):
        return np.arange(start, stop, (stop-start)/amountOfPoints)

    #@benchmark
    def updateDataPlote(self, data):
        self.counter += 1
        self.historyBuffer.append(data)
        self.dock2.img.setImage(self.historyBuffer.get_buffer().transpose(), autoLevels=False, autoRange=False)
        self.curve_plotSpectrum.setData(self.freq, data)

        self.ptr += 1
        now = ptime.time()
        dt = now - self.lastTime
        self.lastTime = now
        if self.fps is None:
            fps = 1.0 / dt
        else:
            s = np.clip(dt * 3., 0, 1)
            fps = self.fps * (1 - s) + (1.0 / dt) * s
        self.lb_fps.setText('%0.2f fps' % fps)

        #if self.counter == 1 and self.histogram_layout:
        #   self.histogram.setImageItem(self.waterfallImg)


class UdpClient(QThread):
    signalData = pyqtSignal(np.ndarray)

    def __init__(self, HOST_client, PORT_client, HOST_server, PORT_server, bufSize:int):
        super().__init__()
        self.bufSize = bufSize
        self.threadRun = False
        self.address = (HOST_server, PORT_server)
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind((HOST_client, PORT_client))

    def run(self):
        while self.threadRun:
            self.sock.sendto('Q'.encode(), self.address)
            data = self.sock.recv(1024)
            data += self.sock.recv(1024)
            data += self.sock.recv(1024)
            data += self.sock.recv(1024)
            data += self.sock.recv(1024)
            data += self.sock.recv(1024)
            data += self.sock.recv(1024)
            data += self.sock.recv(1024)
            data = np.frombuffer(data, dtype=np.uint16) # numpy buf
            bpf = abs(np.fft.fft(data).real)

            self.signalData.emit(bpf)
            self.msleep(25)
        self.finished.emit()


class dataGenerator(QThread):
    genData = pyqtSignal(np.ndarray)

    def __init__(self, bufSize:int):
        super().__init__()
        self.bufSize = bufSize
        self.threadRun = False

    def run(self):
        while self.threadRun:
            self.genData.emit(np.random.normal(size=self.bufSize))
            QThread.msleep(20)
        self.finished.emit()

class HistoryBuffer:
    """Fixed-size NumPy array ring buffer"""
    def __init__(self, data_size, max_history_size, dtype=float):
        self.data_size = data_size
        self.max_history_size = max_history_size
        self.history_size = 0
        self.counter = 0
        self.buffer = np.empty(shape=(max_history_size, data_size), dtype=dtype)

    def append(self, data):
        """Append new data to ring buffer"""
        self.counter += 1
        if self.history_size < self.max_history_size:
            self.history_size += 1
        self.buffer = np.roll(self.buffer, -1, axis=0)
        self.buffer[-1] = data

    def get_buffer(self):
        """Return buffer stripped to size of actual data"""
        if self.history_size < self.max_history_size:
            return self.buffer[-self.history_size:]
        else:
            return self.buffer

    def __getitem__(self, key):
        return self.buffer[key]


if __name__ == '__main__':

    import sys

    app = QApplication(sys.argv)
    mainWin = MainWindow()
    mainWin.resize(1200, 600)
    mainWin.show()
    sys.exit(app.exec_())