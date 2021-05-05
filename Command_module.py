import sys
from PyQt5.QtWidgets import (QComboBox, QLabel, QTextEdit, QListWidget, QGridLayout, QHBoxLayout, QVBoxLayout, QWidget,
                             QPushButton, QSpinBox, QCheckBox, QSlider, QGroupBox, QSpacerItem, QSizePolicy,
                             QMenu, QLCDNumber, QTreeWidget, QTreeWidgetItem, QTreeView, QFileDialog, QStackedWidget,
                             QListWidgetItem, QMessageBox)
from PyQt5.QtCore import pyqtSignal, QSignalMapper
from PyQt5.QtGui import QStandardItemModel, QStandardItem
from service import *
import json


class CmdViewerWidget(QWidget):
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
        self.file_path_lable = QLabel('<b>Path: </b>')
        self.file_dialog_btn = QPushButton('Open')
        self.file_dialog_btn.setShortcut('Ctrl+O')
        self.file_dialog_btn.setToolTip('<b>Open</b> command file .json')
        self.file_dialog_btn.setFixedSize(80, 40)
        self.file_dialog_btn.clicked.connect(self.open_file_dialog)
        file_layout = QHBoxLayout()
        file_layout.addWidget(self.file_path_lable)
        file_layout.addWidget(self.file_dialog_btn)
        file_group.setLayout(file_layout)

        prefix_group = QGroupBox('Prefix')
        self.prefix_check = QCheckBox('On')
        self.prefix_check.setChecked(True)
        self.prefix_check.clicked.connect(self.prefix_check_clicked)
        self.prefix_value = QSpinBox()
        self.prefix_value.setEnabled(True)
        self.prefix_value.setMaximum(255)
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
                byte_widget_index = self.model.indexFromItem(byte_value_item)
                if type(byte_description) == dict:
                    if byte_description['type'] == 'num':
                        spin = QSpinBox()
                        spin.setMinimum(byte_description['min'])
                        spin.setMaximum(byte_description['max'])
                        spin.setSingleStep(byte_description['step'])
                        spin.setValue(byte_description['def_value'])
                        self.cmdtree.setIndexWidget(byte_widget_index, spin)

                    elif byte_description['type'] == 'enum':
                        combo = QComboBox()
                        for text_, data_ in byte_description['values'].items():
                            combo.addItem(text_, data_)
                        self.cmdtree.setIndexWidget(byte_widget_index, combo)

                    elif byte_description['type'] == 'const_num':
                        spin = QSpinBox()
                        spin.setMaximum(0xFF)
                        spin.setValue(byte_description['def_value'])
                        spin.setReadOnly(True)
                        spin.setDisplayIntegerBase(16)
                        spin.setPrefix('0x')
                        self.cmdtree.setIndexWidget(byte_widget_index, spin)

                    elif byte_description['type'] == 'bool':
                        check = QCheckBox()
                        check.setChecked(byte_description['def_state'])
                        self.cmdtree.setIndexWidget(byte_widget_index, check)

                    elif byte_description['type'] == 'bit_field':
                        for bit_name, bit_description in byte_description['description'].items():
                            bit_name_item = QStandardItem(bit_name)
                            bit_value_item = QStandardItem()
                            byte_name_item.appendRow([bit_name_item, bit_value_item])
                            bit_widget_index = self.model.indexFromItem(bit_value_item)
                            if type(bit_description) == dict:
                                if bit_description['type'] == 'bit_enum':
                                    combo = QComboBox()
                                    combo.start_bit = bit_description['start_bit']
                                    combo.quantity_bit = bit_description['quantity_bit']
                                    for text_, data_ in bit_description['values'].items():
                                        combo.addItem(text_, data_)
                                    self.cmdtree.setIndexWidget(bit_widget_index, combo)

                                elif bit_description['type'] == 'bit_bool':
                                    check = QCheckBox()
                                    check.setChecked(bit_description['def_state'])
                                    check.bit_num = bit_description['bit_num']
                                    self.cmdtree.setIndexWidget(bit_widget_index, check)

                                elif bit_description['type'] == 'bit_num':
                                    pass

        self.mapper.mapped[int].connect(self.btn_press)
        self.model.setHorizontalHeaderLabels(['Names', 'Values', 'Send buttons'])
        self.cmdtree.setColumnWidth(0, 200)
        self.cmdtree.setColumnWidth(1, 200)

    def btn_press(self, row_num):
        command_item = self.model.item(row_num, 0)
        command = b''
        if self.prefix_check.isChecked():
            command += self.prefix_value.value().to_bytes(1, 'little', signed=False)
        if command_item.hasChildren():
            for i in range(command_item.rowCount()):
                byte_name_item = command_item.child(i, 0)
                byte_widget_item = command_item.child(i, 1)
                if not byte_name_item.hasChildren():
                    index_ = self.model.indexFromItem(byte_widget_item)
                    widget_ = self.cmdtree.indexWidget(index_)
                    if type(widget_) == QComboBox:
                        command += widget_.currentData().to_bytes(1, 'little', signed=False)
                    elif type(widget_) == QSpinBox:
                        if widget_.maximum() > 0xFF:
                            command += widget_.value().to_bytes(2, 'little', signed=False)
                        else:
                            command += widget_.value().to_bytes(1, 'little', signed=False)
                    elif type(widget_) == QCheckBox:
                        command += widget_.isChecked().to_bytes(1, 'little', signed=False)
                    else:
                        pass
                else:
                    byte_ = 0
                    for j in range(byte_name_item.rowCount()):
                        bit_widget_item = byte_name_item.child(j, 1)
                        index_ = self.model.indexFromItem(bit_widget_item)
                        widget_ = self.cmdtree.indexWidget(index_)
                        if type(widget_) == QComboBox:
                            byte_ += widget_.currentData() << widget_.start_bit
                        elif type(widget_) == QCheckBox:
                            byte_ = bit_change(byte_, widget_.bit_num, widget_.isChecked())
                    command += byte_.to_bytes(1, 'little', signed=False)

        self.signal.emit(signal_type('send_cmd', command))

    def open_file_dialog(self):
        dir_ = QFileDialog.getOpenFileName(None, 'Open File', '', 'CMD file (*.txt, *.json)')
        if dir_[0] != '':
            file_path = dir_[0]
            self.file_path_lable.setText('Path: ' + file_path)
            with open(file_path) as f:
                self.cmd_data = json.load(f)
            self.fill_tree(self.cmd_data)
        print(dir_)

    def prefix_check_clicked(self):
        if self.prefix_check.isChecked():
            self.prefix_check.setText("On")
            self.prefix_value.setEnabled(True)
        else:
            self.prefix_check.setText('Off')
            self.prefix_value.setEnabled(False)


