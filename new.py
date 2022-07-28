import pyqtgraph as pg
from PyQt5 import QtCore, QtWidgets, QtGui
from enum import Enum
import numpy as np


class LCDArrayWidget(QtWidgets.QWidget):
    def __init__(self, count: int, orientation='h'):
        QtWidgets.QWidget.__init__(self)
        if orientation == 'v':
            self.main_layout = QtWidgets.QVBoxLayout()
        else:
            self.main_layout = QtWidgets.QHBoxLayout()
        self.setLayout(self.main_layout)
        self.widgets = []

        for i in range(count):
            widget = QtWidgets.QLCDNumber()
            self.widgets.append(widget)
            self.main_layout.addWidget(widget)
            widget.setSegmentStyle(QtWidgets.QLCDNumber.Flat)
            widget.setDigitCount(4)

    def set_value(self, values: list or tuple):
        for i, widget in enumerate(self.widgets):
            try:
                widget.display(values[i])
                widget.setEnabled(True)
            except IndexError:
                widget.display('--')
                widget.setEnabled(False)
        # for i in range(len(self.widgets)):
        #     try:
        #         self.widgets[i].display(value[i])
        #         self.widgets[i].setEnabled(True)
        #     except:
        #         self.widgets[i].display('--')
        #         self.widgets[i].setEnabled(False)


class Monitor(QtWidgets.QWidget):
    signal = QtCore.pyqtSignal()

    def __init__(self, count: int, names: list):
        QtWidgets.QWidget.__init__(self)
        self.cmd = b''
        self.main_layout = QtWidgets.QGridLayout()
        self.setLayout(self.main_layout)
        self.buf = [[], [], []]
        self.ind = 0

        self.graphWidget = pg.GraphicsLayoutWidget()
        #self.graphWidget.setBackground('w')
        self.plot = self.graphWidget.addPlot()
        self.plot_legend = self.plot.addLegend(offset=(-25, 10))
        self.plot.showGrid(x=False, y=True)
        self.plot.showAxis('bottom', show=False)

        colors = [(0, 0, 200), (100, 200, 0), (126, 47, 142), (0, 114, 189),  (0, 128, 0)]
        self.curves = []
        for i in range(count):
            self.curves.append(self.plot.plot(self.buf[i], name=names[i], pen=colors[i], penSize=8))

        self.btn_start = QtWidgets.QPushButton('Start')
        self.btn_start.setCheckable(True)

        self.dsb_timeout = QtWidgets.QDoubleSpinBox()
        self.dsb_timeout.setMaximum(1000)
        self.dsb_timeout.setValue(5)

        self.sb_points = QtWidgets.QSpinBox()
        self.sb_points.setMaximum(10000)
        self.sb_points.setValue(200)

        self.int_array = LCDArrayWidget(count)

        self.main_layout.addWidget(self.btn_start, 0, 0)
        self.main_layout.addWidget(self.int_array, 0, 7)
        self.main_layout.addWidget(self.graphWidget, 1, 0, 5, 8)

        self.main_layout.addWidget(QtWidgets.QLabel('Timeout, s'), 10, 0)
        self.main_layout.addWidget(self.dsb_timeout, 10, 1)
        self.main_layout.addWidget(QtWidgets.QLabel('Amount of points'), 10, 3)
        self.main_layout.addWidget(self.sb_points, 10, 4)

        self.btn_start.clicked.connect(self.timer_event)

    def set_left_lable(self, text: str, units=None):
        self.plot.setLabel('left', text, units=units)

    def timer_event(self):
        if self.btn_start.isChecked():
            self.ind = 0
            self.buf = [[], [], []]
            self.__start_timer()
        else:
            self.__stop_timer()

    def __start_timer(self):
        self.timer = self.startTimer(int(self.dsb_timeout.value()*1000), QtCore.Qt.VeryCoarseTimer)
        self.btn_start.setText('Stop')
        self.dsb_timeout.setDisabled(True)

    def __stop_timer(self):
        self.killTimer(self.timer)
        self.btn_start.setText('Start')
        self.dsb_timeout.setDisabled(False)

    def timerEvent(self, event):
        self.signal.emit()

    def appendData(self, temps: list):
        self.ind += 1
        self.int_array.set_value(temps)
        for i, temp in enumerate(temps):
            if len(self.buf[i]) == self.sb_points.value():
                self.buf[i].append(temp)
                self.buf[i] = self.buf[i][1:]
                self.curves[i].setPos(self.ind, 0)
            elif len(self.buf[i]) > self.sb_points.value():
                self.buf[i].append(temp)
                self.buf[i] = self.buf[i][len(self.buf[i]) - self.sb_points.value():]
            else:
                self.buf[i].append(temp)
            self.curves[i].setData(np.array(self.buf[i]))

    # self.ind += 1
        # self.int_array.set_value(temp)
        # for i in range(len(temp)):
        #     if len(self.buf[i]) == self.sb_points.value():
        #         self.buf[i].append(temp[i])
        #         self.buf[i] = self.buf[i][1:]
        #         self.curves[i].setPos(self.ind, 0)
        #     elif len(self.buf[i]) > self.sb_points.value():
        #         self.buf[i].append(temp[i])
        #         self.buf[i] = self.buf[i][len(self.buf[i]) - self.sb_points.value():]
        #     else:
        #         self.buf[i].append(temp[i])
        #     self.curves[i].setData(np.array(self.buf[i]))


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


