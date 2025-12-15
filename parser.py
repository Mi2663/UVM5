import re

def parse_assembly(source):
    """
    Парсит исходный текст ассемблера в список инструкций.
    """
    lines = source.split('\n')
    program = []
    
    for line_num, line in enumerate(lines, start=1):
        line = line.strip()
        
        # Пропускаем пустые строки и комментарии
        if not line or line.startswith(';'):
            continue
        
        # Убираем комментарий в конце строки
        if ';' in line:
            line = line.split(';')[0].strip()
        
        # Разбиваем на мнемонику и операнд
        parts = re.split(r'\s+', line, maxsplit=1)
        opcode = parts[0].upper()
        
        # Проверяем поддерживаемые мнемоники
        valid_opcodes = ['LOAD_CONST', 'LOAD_MEM', 'STORE_MEM', 'ROL']
        if opcode not in valid_opcodes:
            raise ValueError(f"Строка {line_num}: неизвестная команда '{opcode}'")
        
        # Обработка операндов
        operand = None
        if opcode in ['LOAD_CONST', 'LOAD_MEM', 'STORE_MEM']:
            if len(parts) < 2:
                raise ValueError(f"Строка {line_num}: отсутствует операнд для '{opcode}'")
            
            try:
                operand = int(parts[1].strip())
            except ValueError:
                raise ValueError(f"Строка {line_num}: неверный операнд '{parts[1]}'")
        
        # Для ROL операнда нет
        elif opcode == 'ROL':
            if len(parts) > 1:
                print(f"Предупреждение: строка {line_num}: команда ROL не принимает операндов")
        
        program.append({
            'opcode': opcode,
            'operand': operand,
            'line': line_num,
            'original': line
        })
    
    return program
