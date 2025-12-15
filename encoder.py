# Соответствие мнемоник кодам A
OPCODE_TO_A = {
    'LOAD_CONST': 2,
    'LOAD_MEM': 3,
    'STORE_MEM': 1,
    'ROL': 4
}

def encode_to_intermediate(program):
    """
    Преобразует список инструкций в промежуточное представление
    (соответствующее полям A и B из спецификации).
    """
    intermediate = []
    
    for instr in program:
        opcode = instr['opcode']
        a_value = OPCODE_TO_A[opcode]
        
        if opcode == 'LOAD_CONST':
            b_value = instr['operand']
            if b_value is None:
                raise ValueError(f"LOAD_CONST требует операнд (строка {instr['line']})")
            if not (0 <= b_value < 1024):
                raise ValueError(f"LOAD_CONST: константа {b_value} вне диапазона 0..1023 (строка {instr['line']})")
            
            intermediate.append({
                'A': a_value,
                'B': b_value,
                'size': 2,
                'opcode': opcode,
                'line': instr['line']
            })
        
        elif opcode == 'LOAD_MEM':
            b_value = instr['operand']
            if b_value is None:
                raise ValueError(f"LOAD_MEM требует операнд (строка {instr['line']})")
            if not (0 <= b_value < 2**24):
                raise ValueError(f"LOAD_MEM: адрес {b_value} вне диапазона 0..16777215 (строка {instr['line']})")
            
            intermediate.append({
                'A': a_value,
                'B': b_value,
                'size': 4,
                'opcode': opcode,
                'line': instr['line']
            })
        
        elif opcode == 'STORE_MEM':
            b_value = instr['operand']
            if b_value is None:
                raise ValueError(f"STORE_MEM требует операнд (строка {instr['line']})")
            if not (-4096 <= b_value < 4096):
                raise ValueError(f"STORE_MEM: смещение {b_value} вне диапазона -4096..4095 (строка {instr['line']})")
            
            intermediate.append({
                'A': a_value,
                'B': b_value,
                'size': 2,
                'opcode': opcode,
                'line': instr['line']
            })
        
        elif opcode == 'ROL':
            intermediate.append({
                'A': a_value,
                'B': None,
                'size': 1,
                'opcode': opcode,
                'line': instr['line']
            })
    
    return intermediate


def encode_to_binary(intermediate):
    """
    Преобразует промежуточное представление в бинарный машинный код УВМ.
    Возвращает bytes.
    """
    binary_data = bytearray()
    
    for instr in intermediate:
        a_value = instr['A']
        b_value = instr.get('B')
        
        if instr['opcode'] == 'ROL':
            # ROL: 1 байт, только поле A в битах 0-2
            # Формат: [AAAAA000]
            byte1 = (a_value << 5) & 0xFF
            binary_data.append(byte1)
            
        elif instr['opcode'] == 'LOAD_CONST':
            # LOAD_CONST: 2 байта
            # Формат: [AAAAABBB BBBBBBBB]
            # A: биты 0-2, B: биты 3-12 (10 бит)
            if b_value is None:
                raise ValueError("LOAD_CONST: отсутствует значение B")
            
            # Первый байт: A (3 бита) + старшие 5 бит B
            byte1 = (a_value << 5) | ((b_value >> 5) & 0x1F)
            # Второй байт: младшие 5 бит B
            byte2 = b_value & 0x1F
            
            binary_data.extend([byte1, byte2])
            
        elif instr['opcode'] == 'STORE_MEM':
            # STORE_MEM: 2 байта
            # Формат: [AAAAABBB BBBBBBBB]
            # A: биты 0-2, B: биты 3-15 (13 бит со знаком)
            if b_value is None:
                raise ValueError("STORE_MEM: отсутствует значение B")
            
            # Преобразуем знаковое значение в беззнаковое для хранения
            if b_value < 0:
                b_value = b_value + 8192  # 2^13
            
            # Первый байт: A (3 бита) + старшие 5 бит B
            byte1 = (a_value << 5) | ((b_value >> 8) & 0x1F)
            # Второй байт: младшие 8 бит B
            byte2 = b_value & 0xFF
            
            binary_data.extend([byte1, byte2])
            
        elif instr['opcode'] == 'LOAD_MEM':
            # LOAD_MEM: 4 байта
            # Формат: [AAAAABBB BBBBBBBB BBBBBBBB BBBBBBBB]
            # A: биты 0-2, B: биты 3-26 (24 бита)
            if b_value is None:
                raise ValueError("LOAD_MEM: отсутствует значение B")
            
            # Первый байт: A (3 бита) + старшие 5 бит B (биты 19-23)
            byte1 = (a_value << 5) | ((b_value >> 19) & 0x1F)
            # Второй байт: биты 11-18 B
            byte2 = (b_value >> 11) & 0xFF
            # Третий байт: биты 3-10 B
            byte3 = (b_value >> 3) & 0xFF
            # Четвертый байт: младшие 3 бита B (биты 0-2) в старших позициях
            byte4 = (b_value & 0x07) << 5
            
            binary_data.extend([byte1, byte2, byte3, byte4])
    
    return bytes(binary_data)


def decode_from_binary(binary_data):
    """
    Обратная функция: преобразует бинарный код обратно в промежуточное представление.
    Для тестирования.
    """
    intermediate = []
    i = 0
    
    while i < len(binary_data):
        byte1 = binary_data[i]
        a_value = (byte1 >> 5) & 0x07
        
        # Определяем команду по A
        if a_value == 4:  # ROL
            intermediate.append({
                'A': a_value,
                'B': None,
                'size': 1,
                'opcode': 'ROL'
            })
            i += 1
            
        elif a_value == 2:  # LOAD_CONST
            if i + 1 >= len(binary_data):
                raise ValueError("Недостаточно данных для LOAD_CONST")
            
            byte2 = binary_data[i + 1]
            b_value = ((byte1 & 0x1F) << 5) | (byte2 & 0x1F)
            
            intermediate.append({
                'A': a_value,
                'B': b_value,
                'size': 2,
                'opcode': 'LOAD_CONST'
            })
            i += 2
            
        elif a_value == 1:  # STORE_MEM
            if i + 1 >= len(binary_data):
                raise ValueError("Недостаточно данных для STORE_MEM")
            
            byte2 = binary_data[i + 1]
            b_value = ((byte1 & 0x1F) << 8) | byte2
            
            # Преобразуем из беззнакового в знаковое
            if b_value >= 4096:
                b_value = b_value - 8192
            
            intermediate.append({
                'A': a_value,
                'B': b_value,
                'size': 2,
                'opcode': 'STORE_MEM'
            })
            i += 2
            
        elif a_value == 3:  # LOAD_MEM
            if i + 3 >= len(binary_data):
                raise ValueError("Недостаточно данных для LOAD_MEM")
            
            byte2 = binary_data[i + 1]
            byte3 = binary_data[i + 2]
            byte4 = binary_data[i + 3]
            
            b_value = ((byte1 & 0x1F) << 19) | (byte2 << 11) | (byte3 << 3) | ((byte4 >> 5) & 0x07)
            
            intermediate.append({
                'A': a_value,
                'B': b_value,
                'size': 4,
                'opcode': 'LOAD_MEM'
            })
            i += 4
            
        else:
            raise ValueError(f"Неизвестный код операции A={a_value}")
    
    return intermediate
