import sys
from PyQt5.QtWidgets import *
from PyQt5.QtCore import pyqtSignal, Qt, QSignalMapper, QSize, QSettings
from PyQt5.QtGui import QStandardItemModel, QStandardItem, QIcon
from utility import *
import json
import copy


class CmdViewerWidget(QWidget):
    signal = pyqtSignal(signal_type)
    signal_bytes = pyqtSignal(signal_cmd)
    signal_info = pyqtSignal(signal_info)

    def __init__(self):
        super().__init__()
        self.setWindowIcon(QIcon(r'icons/send.svg'))
        self.cmd_creator = CmdCreatorWidget()
        self.__create_widgets()
        self.setMinimumWidth(550)
        self.btns_list = []  # список кнопок в дереве
        self.cmd_data = None  # словарь вычитанный из файла
        self.change_flag = False
        self.settings = QSettings('KBRadar', 'ComClientGen3')

    def __create_widgets(self):
        self.main_layout = QVBoxLayout()
        self.setLayout(self.main_layout)

        self.cmdtree = QTreeView()
        self.cmdtree.setSortingEnabled(True)
        self.cmdtree.setMinimumWidth(594)
        #self.cmdtree.setDragEnabled(True)
        #self.cmdtree.setDragDropMode(QAbstractItemView.InternalMove)
        #self.cmdtree.dropEvent = self.dropEvent_
        self.model = QStandardItemModel()
        self.model.setSortRole(5)
        self.cmdtree.setModel(self.model)
        self.mapper = QSignalMapper()

        file_group = QGroupBox()
        self.file_path_lable = QLabel()
        self.file_dialog_btn = QPushButton('Open')
        self.file_dialog_btn.setShortcut('Ctrl+O')
        self.file_dialog_btn.setToolTip('Open command file (*.json)')
        self.file_dialog_btn.setFixedSize(70, 30)
        self.file_dialog_btn.setIcon(QIcon(r'icons/folder.svg'))
        file_layout = QHBoxLayout()
        file_layout.addWidget(QLabel('Path: '))
        file_layout.addWidget(self.file_path_lable)
        file_layout.addStretch(1)
        file_layout.addWidget(self.file_dialog_btn)
        file_group.setLayout(file_layout)

        self.l_current_cmd = QLabel()
        self.l_current_cmd.setFont(QFont('Consolas', 9))

        self.del_cmd_btn = QPushButton('Delete')
        self.del_cmd_btn.setIcon(QIcon(r'icons/delete.svg'))

        self.add_cmd_btn = QPushButton('Add')
        self.add_cmd_btn.setIcon(QIcon(r'icons/plus-square.svg'))

        self.edit_cmd_btn = QPushButton('Edit')
        self.edit_cmd_btn.setIcon(QIcon(r'icons/edit.svg'))

        self.sort_cmd_btn = QPushButton('Sort')
        self.sort_cmd_btn.setIcon(QIcon(r'icons/sort.svg'))

        self.collapse_all_btn = QPushButton('Collapse all')
        self.expand_all_btn = QPushButton('Expand all')

        btn_layout = QHBoxLayout()
        btn_layout.addWidget(self.expand_all_btn)
        btn_layout.addWidget(self.collapse_all_btn)
        btn_layout.addWidget(self.sort_cmd_btn)
        btn_layout.addStretch(1)
        btn_layout.addWidget(self.add_cmd_btn)
        btn_layout.addWidget(self.del_cmd_btn)
        btn_layout.addWidget(self.edit_cmd_btn)

        self.main_layout.addWidget(file_group)
        self.main_layout.addWidget(self.cmdtree)
        #self.main_layout.addWidget(self.l_current_cmd)
        self.main_layout.addLayout(btn_layout)

        self.file_dialog_btn.clicked.connect(self.open_file_dialog)
        self.del_cmd_btn.clicked.connect(self.del_cmd)
        self.edit_cmd_btn.clicked.connect(self.edit_cmd)
        self.cmdtree.selectionModel().selectionChanged.connect(self.selection_item_changed)
        self.sort_cmd_btn.clicked.connect(self.sort_cmds)
        self.collapse_all_btn.clicked.connect(self.cmdtree.collapseAll)
        self.expand_all_btn.clicked.connect(lambda: self.cmdtree.expandToDepth(1))
        self.add_cmd_btn.clicked.connect(self.open_cmd_creator)
        self.cmd_creator.signal_cmd.connect(self.add_cmd, Qt.QueuedConnection)

    def selection_item_changed(self, new, old):
        index = new.indexes()[0]
        if index.parent().data() is None:
            item = self.model.item(index.row(), 0)
            cmd, cmd_num_position = self.get_cmd_current_bytes(item)
            self.signal_info.emit(signal_info('Hex: ' + bytes_to_hex_string(cmd), QFont('Consolas', 9)))

    def edit_cmd(self):
        index = self.cmdtree.currentIndex()
        while index.parent().data() is not None:
            index = index.parent()
        cmd_name = index.data()
        if cmd_name is not None:
            #self.signal.emit(signal_type('edit_cmd', (cmd_name, self.cmd_data[cmd_name])))
            self.cmd_creator.edit_cmd(cmd_name, {cmd_name: self.cmd_data[cmd_name]})
            self.cmd_creator.show()

    def del_cmd(self):
        index = self.cmdtree.currentIndex()
        while index.parent().data() is not None:
            index = index.parent()
        cmd_name = index.data()
        if cmd_name is not None:
            dialog = CustomDialog('Are you sure you want to delete this command\n\"{}\"?'.format(index.data()))
            if dialog.exec_():
                del self.cmd_data[cmd_name]
                self.fill_tree(self.cmd_data)
                self.change_flag = True

    def add_cmd(self, cmd: signal_cmd):
        if self.cmd_data is None:
            self.cmd_data = {}
        self.cmd_data.update(cmd)
        self.fill_tree(self.cmd_data)
        self.change_flag = True
        self.signal_info.emit(signal_info('ok', 'green'))

    def sort_cmds(self):
        if self.cmd_data is not None:
            self.cmd_data = dict(sorted(self.cmd_data.items()))
            #self.change_flag = True
            self.fill_tree(self.cmd_data)

    def save_file_changes(self):
        file_path = self.file_path_lable.text()
        if file_path != '':
            with open(file_path, 'w', encoding='utf-8') as fp:
                json.dump(self.cmd_data, fp, sort_keys=False, indent=4, ensure_ascii=False)
            self.change_flag = False
            self.signal_info.emit(signal_info(f'Saved: {file_path}', None))

    def save_to(self):
        dir_ = QFileDialog.getSaveFileName(None, 'Save File', '', 'CMD file (*.json)')
        if dir_[0] != '':
            file_path = dir_[0]
            with open(file_path, 'w', encoding='utf-8') as fp:
                json.dump(self.cmd_data, fp, sort_keys=False, indent=4, ensure_ascii=False)
            self.change_flag = False
            self.signal_info.emit(signal_info(f'Saved to: {file_path}', None))
            self.file_path_lable.setText(file_path)

    def clear_tree(self):
        """ Очистка модели дерева """
        self.model.clear()
        if len(self.btns_list):
            self.mapper.disconnect()

    def fill_tree(self, commands):
        """ Заполние модели дерева """
        self.clear_tree()
        i = 0
        for cmd_name, cmd in commands.items():

            cmd_name_item = QStandardItem(cmd_name)
            cmd_num_item = QStandardItem(hex(cmd["Command num"]["def_value"]))
            _font = cmd_name_item.font()
            _font.setBold(True)
            cmd_name_item.setFont(_font)
            cmd_num_item.setTextAlignment(Qt.AlignCenter)
            send_btn_item = QStandardItem()
            self.model.appendRow([cmd_name_item, cmd_num_item, send_btn_item])

            btn_send = QPushButton('Send')
            self.btns_list.append(btn_send)
            self.mapper.setMapping(btn_send, i)
            i += 1
            btn_send.clicked.connect(self.mapper.map)
            btn_send.setStyleSheet('background-color: darkGrey;'
                                   'border-style: outset;'
                                   'border-width: 1px;'
                                   'border-radius: 5px;'
                                   'border-color: beige;'
                                   'font: bold 12px;'
                                   'color: white;'
                                   'padding: 4px;')
            btn_send.setFixedWidth(90)

            cmd_index = self.model.indexFromItem(send_btn_item)
            self.cmdtree.setIndexWidget(cmd_index, btn_send)

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
                        self.mapper.setMapping(spin, str(i))
                        spin.valueChanged.connect(self.mapper.map)

                    elif byte_description['type'] == 'enum':
                        combo = QComboBox()
                        for text_, data_ in byte_description['values'].items():
                            combo.addItem(text_, data_)
                        self.cmdtree.setIndexWidget(byte_widget_index, combo)
                        self.mapper.setMapping(combo, str(i))
                        combo.currentIndexChanged.connect(self.mapper.map)

                    elif byte_description['type'] == 'const_num':
                        spin = QSpinBox()
                        spin.setMaximum(0xFF)
                        spin.setValue(byte_description['def_value'])
                        spin.setReadOnly(True)
                        spin.setDisplayIntegerBase(16)
                        spin.setPrefix('0x')
                        spin.setDisabled(True)
                        self.cmdtree.setIndexWidget(byte_widget_index, spin)

                    elif byte_description['type'] == 'bool':
                        check = QCheckBox()
                        check.setChecked(byte_description['def_state'])
                        self.cmdtree.setIndexWidget(byte_widget_index, check)
                        self.mapper.setMapping(check, str(i))
                        check.stateChanged.connect(self.mapper.map)

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
                                    self.mapper.setMapping(combo, str(i))
                                    combo.currentIndexChanged.connect(self.mapper.map)

                                elif bit_description['type'] == 'bit_bool':
                                    check = QCheckBox()
                                    check.setChecked(bit_description['def_state'])
                                    check.bit_num = bit_description['bit_num']
                                    self.cmdtree.setIndexWidget(bit_widget_index, check)
                                    self.mapper.setMapping(check, str(i))
                                    check.stateChanged.connect(self.mapper.map)

                                elif bit_description['type'] == 'bit_num':
                                    pass

        self.mapper.mapped[str].connect(self.description_widget_data_changed)
        self.mapper.mapped[int].connect(self.btn_send_pressed)
        self.model.setHorizontalHeaderLabels(['Names', 'Values', 'Send buttons'])
        self.cmdtree.setColumnWidth(0, 390)
        self.cmdtree.setColumnWidth(1, 110)

    def get_cmd_current_bytes(self, command_item):
        command = b''
        command_num_position = None
        if command_item.hasChildren():
            for i in range(command_item.rowCount()):
                byte_name_item = command_item.child(i, 0)
                byte_widget_item = command_item.child(i, 1)
                if byte_name_item.text() == 'Command num':
                    command_num_position = i
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
            return command, command_num_position

    def btn_send_pressed(self, row_num):
        """ Функция - обработчик нажатия на кнопку Send напротив команты.
         Составляет команду и отправляет ее сигналом."""
        command_item = self.model.item(row_num, 0)
        command, command_num_position = self.get_cmd_current_bytes(command_item)
        self.signal_bytes.emit(signal_cmd('send_cmd', command, command_num_position))

    def description_widget_data_changed(self, row_num):
        item = self.model.item(int(row_num)-1, 0)
        cmd, cmd_num_position = self.get_cmd_current_bytes(item)
        self.signal_info.emit(signal_info('Hex: ' + bytes_to_hex_string(cmd), QFont('Consolas', 9)))

    def open_file_dialog(self):
        if self.settings.contains("last_file_path"):
            last_path = self.settings.value('last_file_path')
        else:
            last_path = ''
        self.check_changes()
        dir_ = QFileDialog.getOpenFileName(None, 'Open File', last_path, 'CMD file (*.json)')
        if dir_[0] != '':
            file_path = dir_[0]
            self.file_path_lable.setText(file_path)
            self.open_file(file_path)

    def open_file(self, path):
        with open(path, 'r', encoding='utf-8') as f:
            self.cmd_data = json.load(f)
            self.fill_tree(self.cmd_data)
            self.settings.setValue('last_file_path', path)
            self.change_flag = False
            self.signal_info.emit(signal_info(f'Opened {path}', None))

    def check_changes(self):
        """
        Возвращает False в том случае, если пользователь нажал Cancel
                   True - пользователь нажал Yes или No
                   True - файл не изменялся
        """
        if self.change_flag is True:
            result = QMessageBox.warning(None, 'Save file ', "You haven't saved changes. Do you want to save?",
                                         buttons=QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel,
                                         defaultButton=QMessageBox.Cancel)
            if result == QMessageBox.Yes:
                self.save_to()
                return True
            elif result == QMessageBox.No:
                return True
            elif result == QMessageBox.Cancel:
                return False
        else:
            return True

    def open_cmd_creator(self):
        self.cmd_creator.show()
        self.cmd_creator.resize(600, 600)




