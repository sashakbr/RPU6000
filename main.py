import sys
from PyQt5.QtWidgets import (QApplication, QMainWindow, QComboBox, QLabel, QTextEdit, QDockWidget,
                             QListWidget, QGridLayout, QHBoxLayout, QVBoxLayout, QWidget, QPushButton,
                             QSpinBox, QCheckBox, QSlider, QGroupBox, QSpacerItem, QSizePolicy, QMenu, QLCDNumber,
                             QTreeWidget, QTreeWidgetItem, QTreeView)
from PyQt5.QtCore import Qt, pyqtSignal, QIODevice
import time
from PyQt5.QtGui import QStandardItemModel, QStandardItem

from PyQt5.QtGui import QPalette, QIcon, QColor

import SerialPortDriver
from collections import namedtuple

signal_type = namedtuple('Signal', ['name', 'value'])

comands = {
    'Channel 1 power':
        {
            'comand num': '5',
            'state': ['0', '1']
        },
    'Channel 2 power':
        {
            'comand num': '6',
            'state': ['0', '1']
        },
    'Set filter':
        {
            'comand num': '4',
            'Low': ['BP1(0x01)', 'BP2(0x02)'],
            'Hight': ['BP1(0x01)', 'BP2(0x02)', 'BP3(0x03)', 'BP4(0x04)']
        }
}


class SP(QWidget):
    signal = pyqtSignal(signal_type)

    def __init__(self):
        super().__init__()
        self.sp = SerialPortDriver.SP()
        self.setFixedWidth(250)
        self.__create_widgets()
        self.__create_events()
        self.set_vertical_layout()

    def __create_widgets(self):
        self.l_PortName = QLabel("Port")
        self.cb_PortName = QComboBox()
        for i in self.sp.get_available_ports():
            self.cb_PortName.addItem(i)

        self.l_BaudRate = QLabel('Baudrate')
        self.cb_BaudRate = QComboBox()
        self.cb_BaudRate.addItem('115200', 115200)
        self.cb_BaudRate.addItem('9600', 9600)
        self.cb_BaudRate.addItem('4800', 4800)

        self.pb_connect = QPushButton("Open")
        # индикатор подключения
        self.pb_con_state = QPushButton()
        self.pb_con_state.setIcon(QIcon('refresh.png'))
        self.pb_con_state.setFixedSize(20, 20)
        # история отправленных  и принятых команд команд
        self.te_log = QTextEdit()

    def __create_events(self):
        self.pb_connect.clicked.connect(self.connection_event)

    def set_vertical_layout(self):
        self.sp_layout = QVBoxLayout()
        self.setLayout(self.sp_layout)
        layout1 = QHBoxLayout()
        layout2 = QHBoxLayout()
        layout3 = QHBoxLayout()
        layout1.addWidget(self.l_PortName)
        layout1.addWidget(self.cb_PortName)
        layout2.addWidget(self.l_BaudRate)
        layout2.addWidget(self.cb_BaudRate)
        layout3.addWidget(self.pb_con_state)
        layout3.addWidget(self.pb_connect)
        self.sp_layout.addLayout(layout1)
        self.sp_layout.addLayout(layout2)
        self.sp_layout.addLayout(layout3)
        self.sp_layout.addWidget(QLabel("History"))
        self.sp_layout.addWidget(self.te_log)

    def set_horizontal_layout(self):
        self.sp_layout = QHBoxLayout()
        self.setLayout(self.sp_layout)
        self.sp_layout.addWidget(self.pb_con_state)
        self.sp_layout.addWidget(self.l_PortName)
        self.sp_layout.addWidget(self.cb_PortName)
        self.sp_layout.addWidget(self.l_BaudRate)
        self.sp_layout.addWidget(self.cb_BaudRate)
        self.sp_layout.addWidget(self.pb_connect)

    def connection_event(self):
        portName = self.cb_PortName.currentText()
        if self.sp.is_open():
            self.sp.close_port()
            self.signal.emit(signal_type('sp state', 'closed'))
            self.pb_con_state.setStyleSheet("background-color: grey")
            self.pb_connect.setText('Open')
            self.log_info(f'Serial port {portName} is close!', 'orange')
        else:
            state = self.sp.open_port(portName)
            if state:
                self.signal.emit(signal_type('sp state', 'opened'))
                self.pb_con_state.setStyleSheet("background-color: green")
                self.pb_connect.setText('Close')
                self.log_info(f'Serial port {portName} is open!', 'green')
            else:
                self.signal.emit(signal_type('sp state', 'opening failed'))
                self.pb_con_state.setStyleSheet("background-color: grey")
                self.pb_connect.setText('Open')
                self.log_info(f'Serial port {portName} opening failed!', 'red')

    def log_info(self, text, color):
        self.te_log.setTextColor(QColor(color))
        self.te_log.append(text)
        self.te_log.append("")

    def log_cmd(self, tx, rx):
        self.te_log.setTextColor(QColor('blue'))
        self.te_log.append(f'TX--> {tx}')
        self.te_log.append(f'RX--> {rx}')
        self.te_log.append('')

    def write_read(self, tx_data: bytes, rx_data_len):
        if self.sp.write(tx_data):
            rx_data = self.sp.read(rx_data_len)
            self.log_cmd(tx_data, rx_data)
            return rx_data


