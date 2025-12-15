import sys
import argparse
import json
import os
from parser import parse_assembly
from encoder import encode_to_intermediate, encode_to_binary, decode_from_binary

def format_hex_dump(binary_data, bytes_per_line=16):
    """Форматирует бинарные данные в hex-дамп."""
    result = []
    for i in range(0, len(binary_data), bytes_per_line):
        chunk = binary_data[i:i + bytes_per_line]
        hex_str = ' '.join(f'{b:02X}' for b in chunk)
        result.append(hex_str)
    return '\n'.join(result)

def main():
    parser = argparse.ArgumentParser(
        description='Ассемблер УВМ (Вариант 5) - Этапы 1 и 2'
    )
    parser.add_argument('input', help='Путь к исходному файлу .asm')
    parser.add_argument('output', help='Путь к выходному файлу')
    parser.add_argument('--test', action='store_true', 
                       help='Режим тестирования: вывод промежуточного представления и бинарного кода')
    parser.add_argument('--stage', type=int, default=2, choices=[1, 2],
                       help='Этап работы: 1 - только промежуточное представление, 2 - бинарный код (по умолчанию)')
    
    args = parser.parse_args()
    
    try:
        # 1. Чтение исходного файла
        with open(args.input, 'r', encoding='utf-8') as f:
            source = f.read()
        
        # 2. Парсинг ассемблера
        print(f"Парсинг файла: {args.input}")
        program = parse_assembly(source)
        print(f"Найдено инструкций: {len(program)}")
        
        # 3. Преобразование в промежуточное представление
        intermediate = encode_to_intermediate(program)
        
        # 4. Режим тестирования (вывод промежуточного представления)
        if args.test or args.stage == 1:
            print("\n=== ПРОМЕЖУТОЧНОЕ ПРЕДСТАВЛЕНИЕ ===")
            for i, instr in enumerate(intermediate):
                print(f"Инструкция {i} (строка {instr['line']}):")
                print(f"  Мнемоника: {instr['opcode']}")
                print(f"  Поле A: {instr['A']}")
                print(f"  Поле B: {instr['B']}")
                print(f"  Размер: {instr['size']} байт")
                print()
        
        if args.stage == 1:
            # Сохраняем только промежуточное представление (JSON)
            output_dict = {
                'program': program,
                'intermediate': intermediate,
                'metadata': {
                    'source_file': args.input,
                    'instruction_count': len(program)
                }
            }
            
            with open(args.output, 'w', encoding='utf-8') as f:
                json.dump(output_dict, f, indent=2, ensure_ascii=False)
            
            print(f"Промежуточное представление сохранено в: {args.output}")
            return
        
        # 5. Кодирование в бинарный формат (Этап 2)
        binary = encode_to_binary(intermediate)
        
        # 6. Запись бинарного файла
        with open(args.output, 'wb') as f:
            f.write(binary)
        
        # 7. Вывод информации о размере
        print(f"\nРазмер бинарного файла: {len(binary)} байт")
        
        # 8. Режим тестирования (вывод бинарного кода)
        if args.test:
            print("\n=== БИНАРНЫЙ КОД (hex) ===")
            print(format_hex_dump(binary, bytes_per_line=4))
            
            print("\n=== БАЙТОВЫЙ ФОРМАТ (как в спецификации) ===")
            hex_bytes = [f'{b:02X}' for b in binary]
            print(", ".join(hex_bytes))
            
            # Проверка обратного декодирования
            try:
                decoded = decode_from_binary(binary)
                print("\n=== ПРОВЕРКА ОБРАТНОГО ДЕКОДИРОВАНИЯ ===")
                for i, instr in enumerate(decoded):
                    print(f"Инструкция {i}: A={instr['A']}, B={instr['B']}, {instr['opcode']}")
            except Exception as e:
                print(f"\nОшибка при обратном декодировании: {e}")
        
        # 9. Проверка тестов из спецификации
        if args.test:
            print("\n=== ОЖИДАЕМЫЕ ТЕСТЫ ИЗ СПЕЦИФИКАЦИИ ===")
            print("1. LOAD_CONST A=2, B=343 → ожидается: 0x4A, 0xB7")
            print("2. LOAD_MEM A=3, B=365 → ожидается: 0x60, 0x00, 0x01, 0x6D")
            print("3. STORE_MEM A=1, B=899 → ожидается: 0x2E, 0x03")
            print("4. ROL A=4 → ожидается: 0x80")
            
            # Создаем отдельные тестовые файлы для каждой команды
            print("\n=== ТЕСТИРОВАНИЕ КАЖДОЙ КОМАНДЫ ===")
            test_commands = [
                ("LOAD_CONST 343", "test_const.bin", [0x4A, 0xB7]),
                ("LOAD_MEM 365", "test_load.bin", [0x60, 0x00, 0x01, 0x6D]),
                ("STORE_MEM 899", "test_store.bin", [0x2E, 0x03]),
                ("ROL", "test_rol.bin", [0x80]),
            ]
            
            for asm_code, filename, expected_bytes in test_commands:
                try:
                    test_program = parse_assembly(asm_code)
                    test_intermediate = encode_to_intermediate(test_program)
                    test_binary = encode_to_binary(test_intermediate)
                    
                    actual_bytes = list(test_binary)
                    if actual_bytes == expected_bytes:
                        print(f"✓ {asm_code.split()[0]}: OK (получено: {[f'0x{b:02X}' for b in actual_bytes]})")
                    else:
                        print(f"✗ {asm_code.split()[0]}: ОШИБКА")
                        print(f"  Ожидалось: {[f'0x{b:02X}' for b in expected_bytes]}")
                        print(f"  Получено:  {[f'0x{b:02X}' for b in actual_bytes]}")
                except Exception as e:
                    print(f"✗ {asm_code.split()[0]}: ОШИБКА - {e}")
        
        print(f"\nБинарный файл сохранен: {args.output}")
        
    except FileNotFoundError:
        print(f"Ошибка: файл '{args.input}' не найден", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Ошибка: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == '__main__':
    main()