class CmdCreatorWidget(QWidget):
    signal_cmd = pyqtSignal(dict)

    def __init__(self):
        super().__init__()
        self.setWindowTitle('Command creator')
        self.__create_widgets()
        self.create_stack_widgets()
        self.cmd = {}
        self.cmd_name = None

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
        self.btn_add_cmd = QPushButton('Create')
        # self.btn_add_cmd.setIcon(QIcon(r'icons/pl'))
        add_layout.addWidget(QLabel('Name: '))
        add_layout.addWidget(self.te_cmd_name)
        add_layout.addWidget(QLabel('Number: '))
        add_layout.addWidget(self.sb_cmd_num)
        add_layout.addWidget(self.btn_add_cmd)

        self.cmdtree = QTreeView()
        self.cmdtree.setDisabled(True)
        self.cmdtree.setMinimumHeight(200)
        self.model = QStandardItemModel()
        self.cmdtree.setModel(self.model)
        self.main_layout.addWidget(self.cmdtree)

        layout1 = QHBoxLayout()
        self.btn_clear_cmd = QPushButton('Clear')
        self.btn_clear_cmd.setIcon(QIcon(r'icons/trash.svg'))

        self.btn_del_byte = QPushButton('Delete')
        self.btn_del_byte.setIcon(QIcon(r'icons/delete.svg'))

        self.pb_up_byte = QPushButton('Up')
        self.pb_up_byte.setIcon(QIcon(r'icons/chevron-up.svg'))

        self.pb_down_byte = QPushButton('Down')
        self.pb_down_byte.setIcon(QIcon(r'icons/chevron-down.svg'))

        layout1.addWidget(self.btn_del_byte)
        layout1.addWidget(self.btn_clear_cmd)
        layout1.addStretch(1)
        layout1.addWidget(self.pb_up_byte)
        layout1.addWidget(self.pb_down_byte)
        self.main_layout.addLayout(layout1)

        self.lw_byte_type = QListWidget()
        self.lw_byte_type.insertItem(0, 'Enum')
        self.lw_byte_type.insertItem(1, 'Bool')
        self.lw_byte_type.insertItem(2, 'Num')
        self.lw_byte_type.insertItem(3, 'Bit_field')
        self.lw_byte_type.setCurrentRow(0)

        self.btn_add_byte = QPushButton('Add byte')
        self.btn_add_byte.setIcon(QIcon(r'icons/plus-square.svg'))
        self.stack = QStackedWidget(self)
        self.layout_stack = QHBoxLayout()
        self.main_layout.addSpacing(30)
        self.main_layout.addLayout(self.layout_stack)

        layout2 = QVBoxLayout()
        group_byte_type = QGroupBox('Byte type')
        group_byte_type.setLayout(layout2)
        group_byte_type.setMaximumWidth(200)
        self.layout_stack.addWidget(group_byte_type)

        layout2.addWidget(self.lw_byte_type)
        # layout2.addStretch(1)
        #layout2.addWidget(self.btn_add_byte)
        #layout1.insertWidget(0, self.btn_add_byte)

        v_line = QFrame()
        v_line.setFrameShape(QFrame.VLine)
        #v_line.setLineWidth(0.5)
        self.layout_stack.addWidget(v_line)

        gb_byte_description = QGroupBox('Byte description')
        layout3 = QHBoxLayout()
        gb_byte_description.setLayout(layout3)
        layout3.addWidget(self.stack)
        self.layout_stack.addWidget(gb_byte_description)
        self.main_layout.addWidget(self.btn_add_byte)
        self.btn_add_byte.setMinimumHeight(32)

        self.buttonBox = QDialogButtonBox()
        self.buttonBox.setStandardButtons(QDialogButtonBox.Cancel | QDialogButtonBox.Ok)
        self.main_layout.addSpacing(40)
        self.main_layout.addWidget(self.buttonBox)

        self.lw_byte_type.currentRowChanged.connect(lambda i: self.stack.setCurrentIndex(i))
        self.btn_add_byte.clicked.connect(self.add_byte)
        self.btn_add_cmd.clicked.connect(self.create_cmd)
        self.btn_del_byte.clicked.connect(self.del_byte)
        self.btn_clear_cmd.clicked.connect(self.clear_cmds)
        self.pb_down_byte.clicked.connect(lambda: self.move_byte('down'))
        self.pb_up_byte.clicked.connect(lambda: self.move_byte('up'))
        self.buttonBox.button(QDialogButtonBox.Cancel).clicked.connect(self.close)
        self.buttonBox.button(QDialogButtonBox.Ok).clicked.connect(lambda: self.signal_cmd.emit(self.cmd))

    def move_byte(self, direction='up'):
        item = self.cmdtree.currentIndex()
        if item.parent().data() is not None:  # проверка есть ли у этой записи родитель
            index = self.cmdtree.currentIndex().row()
            if index == 0 and direction == 'up':
                return
            if direction == 'up':
                index -= 1
            elif direction == 'down':
                index += 1
            item_dict = copy.deepcopy(self.cmd[self.cmd_name][item.data()])
            del self.cmd[self.cmd_name][item.data()]
            self.cmd[self.cmd_name] = insert_item_to_dict(self.cmd[self.cmd_name], index, {item.data(): item_dict})
            self.fill_tree()

    def create_cmd(self):
        cmd_name = self.te_cmd_name.toPlainText()
        if cmd_name != '':
            self.cmd_name = cmd_name
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
        else:
            QMessageBox.warning(None, 'Info ', "Command name cannot be empty!", buttons=QMessageBox.Ok)

    def edit_cmd(self, cmd_name, cmd):
        self.cmd_name = cmd_name
        self.cmd = cmd
        self.te_cmd_name.setText(cmd_name)
        self.sb_cmd_num.setValue(cmd[cmd_name]['Command num']['def_value'])
        self.fill_tree()

    def clear_cmds(self):
        self.cmd = {}
        self.model.clear()
        self.cmdtree.setDisabled(True)


    def del_byte(self):
        item_name = self.cmdtree.currentIndex().data()
        if item_name == "Command num":
            return
        elif item_name == self.cmd_name:
            return
        elif item_name is None:
            return
        else:
                logger.debug(f'From \'{self.cmd_name}\' delete item \'{item_name}\'')
                del self.cmd[self.cmd_name][item_name]
                self.fill_tree()


    def add_byte(self):
        if self.cmd != {}:
            byte_type = self.lw_byte_type.currentItem().text()
            if byte_type == 'Enum':
                added_byte = self.widget_enum.get_byte_item()
            elif byte_type == 'Num':
                added_byte = self.widget_num.get_byte_item()
            elif byte_type == 'Const_num':
                pass
            elif byte_type == 'Bool':
                added_byte = self.widget_bool.get_byte_item()
            elif byte_type == 'Bit_field':
                added_byte = self.widget_bit_fild.get_byte_item()
            self.cmd[self.cmd_name].update(added_byte)
            self.fill_tree()
        else:
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Information)
            msg.setWindowIcon(QIcon(r'icons/message-square.svg'))
            msg.setWindowTitle('Info')
            msg.setText('First, create a command.')
            msg.exec()
            self.btn_add_byte.setFocus()

    def fill_tree(self):
        self.model.clear()
        self.cmdtree.setDisabled(False)
        i = 0
        for cmd_name, cmd in self.cmd.items():
            cmd_name_item = QStandardItem(cmd_name)
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
                        spin.setDisabled(True)
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
        self.cmdtree.expandToDepth(1)

    def create_stack_widgets(self):
        self.widget_enum = WidgetEnum()
        self.stack.addWidget(self.widget_enum)
        self.widget_bool = WidgetBool()
        self.stack.addWidget(self.widget_bool)
        self.widget_num = WidgetNum()
        self.stack.addWidget(self.widget_num)
        self.widget_bit_fild = WidgetBitField()
        self.stack.addWidget(self.widget_bit_fild)


