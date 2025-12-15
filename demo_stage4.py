#!/usr/bin/env python3
"""
Демонстрационный скрипт для Этапа 4.
Показывает работу команды ROL (циклический сдвиг влево).
"""

import os
import subprocess
import json

def run_command(cmd, description):
    """Выполняет команду и выводит описание."""
    print(f"\n{'='*60}")
    print(f"{description}")
    print(f"{'='*60}")
    print(f"Команда: {cmd}")
    
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    
    if result.stdout:
        print(f"Вывод:\n{result.stdout}")
    
    if result.stderr and result.returncode != 0:
        print(f"Ошибка:\n{result.stderr}")
    
    return result.returncode == 0

def main():
    print("ДЕМОНСТРАЦИЯ ЭТАПА 4: РЕАЛИЗАЦИЯ АЛУ (ЦИКЛИЧЕСКИЙ СДВИГ ROL)")
    print("=" * 60)
    
    # 1. Тестируем демонстрационную программу ROL
    print("\n1. Тестирование демонстрационной программы ROL")
    
    if not os.path.exists("rol_demo.asm"):
        print("Создаем демонстрационную программу...")
        with open("rol_demo.asm", "w") as f:
            f.write("""LOAD_CONST 129
LOAD_CONST 1000
ROL
STORE_MEM 2000
LOAD_MEM 2000""")
    
    # Создаем тестовые данные в памяти
    # (количество сдвигов = 1 по адресу 1000)
    
    success = run_command(
        "python main.py rol_demo.asm rol_demo.bin",
        "Ассемблирование демонстрационной программы"
    )
    
    if not success:
        return 1
    
    # 2. Запускаем интерпретатор
    success = run_command(
        "python interpreter.py rol_demo.bin rol_dump.json --start 1000 --end 2010",
        "Выполнение программы с командой ROL"
    )
    
    if not success:
        return 1
    
    # 3. Проверяем результаты
    print(f"\n{'='*60}")
    print("РЕЗУЛЬТАТЫ ВЫПОЛНЕНИЯ ROL")
    print(f"{'='*60}")
    
    if os.path.exists("rol_dump.json"):
        with open("rol_dump.json", 'r') as f:
            dump = json.load(f)
        
        print("Содержимое памяти после выполнения:")
        for addr, value in sorted(dump['memory'].items(), key=lambda x: int(x[0])):
            print(f"  MEM[{addr}] = {value} ({bin(value)})")
        
        if dump['stack']:
            print(f"\nСостояние стека: {dump['stack']}")
            result = dump['stack'][-1]
            print(f"Результат ROL на вершине стека: {result}")
            print(f"  Десятичное: {result}")
            print(f"  Двоичное: {bin(result)}")
            print(f"  Шестнадцатеричное: 0x{result:02X}")
            
            # Проверяем корректность
            # 129 (0b10000001) ROL 1 = 3 (0b00000011)
            expected = 3
            if result == expected:
                print(f"\n✅ РЕЗУЛЬТАТ КОРРЕКТНЫЙ: {result} == {expected}")
            else:
                print(f"\n❌ ОШИБКА: ожидалось {expected}, получено {result}")
    
    # 4. Тестируем программу для поэлементного ROL над векторами
    print(f"\n{'='*60}")
    print("2. ТЕСТИРОВАНИЕ ПОЭЛЕМЕНТНОГО ROL НАД ВЕКТОРАМИ")
    print(f"{'='*60}")
    
    if not os.path.exists("vector_rol.asm"):
        print("Файл vector_rol.asm не найден")
        print("Создайте его с программой из Этапа 4")
    else:
        success = run_command(
            "python main.py vector_rol.asm vector_rol.bin",
            "Ассемблирование программы vector_rol.asm"
        )
        
        if success:
            success = run_command(
                "python interpreter.py vector_rol.bin vector_dump.json --start 300 --end 510",
                "Выполнение программы с поэлементным ROL"
            )
            
            if success and os.path.exists("vector_dump.json"):
                with open("vector_dump.json", 'r') as f:
                    dump = json.load(f)
                
                print("\nРезультаты поэлементного ROL:")
                print("Вектор результатов (адреса 500-504):")
                for addr in ['500', '501', '502', '503', '504']:
                    if addr in dump['memory']:
                        value = dump['memory'][addr]
                        print(f"  MEM[{addr}] = {value} ({bin(value)})")
                
                # Ожидаемые результаты
                expected = {
                    '500': 3,    # 129 ROL 1
                    '501': 51,   # 204 ROL 2
                    '502': 85,   # 170 ROL 3
                    '503': 240,  # 240 ROL 0
                    '504': 240   # 15 ROL 4
                }
                
                print("\nПроверка результатов:")
                all_correct = True
                for addr, exp_value in expected.items():
                    if addr in dump['memory']:
                        actual = dump['memory'][addr]
                        if actual == exp_value:
                            print(f"  MEM[{addr}] = {actual} ✓")
                        else:
                            print(f"  MEM[{addr}] = {actual} ✗ (ожидалось {exp_value})")
                            all_correct = False
                    else:
                        print(f"  MEM[{addr}] не найден в дампе ✗")
                        all_correct = False
                
                if all_correct:
                    print("\n✅ ВСЕ РЕЗУЛЬТАТЫ КОРРЕКТНЫ!")
                else:
                    print("\n❌ НЕКОТОРЫЕ РЕЗУЛЬТАТЫ НЕВЕРНЫ")
    
    # 5. Запускаем unit-тесты АЛУ
    print(f"\n{'='*60}")
    print("3. ЗАПУСК UNIT-ТЕСТОВ АЛУ")
    print(f"{'='*60}")
    
    run_command(
        "python test_alu.py",
        "Тестирование реализации команды ROL"
    )
    
    # 6. Очистка временных файлов
    print(f"\n{'='*60}")
    print("4. ОЧИСТКА ВРЕМЕННЫХ ФАЙЛОВ")
    print(f"{'='*60}")
    
    temp_files = [
        'rol_demo.bin', 'rol_dump.json',
        'vector_rol.bin', 'vector_dump.json'
    ]
    
    for file in temp_files:
        if os.path.exists(file):
            os.remove(file)
            print(f"Удален: {file}")
    
    print("\n✅ Демонстрация Этапа 4 завершена успешно!")
    print("\nРеализовано:")
    print("✓ Команда ROL (циклический сдвиг влево)")
    print("✓ Поддержка чтения количества сдвигов из памяти")
    print("✓ Сохранение результатов в память для проверки")
    print("✓ Тестовая программа с поэлементным ROL над векторами")
    print("✓ Unit-тесты для проверки корректности")
    
    return 0

if __name__ == '__main__':
    exit(main())
