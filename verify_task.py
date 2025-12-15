#!/usr/bin/env python3
"""
Скрипт для проверки выполнения тестовой задачи Этапа 5.
"""

import os
import subprocess
import json
import sys

def run_assembler_and_interpreter(asm_file, json_file, start_addr=0, end_addr=1000):
    """Запускает ассемблер и интерпретатор для программы."""
    
    # Генерируем имя бинарного файла
    bin_file = asm_file.replace('.asm', '.bin')
    
    # 1. Ассемблирование
    print(f"  Ассемблирование {asm_file}...")
    result = subprocess.run(
        ['python', 'main.py', asm_file, bin_file],
        capture_output=True,
        text=True
    )
    
    if result.returncode != 0:
        print(f"    Ошибка ассемблирования: {result.stderr}")
        return None
    
    # 2. Выполнение интерпретатором
    print(f"  Выполнение программы...")
    result = subprocess.run(
        ['python', 'interpreter.py', bin_file, json_file, 
         '--start', str(start_addr), '--end', str(end_addr)],
        capture_output=True,
        text=True
    )
    
    if result.returncode != 0:
        print(f"    Ошибка выполнения: {result.stderr}")
        return None
    
    # 3. Загрузка дампа памяти
    try:
        with open(json_file, 'r') as f:
            dump = json.load(f)
        return dump
    except Exception as e:
        print(f"    Ошибка чтения дампа: {e}")
        return None

def verify_example_1(dump):
    """Проверка первого примера из test_task.asm."""
    print("\n  ПРИМЕР 1: Базовый тест с векторами")
    
    expected = {
        '100': 129,  # Исходные данные
        '101': 204,
        '102': 170,
        '103': 240,
        '104': 15,
        '200': 1,    # Количество сдвигов
        '201': 2,
        '202': 3,
        '203': 0,
        '204': 4,
        '300': 3,    # Результаты ROL
        '301': 51,
        '302': 85,
        '303': 240,
        '304': 240
    }
    
    all_correct = True
    for addr, expected_value in expected.items():
        if addr in dump['memory']:
            actual = dump['memory'][addr]
            if actual == expected_value:
                print(f"    MEM[{addr}] = {actual} ✓")
            else:
                print(f"    MEM[{addr}] = {actual} ✗ (ожидалось {expected_value})")
                all_correct = False
        else:
            print(f"    MEM[{addr}] не найден ✗")
            all_correct = False
    
    return all_correct

def verify_example_2(dump):
    """Проверка второго примера из test_task.asm."""
    print("\n  ПРИМЕР 2: Все элементы с одинаковым сдвигом")
    
    # Ожидаемые результаты ROL с shift=1:
    # 85 (01010101) ROL 1 = 170 (10101010)
    # 51 (00110011) ROL 1 = 102 (01100110) - но 51 ROL 1 = 102? Проверим: 00110011 → 01100110 = 102 ✓
    # 15 (00001111) ROL 1 = 30 (00011110)
    # 255 (11111111) ROL 1 = 255 (11111111)
    # 1 (00000001) ROL 1 = 2 (00000010)
    
    expected = {
        '400': 85,   # Исходные данные
        '401': 51,
        '402': 15,
        '403': 255,
        '404': 1,
        '500': 1,    # Количество сдвигов (все 1)
        '501': 1,
        '502': 1,
        '503': 1,
        '504': 1,
        '600': 170,  # Результаты
        '601': 102,
        '602': 30,
        '603': 255,
        '604': 2
    }
    
    all_correct = True
    for addr in ['600', '601', '602', '603', '604']:
        if addr in dump['memory']:
            actual = dump['memory'][addr]
            expected_val = expected.get(addr, 0)
            if actual == expected_val:
                print(f"    MEM[{addr}] = {actual} ✓")
            else:
                print(f"    MEM[{addr}] = {actual} ✗ (ожидалось {expected_val})")
                all_correct = False
        else:
            print(f"    MEM[{addr}] не найден ✗")
            all_correct = False
    
    return all_correct

def verify_example_3(dump):
    """Проверка третьего примера из test_task.asm."""
    print("\n  ПРИМЕР 3: Граничные случаи")
    
    # Ожидаемые результаты:
    # 1 ROL 7 = 128 (00000001 → 10000000)
    # 128 ROL 15 (15 mod 8 = 7) = 1 (10000000 → 00000001)
    # 255 ROL 0 = 255 (не меняется)
    # 0 ROL 8 = 0 (не меняется)
    # 85 ROL 1 = 170
    
    expected = {
        '900': 128,  # 1 ROL 7
        '901': 1,    # 128 ROL 7 (15 mod 8 = 7)
        '902': 255,  # 255 ROL 0
        '903': 0,    # 0 ROL 8
        '904': 170   # 85 ROL 1
    }
    
    all_correct = True
    for addr, expected_value in expected.items():
        if addr in dump['memory']:
            actual = dump['memory'][addr]
            if actual == expected_value:
                print(f"    MEM[{addr}] = {actual} ✓")
            else:
                print(f"    MEM[{addr}] = {actual} ✗ (ожидалось {expected_value})")
                all_correct = False
        else:
            print(f"    MEM[{addr}] не найден ✗")
            all_correct = False
    
    return all_correct