class WidgetEnum(QWidget):
    signal = pyqtSignal(signal_type)

    def __init__(self, type_='byte'):
        super().__init__()
        self.type_ = type_
        self.__create_widgets()
        self.pb_item_add.clicked.connect(self.add_item)
        self.pb_item_del.clicked.connect(self.del_item)
        self.pb_clear_list.clicked.connect(self.clear_list)
        self.items = {}

    def __create_widgets(self):
        self.main_layout = QVBoxLayout()
        self.setLayout(self.main_layout)

        lable_name = QLabel('Name:')
        self.te_name = QTextEdit('Some enum name')
        self.te_name.setMaximumHeight(24)
        layout_name = QHBoxLayout()
        self.main_layout.addLayout(layout_name)
        layout_name.addWidget(lable_name)
        layout_name.addWidget(self.te_name)

        if self.type_ == 'bit':
            self.setWindowTitle('Bit_enum')
            self.sp_start_bit = QSpinBox()
            self.sp_start_bit.setMaximum(7)
            self.sp_quantity_bit = QSpinBox()
            self.sp_quantity_bit.setMinimum(2)
            self.sp_quantity_bit.setMaximum(8)
            layout_2 = QHBoxLayout()
            layout_2.addWidget(QLabel('Start'))
            layout_2.addWidget(self.sp_start_bit)
            layout_2.addSpacing(30)
            layout_2.addWidget(QLabel('Quantity'))
            layout_2.addWidget(self.sp_quantity_bit)
            layout_2.addStretch(1)
            self.main_layout.addLayout(layout_2)

        group_box = QGroupBox()
        self.main_layout.addWidget(group_box)

        gb_layout = QVBoxLayout()
        group_box.setLayout(gb_layout)
        self.items_list = QListWidget()

        add_layout = QHBoxLayout()
        gb_layout.addLayout(add_layout)
        gb_layout.addWidget(self.items_list)
        self.item_value = QSpinBox()
        self.item_value.setMaximum(0xFF)
        self.item_value.setPrefix('0x')
        self.item_value.setDisplayIntegerBase(16)
        self.item_value.setMinimumWidth(50)
        # self.item_value.setMaximumHeight(40)

        self.item_name = QTextEdit('Item name')
        self.item_name.setMaximumHeight(24)

        self.pb_item_add = QPushButton('Add')
        self.pb_item_add.setIcon(QIcon(r'icons/plus.svg'))

        self.pb_item_del = QPushButton('Delete')
        self.pb_item_del.setIcon(QIcon(r'icons/delete.svg'))

        self.pb_clear_list = QPushButton('Clear')
        self.pb_clear_list.setIcon(QIcon(r'icons/trash.svg'))

        add_layout.addWidget(QLabel('Name'))
        add_layout.addWidget(self.item_name)
        add_layout.addWidget(QLabel('Num'))
        add_layout.addWidget(self.item_value)
        add_layout.addWidget(self.pb_item_add)

        layout_3 = QHBoxLayout()
        self.main_layout.addLayout(layout_3)

        layout_3.addWidget(self.pb_item_del)
        layout_3.addWidget(self.pb_clear_list)
        layout_3.addStretch(1)

        if self.type_ == 'bit':
            self.btn_ok = QPushButton('Ok')
            self.btn_ok.clicked.connect(self.btn_ok_clicked)

            self.btn_cancel = QPushButton('Cancel')
            self.btn_cancel.clicked.connect(self.close)

            layout_ok_cancel = QHBoxLayout()
            layout_ok_cancel.addWidget(self.btn_ok)
            layout_ok_cancel.addStretch(1)
            layout_ok_cancel.addWidget(self.btn_cancel)
            self.main_layout.addSpacing(50)
            self.main_layout.addLayout(layout_ok_cancel)

    def add_item(self):
        name = self.item_name.toPlainText()
        data = self.item_value.value()
        self.items.update({name: data})
        self.items_list.clear()
        for name_, data_ in self.items.items():
            item = QListWidgetItem(name_)
            item.setData(3, data_)
            self.items_list.addItem(item)

    def del_item(self):
        all_items = self.items_list.selectedItems()
        if not all_items:
            return
        for item in all_items:
            self.items_list.takeItem(self.items_list.row(item))
            del self.items[item.text()]

    def clear_list(self):
        self.items_list.clear()
        self.items = {}

    def get_byte_item(self):
        byte_name = self.te_name.toPlainText()
        byte_ = {
            byte_name:
                {
                    'type': 'enum',
                    'values': self.items
                }
        }
        return byte_

    def get_bit_item(self):
        bit_name = self.te_name.toPlainText()
        bit_ = {
            bit_name:
                {
                    'type': 'bit_enum',
                    'start_bit': self.sp_start_bit.value(),
                    'quantity_bit': self.sp_quantity_bit.value(),
                    'values': self.items
                }
        }
        return bit_

    def btn_ok_clicked(self):
        self.signal.emit(signal_type('bit_enum', 'ok'))


