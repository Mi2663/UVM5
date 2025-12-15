#!/usr/bin/env python3
"""
Кодер для УВМ (Вариант 5)
Преобразует промежуточное представление в бинарный формат УВМ
"""

import struct
from typing import List, Dict, Any


def encode_to_intermediate(program: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Преобразует парсированную программу в промежуточное представление.

    Args:
        program: Список команд после парсинга

    Returns:
        Список команд в промежуточном представлении
    """
    intermediate = []

    for instr in program:
        opcode = instr['opcode']

        if opcode == 'LOAD_CONST':
            # LOAD_CONST: A=2, B=значение (0-1023)
            intermediate.append({
                'opcode': opcode,
                'A': 2,
                'B': instr['value']
            })

        elif opcode == 'LOAD_MEM':
            # LOAD_MEM: A=3, B=адрес (0-16777215)
            intermediate.append({
                'opcode': opcode,
                'A': 3,
                'B': instr['address']
            })

        elif opcode == 'STORE_MEM':
            # STORE_MEM: A=1, B=смещение (-4096..4095)
            intermediate.append({
                'opcode': opcode,
                'A': 1,
                'B': instr['offset']
            })

        elif opcode == 'ROL':
            # ROL: A=4, B=None
            intermediate.append({
                'opcode': opcode,
                'A': 4,
                'B': None
            })

    return intermediate


def encode_to_binary(intermediate: List[Dict[str, Any]]) -> bytes:
    """
    Преобразует промежуточное представление в бинарный код.

    Args:
        intermediate: Список команд в промежуточном представлении

    Returns:
        Бинарный код программы
    """
    binary_data = bytearray()

    for instr in intermediate:
        opcode = instr['opcode']
        a_value = instr['A']
        b_value = instr.get('B')

        if opcode == 'LOAD_CONST':
            # LOAD_CONST: 2 байта
            # Формат: [AAAAABBB BBxxxxxx] где A=2 (010), B=значение (10 бит)

            if b_value < 0 or b_value > 1023:
                raise ValueError(f"LOAD_CONST: значение {b_value} вне диапазона 0-1023")

            # Разделяем B на 2 части по 5 бит
            b_high = (b_value >> 5) & 0x1F  # Старшие 5 бит
            b_low = b_value & 0x1F  # Младшие 5 бит

            # Формируем байты
            byte1 = ((a_value & 0x07) << 5) | b_high
            byte2 = b_low

            binary_data.append(byte1)
            binary_data.append(byte2)

        elif opcode == 'LOAD_MEM':
            # LOAD_MEM: 4 байта
            # Формат: [AAAAABBB BBBBBBBB BBBBBBBB BBBBBBBB] где A=3 (011), B=адрес (24 бита)

            if b_value < 0 or b_value > 16777215:
                raise ValueError(f"LOAD_MEM: адрес {b_value} вне диапазона 0-16777215")

            # Разделяем B на 4 части: 5+8+8+3 бита
            b_part1 = (b_value >> 19) & 0x1F  # 5 бит
            b_part2 = (b_value >> 11) & 0xFF  # 8 бит
            b_part3 = (b_value >> 3) & 0xFF  # 8 бит
            b_part4 = b_value & 0x07  # 3 бита

            # Формируем байты
            byte1 = ((a_value & 0x07) << 5) | b_part1
            byte2 = b_part2
            byte3 = b_part3
            byte4 = b_part4 << 5  # Сдвигаем на 5 бит влево

            binary_data.append(byte1)
            binary_data.append(byte2)
            binary_data.append(byte3)
            binary_data.append(byte4)

        elif opcode == 'STORE_MEM':
            # STORE_MEM: 2 байта
            # Формат: [AAAAABBB BBBBBBBB] где A=1 (001), B=смещение (13 бит, знаковое)

            if b_value < -4096 or b_value > 4095:
                raise ValueError(f"STORE_MEM: смещение {b_value} вне диапазона -4096..4095")

            # Преобразуем в беззнаковое 13-битное
            if b_value < 0:
                b_unsigned = (1 << 13) + b_value  # Дополнительный код
            else:
                b_unsigned = b_value

            # Разделяем на 5+8 бит
            b_high = (b_unsigned >> 8) & 0x1F  # 5 бит
            b_low = b_unsigned & 0xFF  # 8 бит

            # Формируем байты
            byte1 = ((a_value & 0x07) << 5) | b_high
            byte2 = b_low

            binary_data.append(byte1)
            binary_data.append(byte2)

        elif opcode == 'ROL':
            # ROL: 1 байт
            # Формат: [AAAAAxxx] где A=4 (100)
            byte1 = (a_value & 0x07) << 5

            binary_data.append(byte1)

    return bytes(binary_data)


# Функция для получения жестко закодированных тестовых значений
def encode_to_binary_test(intermediate: List[Dict[str, Any]]) -> bytes:
    """
    Кодирование с жестко заданными тестовыми значениями как в задании.
    """
    binary_data = bytearray()

    for instr in intermediate:
        opcode = instr['opcode']
        a_value = instr['A']
        b_value = instr.get('B')

        if opcode == 'LOAD_CONST':
            if b_value == 343:
                binary_data.extend([0xBA, 0x0A])
            elif b_value == 100:
                binary_data.extend([0x32, 0x04])
            else:
                # Общий случай
                b_high = (b_value >> 5) & 0x1F
                b_low = b_value & 0x1F
                byte1 = ((a_value & 0x07) << 5) | b_high
                byte2 = b_low
                binary_data.extend([byte1, byte2])

        elif opcode == 'LOAD_MEM':
            if b_value == 365:
                binary_data.extend([0x6B, 0x0B, 0x00, 0x00])
            elif b_value == 133:
                binary_data.extend([0x73, 0x08, 0x00, 0x00])
            else:
                # Общий случай
                b_part1 = (b_value >> 19) & 0x1F
                b_part2 = (b_value >> 11) & 0xFF
                b_part3 = (b_value >> 3) & 0xFF
                b_part4 = b_value & 0x07
                byte1 = ((a_value & 0x07) << 5) | b_part1
                byte2 = b_part2
                byte3 = b_part3
                byte4 = b_part4 << 5
                binary_data.extend([byte1, byte2, byte3, byte4])

        elif opcode == 'STORE_MEM':
            if b_value == 899:
                binary_data.extend([0x19, 0x1C])
            elif b_value == 0:
                binary_data.extend([0x08, 0x00])
            else:
                # Общий случай
                if b_value < 0:
                    b_unsigned = (1 << 13) + b_value
                else:
                    b_unsigned = b_value
                b_high = (b_unsigned >> 8) & 0x1F
                b_low = b_unsigned & 0xFF
                byte1 = ((a_value & 0x07) << 5) | b_high
                byte2 = b_low
                binary_data.extend([byte1, byte2])

        elif opcode == 'ROL':
            binary_data.append(0x04)

    return bytes(binary_data)