class UrpControl(QWidget):
    signal = pyqtSignal(signal_type)

    def __init__(self):
        super().__init__()
        self.__create_widgets()
        self.set_layout()

    def __create_widgets(self):
        self.l_band = QLabel('Band')
        self.sp_band = QSpinBox()

    def set_layout(self):
        self.main_layout = QVBoxLayout()
        self.setLayout(self.main_layout)
        self.main_layout.addWidget(self.l_band)
        self.main_layout.addWidget(self.sp_band)


class CustomCmd(QWidget):
    def __init__(self):
        super().__init__()
        self.__create_widgets()

    def __create_widgets(self):
        self.cmdtree = QTreeView()
        self.main_layout = QVBoxLayout()
        self.setLayout(self.main_layout)
        self.main_layout.addWidget(self.cmdtree)
        self.model = QStandardItemModel()
        self.cmdtree.setModel(self.model)
        self.model.setHorizontalHeaderLabels(['Names', 'Value'])
        for cmd_name, cmd in comands.items():
            btn_send = QPushButton('Send')
            btn_send.setStyleSheet('background-color: grey;'
                                   'border-style: outset;'
                                   'order-width: 2px;'
                                   'border-radius: 7px;'
                                   'border-color: beige;'
                                   'font: bold 12px;'
                                   'color: white;'
                                   'padding: 4px;')
            list_name = QStandardItem(cmd_name)
            send_itm = QStandardItem()

            for bit_name, bit_value in cmd.items():
                col1 = QStandardItem(bit_name)
                if type(bit_value) == list:
                    col2 = QStandardItem()
                    list_name.appendRow([col1, col2])
                    combo = QComboBox()
                    combo.addItems(bit_value)
                    cb_index = self.model.indexFromItem(col2)
                    self.cmdtree.setIndexWidget(cb_index, combo)
                else:
                    col2 = QStandardItem(bit_value)
                    list_name.appendRow([col1, col2])

            self.model.appendRow([list_name, send_itm])
            btn_index = self.model.indexFromItem(send_itm)
            btn_send.clicked.connect(lambda: print(btn_index.internalId()))
            self.cmdtree.setIndexWidget(btn_index, btn_send)
            self.model.


class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()
        self.resize(600, 800)
        self.view_menu = self.menuBar().addMenu("&View")
        self.create_sp_docker()
        self.create_urp_docker()
        self.create_cmd_docker()
        self.sp.signal.connect(self.sp_signal_handling, Qt.QueuedConnection)
        self.urp.sp_band.valueChanged.connect(self.set_band)

    def set_band(self):
        band = self.urp.sp_band.value()
        self.sp.write_read(tx_data=bytes([0, 5, band]), rx_data_len=3)

    def create_urp_docker(self):
        self.urp = UrpControl()
        self.docker_urp = QDockWidget('URP', self)
        self.docker_urp.setWidget(self.urp)
        self.addDockWidget(Qt.RightDockWidgetArea, self.docker_urp)
        self.view_menu.addAction(self.docker_urp.toggleViewAction())

    def create_sp_docker(self):
        self.sp = SP()
        self.doker_sp = QDockWidget('Serial port', self)
        self.doker_sp.setWidget(self.sp)
        self.addDockWidget(Qt.LeftDockWidgetArea, self.doker_sp)
        self.view_menu.addAction(self.doker_sp.toggleViewAction())

    def create_cmd_docker(self):
        self.cmd = CustomCmd()
        self.doker_cmd = QDockWidget('Comand', self)
        self.doker_cmd.setWidget(self.cmd)
        self.addDockWidget(Qt.BottomDockWidgetArea, self.doker_cmd)
        self.view_menu.addAction(self.doker_cmd.toggleViewAction())

    def sp_signal_handling(self, signal):
        print(signal.name, signal.value)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
