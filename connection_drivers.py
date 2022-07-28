from PyQt5 import QtCore, QtWidgets
from collections import namedtuple
import queue
import serial
import socket
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


class SocketTread(QtCore.QThread):
    opened_signal = QtCore.pyqtSignal(datetime)
    closed_signal = QtCore.pyqtSignal(datetime)
    fail_signal = QtCore.pyqtSignal(fail)

    parcel_signal = QtCore.pyqtSignal(parcel)

    def __init__(self, queue: queue.Queue):
        QtCore.QThread.__init__(self)
        self.queue = queue
        self.tread_timeout = 20  # in ms
        self.socket_timeout = 0.005     # in s
        self.socket = None
        self.server_ip = None
        self.server_port = None
        self.socket_type = None
        self.count = 0

    def open(self, server_ip: str, server_port: int, protocol_type: str):
        """
        :param server_ip: ip address in str
        :param server_port: port in int
        :param protocol_type: 'UDP' or 'TCP', default UDP
        :return:
        """

        self.server_ip = server_ip
        self.server_port = server_port

        try:
            if protocol_type == 'tcp' or protocol_type == 'TCP':
                self.socket_type = socket.SOCK_STREAM
                self.socket = socket.socket(socket.AF_INET, self.socket_type)
                self.socket.connect((server_ip, server_port))
            else:
                 self.socket_type = socket.SOCK_DGRAM  # UDP
                 self.socket = socket.socket(socket.AF_INET, self.socket_type)
            self.socket.settimeout(self.socket_timeout)
            self.opened_signal.emit(datetime.now())
            self.start()
        except Exception as e:
            self.socket = None
            self.fail_signal.emit(fail(datetime.now(), str(e)))

    def is_open(self) -> bool:
        if self.socket is not None:
            return True
        else:
            return False

    def close(self):
        try:
            self.socket.close()
            self.socket = None
            self.server_ip = None
            self.server_port = None
            self.socket_type = None

        except Exception as e:
            self.fail_signal.emit(fail(datetime.now(), str(e)))

    def write_read(self, tx_data: bytes):
        self.socket.sendto(tx_data, (self.server_ip, self.server_port))
        self.parcel_signal.emit(parcel(type='TX',
                                       time=datetime.now(),
                                       data=tx_data))
        rx_data = self.socket.recv(len(tx_data))
        self.parcel_signal.emit(parcel(type='RX',
                                       time=datetime.now(),
                                       data=rx_data))
        return rx_data

    def write(self, tx_data: bytes):
        try:
            #self.socket.sendall(tx_data)
            self.socket.sendto(tx_data, (self.server_ip, self.server_port))
            self.parcel_signal.emit(parcel(type='TX',
                                           time=datetime.now(),
                                           data=tx_data))
        except Exception as e:
            self.fail_signal.emit(fail(datetime.now(), str(e)))


    def event_handler(self, e: event_):
        if e.type == 'close_port':
            self.close()
        elif e.type == 'write_read':
            self.write_read(e.data)
        elif e.type == 'write':
            self.write(e.data)

    def run(self):
        while self.is_open():
            while not self.queue.empty():
                self.event_handler(self.queue.get())
            try:
                data = self.socket.recv(1024)
                self.parcel_signal.emit(parcel(type='RX',
                                               time=datetime.now(),
                                               data=data))
            except socket.timeout:
                self.msleep(self.tread_timeout)
            except AttributeError:
                self.closed_signal.emit(datetime.now())
                return
        self.closed_signal.emit(datetime.now())