class CmdCreatorWidget(QWidget):
    signal = pyqtSignal(signal_type)

    def __init__(self):
        super().__init__()
        self.__create_widgets()
        self.create_stack_widgets()

    def __create_widgets(self):
        self.main_layout = QVBoxLayout()
        self.setLayout(self.main_layout)

        add_layout = QHBoxLayout()
        self.main_layout.addLayout(add_layout)
        self.te_cmd_name = QTextEdit('Some name')
        self.te_cmd_name.setMaximumHeight(24)
        self.sb_cmd_num = QSpinBox()
        self.sb_cmd_num.setMaximum(0xFF)
        self.sb_cmd_num.setPrefix('0x')
        self.sb_cmd_num.setDisplayIntegerBase(16)
        self.sb_cmd_num.setMaximumHeight(40)
        self.btn_add_cmd = QPushButton('Add byte')
        add_layout.addWidget(QLabel('Name: '))
        add_layout.addWidget(self.te_cmd_name)
        add_layout.addWidget(QLabel('Number: '))
        add_layout.addWidget(self.sb_cmd_num)
        add_layout.addWidget(self.btn_add_cmd)

        self.cmdtree = QTreeView()
        self.model = QStandardItemModel()
        self.cmdtree.setModel(self.model)
        self.main_layout.addWidget(self.cmdtree)

        self.cb_byte_type = QComboBox()
        self.cb_byte_type.addItem('enum', 0)
        self.cb_byte_type.addItem('const_num', 1)

        self.btn_add_byte = QPushButton('Add')
        self.stack = QStackedWidget(self)
        self.layout_stack = QHBoxLayout()
        self.main_layout.addLayout(self.layout_stack)
        layout1 = QVBoxLayout()
        self.layout_stack.addLayout(layout1)
        layout1.addWidget(self.cb_byte_type)
        layout1.addWidget(self.btn_add_byte)
        self.layout_stack.addWidget(self.stack)

        self.cb_byte_type.currentIndexChanged.connect(lambda: self.stack.setCurrentIndex(self.cb_byte_type.currentIndex()))
        self.btn_add_byte.clicked.connect(self.add_byte)
        self.btn_add_cmd.clicked.connect(self.create_cmd)

    def create_cmd(self):
        self.cmd_name = self.te_cmd_name.toPlainText()
        self.cmd = {
                    self.cmd_name:
                        {
                            'Command num':
                                {
                                    'type': 'const_num',
                                    'def_value': self.sb_cmd_num.value(),
                                },
                        }
                    }
        self.fill_tree()

    def add_byte(self):
        byte_type = self.cb_byte_type.currentText()
        if byte_type == 'enum':
            added_byte = self.widget_enum.get_byte_item()
        elif byte_type == 'num':
            pass
        elif byte_type == 'const_num':
            pass
        elif byte_type == 'bool':
            pass
        elif byte_type == 'bit_field':
            pass


        self.cmd[self.cmd_name].update(added_byte)
        self.fill_tree()

    def fill_tree(self):
        self.model.clear()
        i = 0
        for cmd_name, cmd in self.cmd.items():
            print(cmd_name)
            cmd_name_item = QStandardItem(cmd_name)
            space = QStandardItem()
            send_btn_item = QStandardItem()
            self.model.appendRow([cmd_name_item])
            i += 1
            for byte_name, byte_description in cmd.items():
                byte_name_item = QStandardItem(byte_name)
                byte_value_item = QStandardItem()
                cmd_name_item.appendRow([byte_name_item, byte_value_item])
                byte_widget_index = self.model.indexFromItem(byte_value_item)
                if type(byte_description) == dict:
                    if byte_description['type'] == 'num':
                        spin = QSpinBox()
                        spin.setMinimum(byte_description['min'])
                        spin.setMaximum(byte_description['max'])
                        spin.setSingleStep(byte_description['step'])
                        spin.setValue(byte_description['def_value'])
                        self.cmdtree.setIndexWidget(byte_widget_index, spin)

                    elif byte_description['type'] == 'enum':
                        combo = QComboBox()
                        for text_, data_ in byte_description['values'].items():
                            combo.addItem(text_, data_)
                        self.cmdtree.setIndexWidget(byte_widget_index, combo)

                    elif byte_description['type'] == 'const_num':
                        spin = QSpinBox()
                        spin.setMaximum(0xFF)
                        spin.setValue(byte_description['def_value'])
                        spin.setReadOnly(True)
                        spin.setDisplayIntegerBase(16)
                        spin.setPrefix('0x')
                        self.cmdtree.setIndexWidget(byte_widget_index, spin)

                    elif byte_description['type'] == 'bool':
                        check = QCheckBox()
                        check.setChecked(byte_description['def_state'])
                        self.cmdtree.setIndexWidget(byte_widget_index, check)

                    elif byte_description['type'] == 'bit_field':
                        for bit_name, bit_description in byte_description['description'].items():
                            bit_name_item = QStandardItem(bit_name)
                            bit_value_item = QStandardItem()
                            byte_name_item.appendRow([bit_name_item, bit_value_item])
                            bit_widget_index = self.model.indexFromItem(bit_value_item)
                            if type(bit_description) == dict:
                                if bit_description['type'] == 'bit_enum':
                                    combo = QComboBox()
                                    combo.start_bit = bit_description['start_bit']
                                    combo.quantity_bit = bit_description['quantity_bit']
                                    for text_, data_ in bit_description['values'].items():
                                        combo.addItem(text_, data_)
                                    self.cmdtree.setIndexWidget(bit_widget_index, combo)

                                elif bit_description['type'] == 'bit_bool':
                                    check = QCheckBox()
                                    check.setChecked(bit_description['def_state'])
                                    check.bit_num = bit_description['bit_num']
                                    self.cmdtree.setIndexWidget(bit_widget_index, check)

                                elif bit_description['type'] == 'bit_num':
                                    pass

        self.model.setHorizontalHeaderLabels(['Names', 'Values'])
        self.cmdtree.setColumnWidth(0, 200)
        self.cmdtree.setColumnWidth(1, 200)

    def create_stack_widgets(self):
        self.widget_enum = WidgetEnum()
        self.stack.addWidget(self.widget_enum)


