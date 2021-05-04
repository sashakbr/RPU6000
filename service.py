from collections import namedtuple

signal_type = namedtuple('Signal', ['name', 'value'])


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


def get_bit_from_byte(byte_, position):
    mask = 1 << position
    return bool((mask & byte_) >> position)


def get_bits_from_byte(byte_, pos_start, quantity):
    mask = 0
    for i in range(pos_start, pos_start + quantity):
        mask += 1 << i
    return (mask & byte_) >> pos_start

if __name__ == '__main__':
   # print(cmd_parser(b'\x00\x9e\x01\xaa\x00', commands, True))
   # print(bit_change(1, 1, True))
   #print(int_to_bool_list(3))
   #print(get_bit_from_int(0b01010010, 0))
   print(get_bits_from_byte(0b01010010, 2, 5))
