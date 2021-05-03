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
                    # count += 1
                else:
                    res_str += str(cmd[count]) + '\r'
            elif description['type'] == 'bit_field':
                for bit_name, bit_description in description['description'].items():
                    if bit_description['type'] == 'bit_bool':



            count += 1
        return res_str


commands = \
    {
        'Channel 1 power': {
            'Command num':
                {
                    'type': 'const_num',
                    'def_value': 0x9E,
                },
            'Power':
                {
                    'type': 'enum',
                    'values': {'Off': 0, 'On': 1}
                },
            'Freq':
                {
                    'type': 'num',
                    'def_value': 100,
                    'min': 30,
                    'max': 6000,
                    'step': 10,
                },

        },

        'Preselector power channels': {
            'Command num':
                {
                    'type': 'const_num',
                    'def_value': 0x0E,
                },
            'Power':
                {
                    'type': 'enum',
                    'values': {'Turn off both channels': 0, 'Turn on 1': 1, 'Turn on 2': 2, 'Turn on both channels': 3}
                },
        },

    }

if __name__ == '__main__':
   # print(cmd_parser(b'\x00\x9e\x01\xaa\x00', commands, True))
    print(bit_change(1, 1, True))

