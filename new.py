import pyqtgraph as pg
from PyQt5 import QtCore, QtWidgets
from enum import Enum

class Monitor(QtWidgets.QWidget):
    def __init__(self):
        QtWidgets.QWidget.__init__(self)
        self.cmd = b''
        self.main_layuot = QtWidgets.QGridLayout()
        self.setLayout(self.main_layuot)

        self.graphWidget = pg.PlotWidget()
        self.graphWidget.setBackground('w')
        self.dsb_update = QtWidgets.QDoubleSpinBox()
        self.main_layuot.addWidget(self.graphWidget, 0, 0, 5, 8)
        self.main_layuot.addWidget(QtWidgets.QLabel('Timeout, s'), 5, 0)
        self.main_layuot.addWidget(self.dsb_update, 5, 1)

class Preselector(QtCore.QObject):
    def __init__(self):
        QtCore.QObject.__init__(self)
        self.band = 0
        self.mode = PreamplifierMode.Filters


class PreamplifierMode(Enum):
    Bypass = 0
    Filters = 1
    Off = 2
    WIFI_24GHz = 3

PreamplifierFilters =\
    {
        1: 'Off',
        2: 'Bypass',
        3: '<500 MHz',
        4: '500-1600 MHz',
        5: '1600-3000 MHz',
        6: 'WIFI 2.4 GHz',
        7: '>3000 MHz'
    }
