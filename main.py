import sys
from PyQt5.QtWidgets import (QApplication, QMainWindow, QComboBox, QLabel, QTextEdit, QDockWidget,
                             QListWidget, QGridLayout, QHBoxLayout, QVBoxLayout, QWidget, QPushButton,
                             QSpinBox, QCheckBox, QSlider, QGroupBox, QSpacerItem, QSizePolicy, QMenu, QLCDNumber,
                             QTreeWidget, QTreeWidgetItem, QTreeView, QFileDialog, QStyleOptionDockWidget)
from PyQt5.QtCore import Qt, pyqtSignal, QSignalMapper
import time
from PyQt5.QtGui import QStandardItemModel, QStandardItem

from PyQt5.QtGui import QPalette, QIcon, QColor

import SerialPortDriver
from collections import namedtuple
import json

signal_type = namedtuple('Signal', ['name', 'value'])


def int_to_bytes(number: int):
    """
    Перевод целых чисел в набор байт для случаев, когда число больше 255 (больше uint_8)
    :param number: int
    :return: bytes
    """
    return number.to_bytes(length=(8 + (number + (number < 0)).bit_length()) // 8,
                           byteorder='little',
                           signed=False)


def bytes_to_hex_string(data: bytes):
    res = ''
    for i, j in zip(data.hex()[::2], data.hex()[1::2]):
        res += i + j + ' '
    return res


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
        self.l_PortName = QLabel("Name")
        self.cb_PortName = QComboBox()
        self.cb_PortName.setFixedSize(80, 22)
        self.update_port_name_event()

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
        # история отправленных  и принятых команд команд
        self.te_log = QTextEdit()
        self.te_log.setReadOnly(True)
        # кнопка очистки лога
        self.clear_btn = QPushButton('Clear')

    def __create_events(self):
        self.pb_connect.clicked.connect(self.connection_event)
        self.clear_btn.clicked.connect(lambda: self.te_log.clear())
        self.update_port_name_btn.clicked.connect(self.update_port_name_event)

    def set_vertical_layout(self):
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

    def update_port_name_event(self):
        self.cb_PortName.clear()
        for i in self.sp.get_available_ports():
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

    def write_read(self, tx_data: bytes, rx_data_len):
        if self.sp.is_open():
            self.sp.write(tx_data)
            rx_data = self.sp.read(rx_data_len)
            self.log_cmd(tx_data, rx_data)
            return rx_data
        else:
            self.log_info('Serial port is not open!', 'red')


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
    signal = pyqtSignal(signal_type)

    def __init__(self):
        super().__init__()
        self.__create_widgets()
        self.setMinimumWidth(550)

    def __create_widgets(self):
        self.main_layout = QVBoxLayout()
        self.setLayout(self.main_layout)

        self.cmdtree = QTreeView()
        self.model = QStandardItemModel()
        self.cmdtree.setModel(self.model)
        self.mapper = QSignalMapper()

        file_group = QGroupBox('Command file')
        self.file_path_lable = QLabel('Path: ')
        self.file_dialog_btn = QPushButton('Open')
        self.file_dialog_btn.setFixedSize(80, 40)
        self.file_dialog_btn.clicked.connect(self.open_file_dialog)
        file_layout = QHBoxLayout()
        file_layout.addWidget(self.file_path_lable)
        file_layout.addWidget(self.file_dialog_btn)
        file_group.setLayout(file_layout)

        prefix_group = QGroupBox('Prefix')
        self.prefix_check = QCheckBox('Off')
        self.prefix_check.clicked.connect(self.prefix_check_clicked)
        self.prefix_value = QSpinBox()
        self.prefix_value.setEnabled(False)
        prefix_layout = QHBoxLayout()
        prefix_layout.addWidget(self.prefix_check)
        prefix_layout.addWidget(self.prefix_value)
        prefix_group.setLayout(prefix_layout)
        prefix_layout.addItem(QSpacerItem(50, 0, QSizePolicy.Minimum, QSizePolicy.Minimum))

        self.main_layout.addWidget(file_group)
        self.main_layout.addWidget(self.cmdtree)
        self.main_layout.addWidget(prefix_group)

    def fill_tree(self, commands):
        self.model.clear()
        i = 0
        for cmd_name, cmd in commands.items():

            cmd_name_item = QStandardItem(cmd_name)
            space = QStandardItem()
            send_btn_item = QStandardItem()
            self.model.appendRow([cmd_name_item, space, send_btn_item])

            btn_send = QPushButton('Send')
            self.mapper.setMapping(btn_send, i)
            i += 1
            btn_send.clicked.connect(self.mapper.map)
            btn_send.setStyleSheet('background-color: grey;'
                                   'border-style: outset;'
                                   'order-width: 2px;'
                                   'border-radius: 7px;'
                                   'border-color: beige;'
                                   'font: bold 12px;'
                                   'color: white;'
                                   'padding: 4px;')

            btn_index = self.model.indexFromItem(send_btn_item)
            self.cmdtree.setIndexWidget(btn_index, btn_send)

            for bit_name, bit_value in cmd.items():
                byte_name_item = QStandardItem(bit_name)
                byte_value_item = QStandardItem()
                cmd_name_item.appendRow([byte_name_item, byte_value_item])
                cb_index = self.model.indexFromItem(byte_value_item)
                if type(bit_value) == dict:
                    combo = QComboBox()
                    for text_, data_ in bit_value.items():
                        combo.addItem(text_, data_)
                    self.cmdtree.setIndexWidget(cb_index, combo)
                elif type(bit_value) == int:
                    spin = QSpinBox()
                    spin.setValue(bit_value)
                    self.cmdtree.setIndexWidget(cb_index, spin)

        self.mapper.mapped[int].connect(self.btn_press)
        self.model.setHorizontalHeaderLabels(['Names', 'Values', 'Send buttons'])
        self.cmdtree.setColumnWidth(0, 200)
        self.cmdtree.setColumnWidth(1, 200)

    def btn_press(self, row_num):
        item = self.model.item(row_num, 0)
        if item.hasChildren():
            command = []
            for i in range(item.rowCount()):
                child_item = item.child(i, 1)
                #print(item.child(i, 0).text())
                index_ = self.model.indexFromItem(child_item)
                widget_ = self.cmdtree.indexWidget(index_)
                if type(widget_) == QComboBox:
                    command.append(widget_.currentData())
                elif type(widget_) == QSpinBox:
                    command.append(widget_.value())
            if self.prefix_check.isChecked():
                command.insert(0, self.prefix_value.value())
            bytes_command = b''
            for _ in command:
                bytes_command += int_to_bytes(_)
            self.signal.emit(signal_type('send_cmd', bytes_command))

    def open_file_dialog(self):
        dir_ = QFileDialog.getOpenFileName(None, 'Open File', '', 'CMD file (*.txt, *.json)')
        if dir_[0] != '':
            file_path = dir_[0]
            self.file_path_lable.setText('Path: ' + file_path)
            with open(file_path) as f:
                data = json.load(f)
            self.fill_tree(data)
        print(dir_)

    def prefix_check_clicked(self):
        if self.prefix_check.isChecked():
            self.prefix_check.setText("On")
            self.prefix_value.setEnabled(True)
        else:
            self.prefix_check.setText('Off')
            self.prefix_value.setEnabled(False)