class WidgetEnum(QWidget):
    signal = pyqtSignal(signal_type)

    def __init__(self):
        super().__init__()
        self.__create_widgets()
        self.item_add.clicked.connect(self.add_item_to_list)
        self.items = {}

    def __create_widgets(self):
        self.main_layout = QVBoxLayout()
        self.setLayout(self.main_layout)

        lable_name = QLabel('Enum byte name:')
        self.te_name = QTextEdit('Some byte name')
        self.te_name.setMaximumHeight(24)
        layout_name = QHBoxLayout()
        self.main_layout.addLayout(layout_name)
        layout_name.addWidget(lable_name)
        layout_name.addWidget(self.te_name)

        group_box = QGroupBox('Values')
        self.main_layout.addWidget(group_box)

        gb_layout = QVBoxLayout()
        group_box.setLayout(gb_layout)
        self.items_list = QListWidget()
        gb_layout.addWidget(self.items_list)
        add_layout = QHBoxLayout()
        gb_layout.addLayout(add_layout)
        self.item_value = QSpinBox()
        self.item_value.setMaximum(0xFF)
        self.item_value.setPrefix('0x')
        self.item_value.setDisplayIntegerBase(16)
        self.item_value.setMaximumHeight(40)
        self.item_name = QTextEdit('Name')
        self.item_name.setMaximumHeight(24)
        self.item_add = QPushButton('Add')
        add_layout.addWidget(QLabel('Value'))
        add_layout.addWidget(self.item_value)
        add_layout.addWidget(QLabel('Name'))
        add_layout.addWidget(self.item_name)
        add_layout.addWidget(self.item_add)

    def add_item_to_list(self):
        name = self.item_name.toPlainText()
        data = self.item_value.value()
        self.items.update({name: data})
        self.items_list.clear()
        for name_, data_ in self.items.items():
            item = QListWidgetItem(name_)
            item.setData(3, data_)
            self.items_list.addItem(item)

    def get_byte_item(self):
        byte_name = self.te_name.toPlainText()
        byte_ = {
            byte_name:
            {
                'type': 'enum',
                'values': self.items
            }
        }
        self.items = {}
        self.items_list.clear()
        print(byte_)
        return byte_


