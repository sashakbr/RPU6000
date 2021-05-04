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