class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()
        self.resize(800, 600)
        self.view_menu = self.menuBar().addMenu("&View")
        self.create_sp()
        self.create_urp_docker()
        self.create_cmd_docker()
        self.sp.signal.connect(self.sp_signal_handling, Qt.QueuedConnection)
        self.cmd.signal.connect(self.cmd_signal_handling, Qt.QueuedConnection)
        self.urp.sp_band.valueChanged.connect(self.set_band)

    def set_band(self):
        band = self.urp.sp_band.value()
        self.sp.write_read(tx_data=bytes([0, 5, band]), rx_data_len=3)

    def create_urp_docker(self):
        self.urp = UrpControl()
        self.docker_urp = QDockWidget('URP', self)
        self.docker_urp.setWidget(self.urp)
        self.addDockWidget(Qt.BottomDockWidgetArea, self.docker_urp)
        self.view_menu.addAction(self.docker_urp.toggleViewAction())

    def create_sp(self):
        self.sp = SP()
        self.setCentralWidget(self.sp)

    def create_cmd_docker(self):
        self.cmd = CustomCmd()
        self.doker_cmd = QDockWidget('Comand', self)
        self.doker_cmd.setWidget(self.cmd)
        self.addDockWidget(Qt.RightDockWidgetArea, self.doker_cmd)
        self.view_menu.addAction(self.doker_cmd.toggleViewAction())

    def sp_signal_handling(self, signal):
        print(signal.name, signal.value)
        if signal.name == 'cmd':
            print(self.cmd.cmdtree.currentIndex().row())

    def cmd_signal_handling(self, signal):
        if signal.name == 'send_cmd':
            self.sp.write_read(signal.value, len(signal.value))


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
