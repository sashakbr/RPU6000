from PyQt5.QtCore import pyqtSignal, pyqtSlot, Qt
from PyQt5.QtGui import QIcon, QColor, QFont
from PyQt5.QtWidgets import QWidget, QLabel, QComboBox, QPushButton, QTextEdit, \
    QHBoxLayout, QVBoxLayout, QSpacerItem, QGroupBox, QSizePolicy, QLineEdit,\
    QApplication, QDialog, QDialogButtonBox, QCheckBox
from utility import *
from SP_settings import *
import connection_drivers
import queue
from datetime import datetime
import ipaddress


class Widget(QWidget):
    signal = pyqtSignal(signal_type)
    signal_info = pyqtSignal(signal_info)

    def __init__(self):
        super().__init__()
        self.queue = queue.Queue()
        self.connection = connection_drivers.SocketTread(self.queue)
        self._create_widgets()
        self._set_widget_layouts()
        self._set_events()

        self.connection.closed_signal.connect(self.connection_is_closed)
        self.connection.opened_signal.connect(self.connection_is_open)
        self.connection.fail_signal.connect(self.connection_is_fail)
        self.connection.parcel_signal.connect(self.log_parcel)

    def _create_widgets(self):
        #self.setFixedWidth(370)
        self.setBaseSize(360, self.baseSize().height())
        self.setMinimumWidth(300)
        self.l_ip = QLabel("Server IP")
        self.le_ip = QLineEdit()
        self.le_ip.setText('192.168.1.234')
        self.le_ip.setFixedSize(120, 22)

        self.l_port = QLabel('Server Port')
        self.le_port = QLineEdit()
        self.le_port.setText('20020')
        self.le_port.setFixedSize(120, 22)

        self.con_type = QComboBox()
        self.con_type.addItems(('UDP', 'TCP'))

        self.pb_connect = QPushButton("Open")
        self.pb_connect.setFixedSize(120, 30)

        # индикатор подключения
        self.pb_con_state = QPushButton()
        self.pb_con_state.setFixedSize(26, 26)
        self.pb_con_state.setStyleSheet("background-color: grey")
        # история отправленных  и принятых команд команд
        self.te_log = QTextEdit()
        self.te_log.setReadOnly(True)
        self.te_log.setFont(QFont('Consolas', 9))
        # кнопка очистки лога
        self.clear_btn = QPushButton('Clear')
        self.clear_btn.setIcon(QIcon(r'icons/trash.svg'))
        # галочка включения парсинга принятой команды согласно команд в дереве
        self.cb_parsing = QCheckBox('Parsing')
        self.cb_parsing.setFixedSize(60, 15)
        self.cb_parsing.setDisabled(True)

    def _set_widget_layouts(self):
        self.sp_layout = QVBoxLayout()
        self.setLayout(self.sp_layout)

        layout1 = QHBoxLayout()
        layout2 = QHBoxLayout()
        layout3 = QHBoxLayout()

        layout1.addWidget(self.l_ip)
        layout1.addWidget(self.le_ip)

        layout2.addWidget(self.l_port)
        layout2.addItem(QSpacerItem(0, 0, QSizePolicy.Expanding, QSizePolicy.Minimum))
        layout2.addWidget(self.le_port)

        layout3.addWidget(self.con_type)
        layout3.addItem(QSpacerItem(0, 0, QSizePolicy.Expanding, QSizePolicy.Minimum))
        layout3.addWidget(self.pb_con_state)
        layout3.addWidget(self.pb_connect)

        sp_group = QGroupBox('Ethernet Client')
        group_layout = QVBoxLayout()
        sp_group.setLayout(group_layout)
        self.sp_layout.addWidget(sp_group)
        group_layout.addLayout(layout1)
        group_layout.addLayout(layout2)
        group_layout.addLayout(layout3)

        self.sp_layout.addWidget(QLabel("Command log"))
        self.sp_layout.addWidget(self.te_log)
        layout4 = QHBoxLayout()
        self.sp_layout.addLayout(layout4)
        layout4.addWidget(self.cb_parsing)
        layout4.addStretch(1)
        layout4.addWidget(self.clear_btn)

    def _set_events(self):
        self.pb_connect.clicked.connect(self.event_connect)
        self.clear_btn.clicked.connect(lambda: self.te_log.clear())


    @pyqtSlot()
    def event_connect(self):
        if self.connection.is_open():
            self.queue.put(connection_drivers.event_('close_port', None))
        else:
            ip_address = self.le_ip.text()
            #   validate IP address
            try:
                ipaddress.ip_address(ip_address)
                self.connection.open(ip_address, int(self.le_port.text()), self.con_type.currentText())
            except ValueError:
                self.log_info(f'IP address {ip_address} is not valid', 'red')

    def log_info(self, text, color):
        self.te_log.setTextColor(QColor(color))
        self.te_log.append(text)
        self.te_log.append("")

    @pyqtSlot(datetime)
    def connection_is_closed(self, time):
        str_time = (time.strftime('%H:%M:%S.%f')[:-3])
        text = f'Connection ({self.le_ip.text()}, {self.le_port.text()}) is closed.'
        self.log_info(text, color='darkGreen')
        self.signal_info.emit(signal_info(text, None))
        self.pb_connect.setText('Open')
        self.pb_con_state.setStyleSheet("background-color: grey")
        self.le_port.setDisabled(False)
        self.le_ip.setDisabled(False)
        self.con_type.setDisabled(False)

    @pyqtSlot(datetime)
    def connection_is_open(self, time):
        str_time = (time.strftime('%H:%M:%S.%f')[:-3])
        text = f'Connection ({self.le_ip.text()}, {self.le_port.text()}) is open.'
        self.log_info(text, color='green')
        self.signal_info.emit(signal_info(text, None))
        self.pb_connect.setText('Close')
        self.pb_con_state.setStyleSheet("background-color: green")
        self.le_port.setDisabled(True)
        self.le_ip.setDisabled(True)
        self.con_type.setDisabled(True)

    @pyqtSlot(connection_drivers.fail)
    def connection_is_fail(self, fail: connection_drivers.fail):
        str_time = (fail.time.strftime('%H:%M:%S.%f')[:-3])
        self.log_info(f'{str_time}  {fail.text}', color='red')

    @pyqtSlot(connection_drivers.parcel)
    def log_parcel(self, parcel: connection_drivers.parcel):
        str_time = (parcel.time.strftime('%H:%M:%S.%f')[:-3])

        if parcel.type == 'TX':
            self.te_log.setTextColor(QColor('blue'))
            self.te_log.append(f'{str_time}  TX --> hex: {bytes_to_hex_string(parcel.data)}')
        elif parcel.type == 'RX':
            self.signal.emit(signal_type('read data', parcel.data))
            self.te_log.setTextColor(QColor('magenta'))
            self.te_log.append(f'{str_time}  RX <-- hex: {bytes_to_hex_string(parcel.data)}')

    def write_read(self, tx_data: bytes):
        if self.connection.is_open():
            return self.connection.write_read(tx_data)
        else:
            self.log_info('Connection is not open!', 'red')

    def write(self, tx_data: bytes):
        if self.connection.is_open():
            #self.connection.write(tx_data)
            self.queue.put(connection_drivers.event_('write', tx_data))  # правильнее работать с очередью
        else:
            self.log_info('Connection is not open!', 'red')

if __name__ == '__main__':
    import sys
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    window = SP2()
    window.show()
    sys.exit(app.exec_())