class Gain(QtWidgets.QWidget):
    value_changed = QtCore.pyqtSignal(int)

    def __init__(self, min_=0, max_=31, step=1, orientation=QtCore.Qt.Horizontal):
        QtWidgets.QWidget.__init__(self)
        self.slider = QtWidgets.QSlider(orientation=orientation)
        self.spinbox = QtWidgets.QSpinBox()
        self.set_minimum(min_)
        self.set_maximum(max_)
        self.set_step(step)

        if orientation == QtCore.Qt.Horizontal:
            layout = QtWidgets.QHBoxLayout()
            self.setMinimumWidth(120)
        elif orientation == QtCore.Qt.Vertical:
            layout = QtWidgets.QHBoxLayout()
            self.setMinimumHeight(100)
        self.setLayout(layout)
        layout.addWidget(self.slider)
        layout.addWidget(self.spinbox)

        self.slider.valueChanged.connect(self.__valueChangedHandel)
        self.spinbox.valueChanged.connect(self.__valueChangedHandel)

    def __valueChangedHandel(self, value):
        self.set_value(value)
        self.value_changed.emit(value)

    def set_maximum(self, value: int):
        self.slider.setMaximum(value)
        self.spinbox.setMaximum(value)

    def set_minimum(self, value: int):
        self.slider.setMinimum(value)
        self.spinbox.setMinimum(value)

    def set_step(self, value):
        self.slider.setSingleStep(value)
        self.spinbox.setSingleStep(value)

    def get_value(self):
        return self.spinbox.value()

    def set_value(self, value: int):
        self.slider.blockSignals(True)
        self.spinbox.blockSignals(True)
        self.slider.setValue(value)
        self.spinbox.setValue(value)
        self.slider.blockSignals(False)
        self.spinbox.blockSignals(False)


class Preamplifier(QtWidgets.QGroupBox):
    def __init__(self):
        QtWidgets.QGroupBox.__init__(self, 'Preamplifier')
        self.main_layout = QtWidgets.QGridLayout()
        self.setLayout(self.main_layout)

        self.filters = Filters(PreamplifierFilters)
        self.gain = Gain()
        # self.gain.value_changed.connect(lambda value: print(value))

        self.main_layout.addWidget(QtWidgets.QLabel('Input'), 0, 0)
        self.main_layout.addWidget(self.filters, 0, 1)
        self.main_layout.addWidget(QtWidgets.QLabel('Gain'))
        self.main_layout.addWidget(self.gain, 1, 1)


class BpfBlock(QtWidgets.QGroupBox):
    def __init__(self):
        QtWidgets.QGroupBox.__init__(self, 'Bandpass filters block')
        self.main_layout = QtWidgets.QGridLayout()
        self.setLayout(self.main_layout)

        self.filters = Filters(PreamplifierFilters)
        self.gain = Gain()

        self.main_layout.addWidget(QtWidgets.QLabel('BPF'), 0, 0)
        self.main_layout.addWidget(self.filters, 0, 1)
        self.main_layout.addWidget(QtWidgets.QLabel('Gain'))
        self.main_layout.addWidget(self.gain, 1, 1)