class WidgetBool(QWidget):
    signal = pyqtSignal(signal_type)

    def __init__(self, type_='byte'):
        super().__init__()
        self.type_ = type_
        self.__create_widgets()
        self.cb_state.clicked.connect(self.changed_state)

    def __create_widgets(self):
        self.main_layout = QVBoxLayout()
        self.setLayout(self.main_layout)

        lable_name = QLabel('Name:')
        self.te_name = QTextEdit('Some bool name')
        self.te_name.setMaximumHeight(24)
        layout_name = QHBoxLayout()
        self.main_layout.addLayout(layout_name)
        layout_name.addWidget(lable_name)
        layout_name.addWidget(self.te_name)

        lable_cb = QLabel('Default state: ')
        self.cb_state = QCheckBox('Off')
        layout_state = QHBoxLayout()
        self.main_layout.addLayout(layout_state)
        layout_state.addWidget(lable_cb)
        layout_state.addWidget(self.cb_state)
        layout_state.addStretch(1)
        self.main_layout.addStretch(1)

        if self.type_ == 'bit':
            self.setWindowTitle('Add bit_bool')

            self.sb_bit_num = QSpinBox()
            self.sb_bit_num.setMaximum(7)
            self.sb_bit_num.setMinimumWidth(55)

            layout_bit = QHBoxLayout()
            self.main_layout.addLayout(layout_bit)
            layout_bit.addWidget(QLabel('Bit num: '))
            layout_bit.addWidget(self.sb_bit_num)
            layout_bit.addStretch(1)

            self.btn_ok = QPushButton('Ok')
            self.btn_ok.clicked.connect(self.btn_ok_clicked)

            self.btn_cancel = QPushButton('Cancel')
            self.btn_cancel.clicked.connect(self.close)

            layout_ok_cancel = QHBoxLayout()
            layout_ok_cancel.addWidget(self.btn_ok)
            layout_ok_cancel.addStretch(1)
            layout_ok_cancel.addWidget(self.btn_cancel)
            self.main_layout.addSpacing(50)
            self.main_layout.addLayout(layout_ok_cancel)

    def changed_state(self):
        if self.cb_state.isChecked():
            self.cb_state.setText('On')
        else:
            self.cb_state.setText('Off')

    def get_byte_item(self):
        byte_name = self.te_name.toPlainText()
        byte_ = {
            byte_name:
                {
                    'type': 'bool',
                    'def_state': self.cb_state.isChecked()
                }
        }
        return byte_

    def get_bit_item(self):
        bit_name = self.te_name.toPlainText()
        bit_ = {
            bit_name:
                {
                    'type': 'bit_bool',
                    'def_state': self.cb_state.isChecked(),
                    'bit_num': self.sb_bit_num.value()

                }
        }
        return bit_

    def btn_ok_clicked(self):
        self.signal.emit(signal_type('bit_bool', 'ok'))


