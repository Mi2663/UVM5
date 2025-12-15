import sys
import argparse
import json
from parser import parse_assembly
from encoder import encode_to_intermediate

def main():
    parser = argparse.ArgumentParser(
        description='Ассемблер УВМ (Вариант 5) - Этап 1: Промежуточное представление'
    )
    parser.add_argument('input', help='Путь к исходному файлу .asm')
    parser.add_argument('output', help='Путь к выходному файлу (.json для промежуточного представления)')
    parser.add_argument('--test', action='store_true', 
                       help='Режим тестирования: вывод промежуточного представления')
    
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
        
        # 4. Режим тестирования (вывод на экран)
        if args.test:
            print("\n=== ПРОМЕЖУТОЧНОЕ ПРЕДСТАВЛЕНИЕ ===")
            for i, instr in enumerate(intermediate):
                print(f"Инструкция {i} (строка {instr['line']}):")
                print(f"  Мнемоника: {instr['opcode']}")
                print(f"  Поле A: {instr['A']}")
                print(f"  Поле B: {instr['B']}")
                print(f"  Размер: {instr['size']} байт")
                print()
        
        # 5. Сохранение в JSON файл
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
        
        # 6. Проверка тестов из спецификации
        if args.test:
            print("\n=== ПРОВЕРКА ТЕСТОВ ИЗ СПЕЦИФИКАЦИИ ===")
            print("Ожидаемые значения из спецификации:")
            print("1. LOAD_CONST A=2, B=343")
            print("2. LOAD_MEM A=3, B=365") 
            print("3. STORE_MEM A=1, B=899")
            print("4. ROL A=4")
        
    except FileNotFoundError:
        print(f"Ошибка: файл '{args.input}' не найден", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Ошибка: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == '__main__':
    main()