class PreselectorMode(QtWidgets.QGroupBox):
    mode_changed = QtCore.pyqtSignal(int)

    def __init__(self):
        QtWidgets.QGroupBox.__init__(self, 'Mode')

        self.bypass = QtWidgets.QRadioButton('Bypass')
        self.filters = QtWidgets.QRadioButton('Filters')
        self.filters.click()
        self.off = QtWidgets.QRadioButton('Off')
        self.wifi = QtWidgets.QRadioButton('WIFI 2.4GHz')

        layout = QtWidgets.QGridLayout()
        self.setLayout(layout)
        layout.addWidget(self.bypass)
        layout.addWidget(self.filters)
        layout.addWidget(self.off)
        layout.addWidget(self.wifi)

        self.items = \
            {
                0: self.bypass,
                1: self.filters,
                2: self.off,
                3: self.wifi,
            }

        self.bypass.clicked.connect(lambda: self.mode_changed.emit(0))
        self.filters.clicked.connect(lambda: self.mode_changed.emit(1))
        self.off.clicked.connect(lambda: self.mode_changed.emit(2))
        self.wifi.clicked.connect(lambda: self.mode_changed.emit(3))

    def set_mode(self, num: int):
        try:
            self.items[num].blockSignals(True)
            self.items[num].click()
            self.items[num].blockSignals(False)
        except Exception as e:
            print(f'Preselector mode value [{e}] ERROR!')


class Preselector(QtWidgets.QGroupBox):
    def __init__(self, embed=False):
        QtWidgets.QGroupBox.__init__(self, 'Preselector')
        self.band = 0
        self.main_layout = QtWidgets.QGridLayout()
        self.setLayout(self.main_layout)

        self.mode = PreselectorMode()
        self.band = QtWidgets.QSpinBox()
        self.band.setMaximum(13)
        self.preamplifier = Preamplifier()
        self.bpf_block = BpfBlock()

        self.main_layout.addWidget(self.mode, 0, 0)
        if embed:
            self.main_layout.addWidget(QtWidgets.QLabel('Band'), 1, 0)
            self.main_layout.addWidget(self.band, 2, 0)
        self.main_layout.addWidget(self.preamplifier, 0, 1, 3, 2)
        self.main_layout.addWidget(self.bpf_block, 0, 4, 3, 2)


class LORange(QtWidgets.QGroupBox):
    value_changed = QtCore.pyqtSignal(int)

    def __init__(self):
        QtWidgets.QGroupBox.__init__(self, 'Range')
        self.main_layout = QtWidgets.QGridLayout()
        self.setLayout(self.main_layout)

        self.setFixedSize(80, 80)

        self.high = QtWidgets.QRadioButton('High')
        self.low = QtWidgets.QRadioButton('Low')
        self.high.setChecked(True)

        self.main_layout.addWidget(self.high)
        self.main_layout.addWidget(self.low)

        self.items = \
            {
                0: self.low,
                1: self.high,
            }
        self.low.clicked.connect(lambda: self.value_changed.emit(0))
        self.high.clicked.connect(lambda: self.value_changed.emit(1))

    def set_value(self, num: int):
        try:
            self.items[num].blockSignals(True)
            self.items[num].click()
            self.items[num].blockSignals(False)
        except Exception as e:
            print(f'Preselector mode value [{e}] ERROR!')