class WidgetNum(QWidget):
    signal = pyqtSignal(signal_type)

    def __init__(self):
        super().__init__()
        self.__create_widgets()
        self.sb_step.valueChanged.connect(self.changed_step)
        self.sb_max.valueChanged.connect(self.changed_max)
        self.sb_min.valueChanged.connect(self.changed_min)

    def __create_widgets(self):
        self.main_layout = QGridLayout()
        self.setLayout(self.main_layout)

        lable_name = QLabel('Name:')
        self.te_name = QTextEdit('Some numeric name')
        self.te_name.setMaximumHeight(24)

        lable_sb_def = QLabel('Default: ')
        self.sb_def = QSpinBox()

        lable_sb_min = QLabel('Minimum: ')
        self.sb_min = QSpinBox()
        self.sb_min.setMaximum(0xFFFF)

        lable_sb_max = QLabel('Maximum: ')
        self.sb_max = QSpinBox()
        self.sb_max.setMaximum(0xFFFF)
        self.sb_max.setValue(0xFF)

        lable_sb_step = QLabel('Step: ')
        self.sb_step = QSpinBox()
        self.sb_step.setMinimum(1)

        self.main_layout.addWidget(lable_name, 0, 0)
        self.main_layout.addWidget(self.te_name, 0, 1)
        self.main_layout.addWidget(lable_sb_max, 1, 0)
        self.main_layout.addWidget(self.sb_max, 1, 1)
        self.main_layout.addWidget(lable_sb_min, 2, 0)
        self.main_layout.addWidget(self.sb_min, 2, 1)
        self.main_layout.addWidget(lable_sb_def, 3, 0)
        self.main_layout.addWidget(self.sb_def, 3, 1)
        self.main_layout.addWidget(lable_sb_step, 4, 0)
        self.main_layout.addWidget(self.sb_step, 4, 1)

    def changed_min(self):
        if self.sb_min.value() > (self.sb_max.value() - self.sb_step.value()):
            self.sb_max.setValue(self.sb_min.value() + self.sb_step.value())

        if self.sb_def.value() < self.sb_min.value():
            self.sb_def.setValue(self.sb_min.value())
        if self.sb_def.value() > self.sb_max.value():
            self.sb_def.setValue(self.sb_max.value())
        self.sb_def.setMinimum(self.sb_min.value())

    def changed_max(self):
        if self.sb_max.value() < (self.sb_min.value() + self.sb_step.value()):
            step = self.sb_max.value() - self.sb_min.value()
            if step >= 1:
                self.sb_step.setValue(step)
            else:
                self.sb_max.setValue(self.sb_min.value() + self.sb_step.value())
        if self.sb_def.value() < self.sb_min.value():
            self.sb_def.setValue(self.sb_min.value())
        if self.sb_def.value() > self.sb_max.value():
            self.sb_def.setValue(self.sb_max.value())
        self.sb_def.setMaximum(self.sb_max.value())

    def changed_step(self):
        if self.sb_step.value() > (self.sb_max.value() - self.sb_min.value()):
            self.sb_max.setValue(self.sb_min.value() + self.sb_step.value())

        if self.sb_def.value() < self.sb_min.value():
            self.sb_def.setValue(self.sb_min.value())
        if self.sb_def.value() > self.sb_max.value():
            self.sb_def.setValue(self.sb_max.value())
        self.sb_def.setSingleStep(self.sb_step.value())

    def get_byte_item(self):
        byte_name = self.te_name.toPlainText()
        byte_ = {
            byte_name:
                {
                    'type': 'num',
                    'def_value': self.sb_def.value(),
                    'min': self.sb_min.value(),
                    'max': self.sb_max.value(),
                    'step': self.sb_step.value(),
                }
        }
        return byte_


