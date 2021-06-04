import pyqtgraph as pg
from PyQt5 import QtCore, QtWidgets
from enum import Enum


class Monitor(QtWidgets.QWidget):
    def __init__(self):
        QtWidgets.QWidget.__init__(self)
        self.cmd = b''
        self.main_layout = QtWidgets.QGridLayout()
        self.setLayout(self.main_layout)

        self.graphWidget = pg.PlotWidget()
        self.graphWidget.setBackground('w')
        self.dsb_update = QtWidgets.QDoubleSpinBox()
        self.main_layout.addWidget(self.graphWidget, 0, 0, 5, 8)
        self.main_layout.addWidget(QtWidgets.QLabel('Timeout, s'), 5, 0)
        self.main_layout.addWidget(self.dsb_update, 5, 1)


class Filters(QtWidgets.QComboBox):
    def __init__(self, items: dict):
        QtWidgets.QComboBox.__init__(self)
        self._items = items
        self.__set_items()

    def __set_items(self):
        for data, name in self._items.items():
            self.addItem(name, data)

    def set_current_item(self, data):
        self.blockSignals(True)
        self.setCurrentText(self._items[data])
        self.blockSignals(False)

    def get_current_item(self):
        return self.currentData()


class Gain(QtWidgets.QSlider):
    def __init__(self):
        QtWidgets.QSlider.__init__(self, orientation=QtCore.Qt.Horizontal)
        self.setMaximum(31)
        self.setMinimum(0)

    def get_value(self):
        return self.value()

    def set_value(self, value: int):
        self.blockSignals(True)
        self.setValue(value)
        self.blockSignals(False)


class Preamplifier(QtWidgets.QGroupBox):
    def __init__(self):
        QtWidgets.QGroupBox.__init__(self, 'Preamplifier')
        self.filters = Filters(PreamplifierFilters)
        self.gain = Gain()

        self.main_layout = QtWidgets.QGridLayout()
        self.setLayout(self.main_layout)
        self.main_layout.addWidget(QtWidgets.QLabel('Input'), 0, 0)
        self.main_layout.addWidget(self.filters, 0, 1)
        self.main_layout.addWidget(QtWidgets.QLabel('Gain'))
        self.main_layout.addWidget(self.gain, 1, 1)


class BpfBlock(QtWidgets.QGroupBox):
    def __init__(self):
        QtWidgets.QGroupBox.__init__(self, 'Bandpass filters block')
        self.filters = Filters(PreamplifierFilters)
        self.gain = Gain()

        self.main_layout = QtWidgets.QGridLayout()
        self.setLayout(self.main_layout)
        self.main_layout.addWidget(QtWidgets.QLabel('BPF'), 0, 0)
        self.main_layout.addWidget(self.filters, 0, 1)
        self.main_layout.addWidget(QtWidgets.QLabel('Gain'))
        self.main_layout.addWidget(self.gain, 1, 1)


class PreselectorMode(QtWidgets.QGroupBox):
    def __init__(self):
        QtWidgets.QGroupBox.__init__(self, 'Mode')

        self.bypass = QtWidgets.QRadioButton('Bypass')
        self.filters = QtWidgets.QRadioButton('Filters')
        self.off = QtWidgets.QRadioButton('Off')
        self.wifi = QtWidgets.QRadioButton('WIFI 2.4GHz')

        layout = QtWidgets.QGridLayout()
        self.setLayout(layout)
        layout.addWidget(self.bypass)
        layout.addWidget(self.filters)
        layout.addWidget(self.off)
        layout.addWidget(self.wifi)


class Preselector(QtWidgets.QWidget):
    def __init__(self):
        QtWidgets.QWidget.__init__(self)
        self.band = 0
        self.main_layout = QtWidgets.QGridLayout()
        self.setLayout(self.main_layout)

        self.mode = PreselectorMode()
        self.band = QtWidgets.QSpinBox()
        self.band.setMaximum(13)
        self.preamplifier = Preamplifier()
        self.bpf_block = BpfBlock()

        self.main_layout.addWidget(self.mode, 0, 0)
        self.main_layout.addWidget(QtWidgets.QLabel('Band'), 1, 0)
        self.main_layout.addWidget(self.band, 2, 0)
        self.main_layout.addWidget(self.preamplifier, 0, 1, 3, 2)
        self.main_layout.addWidget(self.bpf_block, 0, 4, 3, 2)


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
