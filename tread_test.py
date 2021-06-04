from PyQt5 import QtCore, QtWidgets
from collections import namedtuple
import queue
import serial
from datetime import datetime


PARITY_NONE, PARITY_EVEN, PARITY_ODD, PARITY_MARK, PARITY_SPACE = 'N', 'E', 'O', 'M', 'S'
STOPBITS_ONE, STOPBITS_ONE_POINT_FIVE, STOPBITS_TWO = (1, 1.5, 2)
FIVEBITS, SIXBITS, SEVENBITS, EIGHTBITS = (5, 6, 7, 8)

parcel = namedtuple('parcel', ['type', 'time', 'data'])
event_ = namedtuple('event', ['type', 'data'])
fail = namedtuple('fail', ['time', 'text'])


class SerialTread(QtCore.QThread):
    opened_signal = QtCore.pyqtSignal(datetime)
    closed_signal = QtCore.pyqtSignal(datetime)
    fail_signal = QtCore.pyqtSignal(fail)

    parcel_signal = QtCore.pyqtSignal(parcel)

    def __init__(self, queue: queue.Queue):
        QtCore.QThread.__init__(self)
        self.queue = queue
        self.tread_timeout = 20  # in ms
        self.serial = serial.Serial()
        self.count = 0

    def open(self, port_name: str):
        self.serial.setPort(port_name)
        try:
            self.serial.open()
            self.opened_signal.emit(datetime.now())
            self.start()
        except Exception as e:
            self.fail_signal.emit(fail(datetime.now(), str(e)))

    def close(self):
        try:
            self.serial.close()
        except Exception as e:
            self.fail_signal.emit(datetime.now(), str(e))
        
    def is_open(self):
        return self.serial.isOpen()

    def set_baudrate(self, value):
        self.serial.baudrate = value

    def set_timeout(self, value):
        self.serial.timeout = value

    def set_parity(self, value):
        self.serial.parity = value

    def set_stopbits(self, value):
        self.serial.stopbits = value

    def set_bytesize(self, value):
        self.serial.bytesize =value

    def write_read(self, tx_data: bytes):
        self.serial.write(tx_data)
        self.parcel_signal.emit(parcel(type='TX',
                                       time=datetime.now(),
                                       data=tx_data))
        rx_data = self.serial.read(len(tx_data))
        self.parcel_signal.emit(parcel(type='RX',
                                       time=datetime.now(),
                                       data=rx_data))
        return rx_data

    def write(self, tx_data: bytes):
        self.serial.write(tx_data)
        self.parcel_signal.emit(parcel(type='TX',
                                       time=datetime.now(),
                                       data=tx_data))

    def event_handler(self, e: event_):
        if e.type == 'close_port':
            self.close()
        elif e.type == 'write_read':
            self.write_read(e.data)
        elif e.type == 'write':
            self.write(e.data)


    def run(self):
        while self.serial.isOpen():
            while not self.queue.empty():
                self.event_handler(self.queue.get())
            if self.serial.isOpen() and self.serial.inWaiting():
                print(self.serial.inWaiting())
                self.parcel_signal.emit(parcel(type='RX',
                                               time=datetime.now(),
                                               data=self.serial.read(self.serial.inWaiting())))
            else:
                self.msleep(self.tread_timeout)
        self.closed_signal.emit(datetime.now())