def cmd_parser(cmd: bytes, protocol: dict, is_prefix_on: bool):
    if len(cmd):
        count = 0
        res_str = ''
        if is_prefix_on:
            res_str += 'Device number: ' + str(cmd[count]) + '\n'
            count += 1
        command_num = cmd[count]
        parser_dict = {}
        for cmd_name, cmd_value in protocol.items():
            parser_dict.update({cmd_value['Command num']['def_value']: cmd_name})
        command_name = parser_dict[command_num]
        cmd_bytes_dict = protocol[command_name]
        res_str += 'Command name: ' + command_name + '\r'
        for byte_name, description in cmd_bytes_dict.items():
            res_str += byte_name + ': '
            if description['type'] == 'const_num':
                res_str += str(description['def_value']) + '\r'

            elif description['type'] == 'enum':
                my_dict = description['values']
                my_dict = {my_dict[k]: k for k in my_dict}
                res_str += my_dict[cmd[count]] + '\r'

            elif description['type'] == 'num':
                if description['max'] > 0xFF:
                    res_str += str(cmd[count] + cmd[count + 1] * 0x100) + '\r'
                    count += 1
                else:
                    res_str += str(cmd[count]) + '\r'

            elif description['type'] == 'bool':
                res_str += str(bool(cmd[count])) + '\r'

            elif description['type'] == 'bit_field':
                res_str += '\r'
                byte_ = cmd[count]
                for bit_name, bit_description in description['description'].items():
                    res_str += bit_name + ': '
                    if bit_description['type'] == 'bit_bool':
                        state = get_bit_from_byte(byte_, bit_description['bit_num'])
                        res_str += str(state) + '\r'
                    elif bit_description['type'] == 'bit_enum':
                        my_dict = bit_description['values']
                        my_dict = {my_dict[k]: k for k in my_dict}
                        current_num = get_bits_from_byte(byte_, bit_description['start_bit'],
                                                         bit_description['quantity_bit'])
                        res_str += my_dict[current_num] + '\r'

            count += 1
        return res_str