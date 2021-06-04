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
from service import *
import json


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

            for byte_name, byte_description in cmd.items():
                byte_name_item = QStandardItem(byte_name)
                byte_value_item = QStandardItem()
                cmd_name_item.appendRow([byte_name_item, byte_value_item])
                cb_index = self.model.indexFromItem(byte_value_item)
                if type(byte_description) == dict:
                    if byte_description['type'] == 'num':
                        spin = QSpinBox()
                        spin.setMinimum(byte_description['min'])
                        spin.setMaximum(byte_description['max'])
                        spin.setSingleStep(byte_description['step'])
                        spin.setValue(byte_description['def_value'])
                        self.cmdtree.setIndexWidget(cb_index, spin)
                    elif byte_description['type'] == 'enum':
                        combo = QComboBox()
                        for text_, data_ in byte_description['values'].items():
                            combo.addItem(text_, data_)
                        self.cmdtree.setIndexWidget(cb_index, combo)
                    elif byte_description['type'] == 'const_num':
                        spin = QSpinBox()
                        spin.setMaximum(0xFF)
                        spin.setValue(byte_description['def_value'])
                        spin.setReadOnly(True)
                        spin.setDisplayIntegerBase(16)
                        spin.setPrefix('0x ')
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
                bytes_command += uint_to_bytes(_)
            self.signal.emit(signal_type('send_cmd', bytes_command))

    def open_file_dialog(self):
        dir_ = QFileDialog.getOpenFileName(None, 'Open File', '', 'CMD file (*.txt, *.json)')
        if dir_[0] != '':
            file_path = dir_[0]
            self.file_path_lable.setText('Path: ' + file_path)
            with open(file_path) as f:
                self.cmd_data = json.load(f)
            self.fill_tree(self.cmd_data)
            self.file_parse()
        print(dir_)

    def file_parse(self):
        self.perser_dict = {}
        for cmd_name, cmd_value in self.cmd_data.items():
            self.perser_dict.update({cmd_value['Command num']['def_value']: cmd_name})






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
        self.sp = SerialPortDriver.SP()
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
            read_cmd = self.sp.write_read(signal.value, len(signal.value))
            if len(read_cmd):
                key = self.cmd.perser_dict[int(read_cmd[1])]
                print(key)
                cmd_bytes_items = self.cmd.cmd_data[key]
                for name, item_ in cmd_bytes_items.items():
                    print(name)
                    if item_['type'] == 'const_num':
                        print(item_['def_value'])
                    elif item_['type'] == 'enum':
                        my_dict = item_['values']
                        my_dict = {my_dict[k]: k for k in my_dict}
                        print(my_dict[read_cmd[2]])




if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