class LO(QtWidgets.QGroupBox):
    def __init__(self, num, gain_on=True):
        QtWidgets.QGroupBox.__init__(self, 'LO' + str(num))
        self.main_layout = QtWidgets.QGridLayout()
        self.setLayout(self.main_layout)

        self.range = LORange()
        self.freq = QtWidgets.QSpinBox()
        self.freq.setMinimum(10)
        self.freq.setMaximum(15000)
        self.level = QtWidgets.QSpinBox()
        self.level.setDisabled(True)
        #self.gain = Gain(orientation=QtCore.Qt.Vertical)
        self.gain = Gain(orientation=QtCore.Qt.Horizontal)

        self.main_layout.addWidget(self.range, 0, 1)
        self.main_layout.addWidget(QtWidgets.QLabel('Freq.'), 1, 0)
        self.main_layout.addWidget(self.freq, 1, 1, 1, 2)
        self.main_layout.addWidget(QtWidgets.QLabel('Level'), 2, 0)
        self.main_layout.addWidget(self.level, 2, 1, 1, 2)
        if gain_on:
            self.main_layout.addWidget(QtWidgets.QLabel('Gain'), 3, 0)
            self.main_layout.addWidget(self.gain, 3, 1, 1, 2)

    def set_freq(self, value: int):
        self.freq.blockSignals(True)
        self.freq.setValue(value)
        self.freq.blockSignals(False)

    def set_range(self, value: int):
        self.range.set_value(value)

    def set_level(self, value: int):
        self.level.setValue(value)

    def set_gain(self, value: int):
        self.gain.set_value(value)


class Out(QtWidgets.QGroupBox):
    def __init__(self):
        QtWidgets.QGroupBox.__init__(self)
        self.main_layout = QtWidgets.QGridLayout()
        self.setLayout(self.main_layout)

        self.gain = Gain(orientation=QtCore.Qt.Vertical)
        self.level = QtWidgets.QSpinBox()

        self.main_layout.addWidget(QtWidgets.QLabel('Gain'))
        self.main_layout.addWidget(self.gain)
        self.main_layout.addWidget(QtWidgets.QLabel('Level'))
        self.main_layout.addWidget(self.level)


class URP(QtWidgets.QWidget):

    def __init__(self):
        QtWidgets.QWidget.__init__(self)
        self.main_layout = QtWidgets.QGridLayout()
        self.setLayout(self.main_layout)

        self.preselector = Preselector()
        self.lo1 = LO(1)
        self.lo2 = LO(2, False)
        self.if1 = QtWidgets.QSpinBox()
        self.if1.setMinimumWidth(60)
        self.if1.setMaximum(100000)
        self.if2 = QtWidgets.QSpinBox()
        self.if2.setMinimumWidth(60)
        self.if2.setMaximum(100000)
        self.out = Out()

        # self.preselector.mode.mode_changed.connect()
        # self.preselector.preamplifier.gain.value_changed.connect()
        # self.preselector.bpf_block.gain.value_changed.connect()
        # self.lo1.freq.valueChanged.connect()
        # self.lo1.gain.value_changed.connect()
        # self.lo1.range.value_changed.connect()

        self.l_mixer1 = QtWidgets.QLabel()
        self.l_mixer2 = QtWidgets.QLabel()
        self.l_mixer1.setPixmap(QtGui.QPixmap('test.svg'))
        self.l_mixer2.setPixmap(QtGui.QPixmap('test.svg'))
        self.arrow = QtWidgets.QLabel()
        self.arrow.setPixmap(QtGui.QPixmap('arrow.svg'))

        self.main_layout.addWidget(self.preselector, 0, 0, 5, 12)
        self.main_layout.addWidget(self.l_mixer1, 0, 12, 6, 5)
        self.main_layout.addWidget(self.l_mixer2, 0, 17, 6, 5)

        self.main_layout.addWidget(QtWidgets.QLabel('IF1, MHz'), 0, 16)
        self.main_layout.addWidget(QtWidgets.QLabel('2500'), 1, 16, 2, 2)
        self.main_layout.addWidget(QtWidgets.QLabel('IF2, MHz'), 0, 21)
        self.main_layout.addWidget(QtWidgets.QLabel('2500'), 1, 21, 2, 2)

        self.main_layout.addWidget(self.out, 0, 22, 6, 3)

        self.main_layout.addWidget(self.lo1, 6, 12, 6, 5)
        self.main_layout.addWidget(self.lo2, 6, 17, 6, 5)



PreamplifierFilters = \
    {
        1: 'Off',
        2: 'Bypass',
        3: '<500 MHz',
        4: '500-1600 MHz',
        5: '1600-3000 MHz',
        6: 'WIFI 2.4 GHz',
        7: '>3000 MHz'
    }