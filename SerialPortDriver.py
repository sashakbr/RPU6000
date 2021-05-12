from PyQt5.QtSerialPort import QSerialPortInfo
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtGui import QIcon, QColor, QFont
from PyQt5.QtWidgets import QWidget, QLabel, QComboBox, QPushButton, QTextEdit,\
                            QHBoxLayout, QVBoxLayout, QSpacerItem, QGroupBox, QSizePolicy
import serial
from service import *


def get_available_ports():
    ports = QSerialPortInfo.availablePorts()
    portsName = [p.portName() for p in ports]
    # discriptions = [p.description() for p in ports]
    # return dict(zip(portsName, discriptions))
    return portsName


class SP(QWidget):
    signal = pyqtSignal(signal_type)

    def __init__(self):
        super().__init__()
        self.connection = serial.Serial(parity=serial.PARITY_NONE,
                                        stopbits=serial.STOPBITS_ONE,
                                        bytesize=serial.EIGHTBITS,
                                        timeout=2,
                                        xonxoff=False,
                                        write_timeout=2)
        self.__create_widgets()
        self.__set_appearance_widget()
        self.__set_events()

    def __create_widgets(self):
        self.setFixedWidth(370)
        self.l_PortName = QLabel("Name")
        self.cb_PortName = QComboBox()
        self.cb_PortName.setFixedSize(80, 22)
        self.event_update_ports_name()

        self.update_port_name_btn = QPushButton()
        self.update_port_name_btn.setIcon(QIcon('icons\\refresh.png'))
        self.update_port_name_btn.setFixedSize(22, 22)

        self.l_BaudRate = QLabel('Baudrate')
        self.cb_BaudRate = QComboBox()
        self.cb_BaudRate.setFixedSize(80, 22)
        self.cb_BaudRate.addItem('115200', 115200)
        self.cb_BaudRate.addItem('57600', 57600)
        self.cb_BaudRate.addItem('38400', 38400)
        self.cb_BaudRate.addItem('19200', 19200)
        self.cb_BaudRate.addItem('9600', 9600)
        self.cb_BaudRate.addItem('4800', 4800)
        self.cb_BaudRate.addItem('2400', 2400)
        self.cb_BaudRate.addItem('1200', 1200)

        self.pb_connect = QPushButton("Open")
        self.pb_connect.setFixedSize(80, 30)
        # индикатор подключения
        self.pb_con_state = QPushButton()
        self.pb_con_state.setFixedSize(22, 22)
        self.pb_con_state.setStyleSheet("background-color: grey")
        # история отправленных  и принятых команд команд
        self.te_log = QTextEdit()
        self.te_log.setReadOnly(True)
        self.te_log.setFont(QFont('Courier New', 9))
        # кнопка очистки лога
        self.clear_btn = QPushButton('Clear')
        self.clear_btn.setIcon(QIcon('icons\\trash.svg'))



    def __set_events(self):
        self.pb_connect.clicked.connect(self.event_connect)
        self.clear_btn.clicked.connect(lambda: self.te_log.clear())
        self.update_port_name_btn.clicked.connect(self.event_update_ports_name)

    def __set_appearance_widget(self):
        self.sp_layout = QVBoxLayout()
        self.setLayout(self.sp_layout)

        layout1 = QHBoxLayout()
        layout2 = QHBoxLayout()
        layout3 = QHBoxLayout()

        layout1.addWidget(self.l_PortName)
        layout1.addWidget(self.update_port_name_btn)
        layout1.addWidget(self.cb_PortName)

        layout2.addWidget(self.l_BaudRate)
        layout2.addWidget(self.cb_BaudRate)

        layout3.addItem(QSpacerItem(0, 0, QSizePolicy.Expanding, QSizePolicy.Minimum))
        layout3.addWidget(self.pb_con_state)
        layout3.addWidget(self.pb_connect)

        sp_group = QGroupBox('Serial Port')
        group_layout = QVBoxLayout()
        sp_group.setLayout(group_layout)
        self.sp_layout.addWidget(sp_group)
        group_layout.addLayout(layout1)
        group_layout.addLayout(layout2)
        group_layout.addLayout(layout3)

        self.sp_layout.addWidget(QLabel("History"))
        self.sp_layout.addWidget(self.te_log)
        self.sp_layout.addWidget(self.clear_btn)

    def event_connect(self):
        portName = self.cb_PortName.currentText()
        if self.connection.isOpen():
            self.close_port()
            self.signal.emit(signal_type('sp state', 'closed'))
            self.pb_con_state.setStyleSheet("background-color: grey")
            self.pb_connect.setText('Open')
            self.cb_BaudRate.setDisabled(False)
            self.cb_PortName.setDisabled(False)
            self.log_info(f'Serial port {portName} is close!', 'orange')
        else:
            state = self.open_port(portName)
            if state:
                self.signal.emit(signal_type('sp state', 'opened'))
                self.pb_con_state.setStyleSheet("background-color: green")
                self.pb_connect.setText('Close')
                self.cb_BaudRate.setDisabled(True)
                self.cb_PortName.setDisabled(True)
                self.log_info(f'Serial port {portName} is open!', 'green')
            else:
                self.signal.emit(signal_type('sp state', 'opening failed'))
                self.pb_con_state.setStyleSheet("background-color: grey")
                self.pb_connect.setText('Open')
                self.cb_BaudRate.setDisabled(False)
                self.cb_PortName.setDisabled(False)
                self.log_info(f'Serial port {portName} opening failed!', 'red')

    def event_update_ports_name(self):
        self.cb_PortName.clear()
        for i in get_available_ports():
            self.cb_PortName.addItem(i)

    def log_info(self, text, color):
        self.te_log.setTextColor(QColor(color))
        self.te_log.append(text)
        self.te_log.append("")

    def log_cmd(self, tx, rx):
        self.te_log.setTextColor(QColor('blue'))
        tx_str = bytes_to_hex_string(tx)
        rx_str = bytes_to_hex_string(rx)
        self.te_log.append(f'TX--> hex: {tx_str}')
        self.te_log.append(f'RX--> hex: {rx_str}')
        self.te_log.append('')

    #******************************************************
    def open_port(self, port_name):
        if not self.connection.isOpen():
            try:
                self.connection.setPort(port_name)
                self.connection.open()
                return True
            except Exception:
                self.log_info("Could not open port " + port_name, 'red')
                return False
        else:
            return True

    def close_port(self):
        if self.connection.isOpen():
            self.connection.close()

    def write(self, data):
        self.connection.write(data)

    def read(self, len_data):
        return self.connection.read(len_data)

    def read_line(self):
        return self.connection.readline()

    def write_read(self, tx_data: bytes, rx_data_len):
        if self.connection.isOpen():
            self.connection.write(tx_data)
            rx_data = self.connection.read(rx_data_len)
            self.log_cmd(tx_data, rx_data)
            return rx_data
        else:
            self.log_info('Serial port is not open!', 'red')
