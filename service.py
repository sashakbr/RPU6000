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

commands = \
    {
        'Channel 1 power': {
            'Comand num':
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

    }