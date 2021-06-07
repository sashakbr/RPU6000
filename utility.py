from collections import namedtuple
from PyQt5.QtWidgets import (
                                QDialog,
                                QDialogButtonBox,
                                QLabel,
                                QVBoxLayout,
                            )
from PyQt5.QtGui import QFont

signal_type = namedtuple('Signal', ['name', 'value'])
signal_cmd = namedtuple('CMD', ['name', 'value', 'position'])
signal_info = namedtuple('info', ['text', 'font'])


class CustomDialog(QDialog):
    def __init__(self, text: str, parent=None):
        super().__init__(parent=parent)

        self.setWindowTitle("Warning!")
        QBtn = QDialogButtonBox.Ok | QDialogButtonBox.Cancel

        self.buttonBox = QDialogButtonBox(QBtn)
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)

        self.layout = QVBoxLayout()
        message = QLabel(text)
        self.layout.addWidget(message)
        self.layout.addSpacing(20)
        self.layout.addWidget(self.buttonBox)
        self.setLayout(self.layout)


class SaveDialog(QDialog):
    def __init__(self, text: str, parent=None):
        super().__init__(parent=parent)

        self.setWindowTitle("Save changes")
        QBtn = QDialogButtonBox.Save | QDialogButtonBox.Close

        self.buttonBox = QDialogButtonBox(QBtn)
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)

        self.layout = QVBoxLayout()
        message = QLabel(text)
        self.layout.addWidget(message)
        self.layout.addSpacing(20)
        self.layout.addWidget(self.buttonBox)
        self.setLayout(self.layout)


def uint_to_bytes(number: int):
    """
    Перевод целых чисел в набор байт для случаев, когда число больше 255 (больше uint_8)
    :param number: int
    :return: bytes
    """
    return number.to_bytes(length=(7 + (number + (number == 0)).bit_length()) // 8,
                           byteorder='little',
                           signed=False)


def bytes_to_hex_string(data: bytes):
    res = ''
    for i, j in zip(data.hex()[::2], data.hex()[1::2]):
        res += i + j + ' '
    return res


def bit_change(value, num: int, state: bool):
    if state:
        return value | (1 << num)
    else:
        return value & ~(1 << num)


def get_bit_from_byte(byte_, position):
    mask = 1 << position
    return bool((mask & byte_) >> position)


def get_bits_from_byte(byte_, pos_start, quantity):
    mask = 0
    for i in range(pos_start, pos_start + quantity):
        mask += 1 << i
    return (mask & byte_) >> pos_start


def insert_item_to_dict(dict_: dict, position: int, items: dict):
    list_ = list(dict_.items())
    for item in list(items.items()):
        list_.insert(position, item)
        position += 1
    return dict(list_)


def cmd_parser(cmd: bytes, protocol: dict, command_num_position: int):
    if type(cmd) == bytes and len(cmd) != 0:
        res_str = ''
        command_num = cmd[command_num_position]
        parser_dict = {}
        for cmd_name, cmd_value in protocol.items():
            parser_dict.update({cmd_value['Command num']['def_value']: cmd_name})
        try:
            count = 0
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
        except KeyError:
            print(TypeError)
            return 'Unknown command!'
    else:
        return 'No response from device!'

def cmd_parser2(cmd: bytes, protocol: dict, cmd_num_position: int):
    if len(cmd) != 0:
        cmd_num = cmd[cmd_num_position]
        res_str = ''
        for cmd_name, cmd_body in protocol.items():
            if cmd_num == cmd_body['Command num']['def_value']:
                if cmd_num_position != 0:
                    print(list(cmd_body.items())[0])
                else:
                    pass
        return res_str


if __name__ == '__main__':
   # print(cmd_parser(b'\x00\x9e\x01\xaa\x00', commands, True))
   # print(bit_change(1, 1, True))
   #print(int_to_bool_list(3))
   #print(get_bit_from_int(0b01010010, 0))
   print(get_bits_from_byte(0b01010010, 2, 5))
   print(insert_item_to_dict({1: 2, 2: 3, 3: 4}, 1, {5: 6, 6: 7}))