def verify_calc_demo(dump):
    """Проверка демонстрационной программы с вычислениями."""
    print("\n  ДЕМОНСТРАЦИЯ ВЫЧИСЛЕНИЙ:")
    
    # Проверяем ключевые результаты
    checkpoints = [
        ('13', 64, "1 ROL 1 ROL 2 ROL 3 = 64"),
        ('31', 170, "85 ROL 1 = 170"),
        ('32', 85, "85 ROL 2 = 85 (симметрия)"),
        ('33', 85, "85 ROL 4 = 85 (симметрия)"),
        ('70', 60, "15 ROL 2 = 60"),
        ('71', 60, "60 ROL 4 = 60 (после маскировки)"),
        ('72', 15, "240 ROL 6 = 15")
    ]
    
    all_correct = True
    for addr, expected, description in checkpoints:
        if addr in dump['memory']:
            actual = dump['memory'][addr]
            if actual == expected:
                print(f"    {description}: MEM[{addr}] = {actual} ✓")
            else:
                print(f"    {description}: MEM[{addr}] = {actual} ✗ (ожидалось {expected})")
                all_correct = False
        else:
            print(f"    {description}: MEM[{addr}] не найден ✗")
            all_correct = False
    
    return all_correct

def main():
    print("=" * 70)
    print("ПРОВЕРКА ТЕСТОВОЙ ЗАДАЧИ ЭТАПА 5")
    print("=" * 70)
    
    # Очистка старых файлов
    for ext in ['.bin', '.json']:
        for file in ['test_task', 'calc_demo']:
            filename = file + ext
            if os.path.exists(filename):
                os.remove(filename)
    
    all_tests_passed = True
    
    # 1. Проверка основной тестовой задачи
    print("\n1. ОСНОВНАЯ ТЕСТОВАЯ ЗАДАЧА (test_task.asm)")
    print("-" * 70)
    
    if not os.path.exists('test_task.asm'):
        print("  Файл test_task.asm не найден!")
        return 1
    
    dump = run_assembler_and_interpreter(
        'test_task.asm', 
        'test_task_dump.json',
        start_addr=0,
        end_addr=1000
    )
    
    if dump:
        # Проверяем все три примера
        ex1_ok = verify_example_1(dump)
        ex2_ok = verify_example_2(dump)
        ex3_ok = verify_example_3(dump)
        
        if ex1_ok and ex2_ok and ex3_ok:
            print("\n  ✅ ВСЕ ПРИМЕРЫ ТЕСТОВОЙ ЗАДАЧИ ВЫПОЛНЕНЫ КОРРЕКТНО")
        else:
            print("\n  ❌ НЕКОТОРЫЕ ПРИМЕРЫ ИМЕЮТ ОШИБКИ")
            all_tests_passed = False
        
        # Показываем информацию о стеке
        if dump['stack']:
            print(f"\n  Состояние стека после выполнения: {dump['stack']}")
            print(f"  На стеке результатов: {len(dump['stack'])} значений")
    else:
        all_tests_passed = False
    
    # 2. Проверка демонстрационной программы с вычислениями
    print("\n\n2. ДЕМОНСТРАЦИОННАЯ ПРОГРАММА С ВЫЧИСЛЕНИЯМИ (calc_demo.asm)")
    print("-" * 70)
    
    if not os.path.exists('calc_demo.asm'):
        print("  Файл calc_demo.asm не найден!")
        return 1
    
    dump2 = run_assembler_and_interpreter(
        'calc_demo.asm',
        'calc_demo_dump.json',
        start_addr=0,
        end_addr=200
    )
    
    if dump2:
        calc_ok = verify_calc_demo(dump2)
        
        if calc_ok:
            print("\n  ✅ ВЫЧИСЛЕНИЯ ВЫПОЛНЕНЫ КОРРЕКТНО")
        else:
            print("\n  ❌ НЕКОТОРЫЕ ВЫЧИСЛЕНИЯ НЕВЕРНЫ")
            all_tests_passed = False
        
        # Показываем стек
        if dump2['stack']:
            print(f"\n  Состояние стека: {dump2['stack']}")
    else:
        all_tests_passed = False
    
    # 3. Сводка результатов
    print("\n" + "=" * 70)
    print("СВОДКА РЕЗУЛЬТАТОВ")
    print("=" * 70)
    
    if all_tests_passed:
        print("\n✅ ТЕСТОВАЯ ЗАДАЧА ЭТАПА 5 ВЫПОЛНЕНА УСПЕШНО!")
        print("\nРеализовано:")
        print("1. Программа для поэлементного ROL над двумя векторами длины 5")
        print("2. Три различных примера программ с вычислениями")
        print("3. Все дампы памяти соответствуют требованиям задачи")
        print("4. Результаты проверены автоматически")
    else:
        print("\n❌ ТЕСТОВАЯ ЗАДАЧА ИМЕЕТ ОШИБКИ")
    
    # 4. Очистка временных файлов
    print("\n" + "-" * 70)
    print("ОЧИСТКА ВРЕМЕННЫХ ФАЙЛОВ")
    print("-" * 70)
    
    temp_files = [
        'test_task.bin', 'test_task_dump.json',
        'calc_demo.bin', 'calc_demo_dump.json'
    ]
    
    for file in temp_files:
        if os.path.exists(file):
            os.remove(file)
            print(f"  Удален: {file}")
    
    print("\n" + "=" * 70)
    return 0 if all_tests_passed else 1

if __name__ == '__main__':
    sys.exit(main())