class WidgetBitField(QDialog):
    signal = pyqtSignal(signal_type)

    def __init__(self):
        super().__init__()
        self.byte_ = {}
        self.bit_enum = WidgetEnum('bit')
        self.bit_bool = WidgetBool('bit')
        # self.__create_widgets()
        self.main_layout = QVBoxLayout()
        self.setLayout(self.main_layout)

        add_layout = QHBoxLayout()
        self.te_byte_name = QTextEdit('Some bit field name')
        self.te_byte_name.setMaximumHeight(24)
        self.btn_create_byte = QPushButton('Create')
        self.btn_create_byte.setIcon(QIcon(r'icons/plus.svg'))
        self.btn_clear_byte = QPushButton('Clear')
        self.btn_clear_byte.setIcon(QIcon(r'icons/trash.svg'))

        add_layout.addWidget(QLabel('Name: '))
        add_layout.addWidget(self.te_byte_name)
        add_layout.addWidget(self.btn_create_byte)
        add_layout.addWidget(self.btn_clear_byte)

        self.cmdtree = QTreeView()
        self.model = QStandardItemModel()
        self.cmdtree.setModel(self.model)

        self.btn_add_bool = QPushButton('Add bool')
        self.btn_add_bool.setIcon(QIcon(r'icons/plus.svg'))
        self.btn_add_enum = QPushButton('Add enum')
        self.btn_add_enum.setIcon(QIcon(r'icons/plus.svg'))

        layout_2 = QHBoxLayout()
        layout_2.addWidget(self.btn_add_bool)
        layout_2.addWidget(self.btn_add_enum)
        layout_2.addStretch(1)

        self.btn_create_byte.clicked.connect(self.create_byte)
        self.btn_clear_byte.clicked.connect(self.remote_byte)
        self.btn_add_bool.clicked.connect(self.bit_bool.show)
        self.btn_add_enum.clicked.connect(self.bit_enum.show)
        self.bit_bool.signal.connect(self.add_item, Qt.QueuedConnection)
        self.bit_enum.signal.connect(self.add_item, Qt.QueuedConnection)

        self.main_layout.addLayout(add_layout)
        self.main_layout.addWidget(self.cmdtree)
        self.main_layout.addLayout(layout_2)

    def add_item(self, signal):
        if self.byte_ != {}:
            if signal.name == 'bit_bool':
                added_item = self.bit_bool.get_bit_item()
                self.bit_bool.close()
            elif signal.name == 'bit_enum':
                added_item = self.bit_enum.get_bit_item()
                self.bit_enum.close()
            self.byte_[self.byte_name]['description'].update(added_item)
            self.fill_tree()
        else:
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Information)
            msg.setWindowIcon(QIcon(r'icons/message-square.svg'))
            msg.setWindowTitle('Info')
            msg.setText('First, create a bit field.')
            msg.exec()

    def remote_byte(self):
        self.byte_ = {}
        self.model.clear()

    def create_byte(self):
        self.byte_name = self.te_byte_name.toPlainText()
        self.byte_ = {
            self.byte_name: {
                'type': 'bit_field',
                'description': {}
            }
        }
        self.fill_tree()

    def fill_tree(self):
        self.model.clear()
        byte_name_item = QStandardItem(self.byte_name)
        self.model.appendRow([byte_name_item, QStandardItem()])
        for bit_name, bit_description in self.byte_[self.byte_name]['description'].items():
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
        self.model.setHorizontalHeaderLabels(['Names', 'Values'])
        self.cmdtree.setColumnWidth(0, 250)
        self.cmdtree.expandToDepth(1)

    def get_byte_item(self):
        return self.byte_

if __name__ == '__main__':
    import sys
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    window = CmdViewerWidget()
    window.show()
    sys.exit(app.exec_())

