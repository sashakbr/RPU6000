from PyQt5.QtSerialPort import QSerialPortInfo
from PyQt5.QtCore import pyqtSignal, pyqtSlot, Qt
from PyQt5.QtGui import QIcon, QColor, QFont
from PyQt5.QtWidgets import QWidget, QLabel, QComboBox, QPushButton, QTextEdit, \
    QHBoxLayout, QVBoxLayout, QSpacerItem, QGroupBox, QSizePolicy, \
    QApplication, QDialog, QDialogButtonBox, QCheckBox
import serial
from utility import *
from SP_settings import *
import connection_drivers
import queue
from datetime import datetime


def get_available_ports():
    ports = QSerialPortInfo.availablePorts()
    portsName = [p.portName() for p in ports]
    # discriptions = [p.description() for p in ports]
    # return dict(zip(portsName, discriptions))
    return portsName


class Widget(QWidget):
    signal = pyqtSignal(signal_type)
    signal_info = pyqtSignal(signal_info)

    def __init__(self):
        super().__init__()
        self.queue = queue.Queue()
        self.connection = connection_drivers.SerialTread(self.queue)
        self._create_widgets()
        self._set_widget_layouts()
        self._set_events()
        self._create_settings_widget()

        self.connection.closed_signal.connect(self.connection_is_closed)
        self.connection.opened_signal.connect(self.connection_is_open)
        self.connection.fail_signal.connect(self.connection_is_fail)
        self.connection.parcel_signal.connect(self.log_parcel)

    def _create_widgets(self):
        #self.setFixedWidth(370)
        self.setBaseSize(360, self.baseSize().height())
        self.setMinimumWidth(300)
        self.l_PortName = QLabel("Name")
        self.cb_PortName = QComboBox()
        self.cb_PortName.setFixedSize(80, 22)
        self.event_update_ports_name()

        self.update_port_name_btn = QPushButton()
        self.update_port_name_btn.setIcon(QIcon(r'icons/refresh.png'))
        self.update_port_name_btn.setFixedSize(26, 26)

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

        # кнопка дополнительных настроек COM порта
        self.pb_settings = QPushButton()
        self.pb_settings.setIcon(QIcon(r'icons/settings.svg'))
        self.pb_settings.setFixedSize(26, 26)
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

        layout1.addWidget(self.l_PortName)
        layout1.addWidget(self.update_port_name_btn)
        layout1.addWidget(self.cb_PortName)

        layout2.addWidget(self.l_BaudRate)
        layout2.addItem(QSpacerItem(0, 0, QSizePolicy.Expanding, QSizePolicy.Minimum))
        layout2.addWidget(self.pb_settings)
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
        self.update_port_name_btn.clicked.connect(self.event_update_ports_name)
        self.pb_settings.clicked.connect(self.event_settings)

    def _create_settings_widget(self):
        self.settings_ui = Ui_Dialog()
        self.settings_dialog = QDialog()
        self.settings_ui.setupUi(self.settings_dialog)
        self.settings_ui.cb_bytesize.addItem('8 BITS', serial.EIGHTBITS)
        self.settings_ui.cb_bytesize.addItem('7 BITS', serial.SEVENBITS)
        self.settings_ui.cb_bytesize.addItem('6 BITS', serial.SIXBITS)
        self.settings_ui.cb_bytesize.addItem('5 BITS', serial.FIVEBITS)

        self.settings_ui.cb_stopbits.addItem('1', serial.STOPBITS_ONE)
        self.settings_ui.cb_stopbits.addItem('2', serial.STOPBITS_TWO)
        self.settings_ui.cb_stopbits.addItem('1.5', serial.STOPBITS_ONE_POINT_FIVE)

        self.settings_ui.cb_parity.addItem('NONE', serial.PARITY_NONE)
        self.settings_ui.cb_parity.addItem('ODD', serial.PARITY_ODD)
        self.settings_ui.cb_parity.addItem('SPACE', serial.PARITY_SPACE)
        self.settings_ui.cb_parity.addItem('EVEN', serial.PARITY_EVEN)
        self.settings_ui.cb_parity.addItem('NAMES', serial.PARITY_NAMES)

        self.settings_ui.buttonBox.button(QDialogButtonBox.Ok).clicked.connect(self.set_connection_settings)
        self.settings_ui.buttonBox.button(QDialogButtonBox.Cancel).clicked.connect(self.settings_dialog.close)

    @pyqtSlot()
    def set_connection_settings(self):
        self.connection.set_timeout(self.settings_ui.dsb_timeout.value())
        self.connection.set_parity(self.settings_ui.cb_parity.currentData())
        self.connection.set_stopbits(self.settings_ui.cb_stopbits.currentData())
        self.connection.set_bytesize(self.settings_ui.cb_bytesize.currentData())
        self.settings_dialog.close()

    @pyqtSlot()
    def event_settings(self):
        self.settings_dialog.show()
        self.settings_dialog.exec()

    @pyqtSlot()
    def event_connect(self):
        if self.connection.is_open():
            self.queue.put(connection_drivers.event_('close_port', None))
        else:
            self.connection.set_baudrate(self.cb_BaudRate.currentData())
            self.set_connection_settings()
            self.connection.open(self.cb_PortName.currentText())

    @pyqtSlot()
    def event_update_ports_name(self):
        self.cb_PortName.clear()
        for i in get_available_ports():
            self.cb_PortName.addItem(i)

    def log_info(self, text, color):
        self.te_log.setTextColor(QColor(color))
        self.te_log.append(text)
        self.te_log.append("")

    @pyqtSlot(datetime)
    def connection_is_closed(self, time):
        str_time = (time.strftime('%H:%M:%S.%f')[:-3])
        self.log_info(f'{str_time}  Port {self.cb_PortName.currentText()} is closed!', color='darkGreen')
        self.signal_info.emit(signal_info(f'Port {self.cb_PortName.currentText()} is closed.', None))
        self.pb_connect.setText('Open')
        self.pb_con_state.setStyleSheet("background-color: grey")
        self.cb_BaudRate.setDisabled(False)
        self.cb_PortName.setDisabled(False)
        self.pb_settings.setDisabled(False)

    @pyqtSlot(datetime)
    def connection_is_open(self, time):
        str_time = (time.strftime('%H:%M:%S.%f')[:-3])
        self.log_info(f'{str_time}  Port {self.cb_PortName.currentText()} is open!', color='green')
        self.signal_info.emit(signal_info(f'Port {self.cb_PortName.currentText()} is opened.', None))
        self.pb_connect.setText('Close')
        self.pb_con_state.setStyleSheet("background-color: green")
        self.cb_BaudRate.setDisabled(True)
        self.cb_PortName.setDisabled(True)
        self.pb_settings.setDisabled(True)

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
            self.log_info('Serial port is not open!', 'red')

    def write(self, tx_data: bytes):
        if self.connection.is_open():
            #self.connection.write(tx_data)
            self.queue.put(connection_drivers.event_('write', tx_data))  # правильнее работать с очередью
        else:
            self.log_info('Serial port is not open!', 'red')

if __name__ == '__main__':
    import sys
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    window = SP2()
    window.show()
    sys.exit(app.exec_())