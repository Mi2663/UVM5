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
