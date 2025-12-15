import unittest
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from parser import parse_assembly
from encoder import encode_to_intermediate, encode_to_binary
from interpreter import UVMMemory, UVMExecutor

class TestALUROL(unittest.TestCase):
    """Тесты для команды ROL (АЛУ)."""
    
    def test_rol_single_shift(self):
        """Тест ROL с одним сдвигом."""
        # Создаем программу на ассемблере
        source = """LOAD_CONST 129    ; 0b10000001
LOAD_CONST 1000   ; Адрес с количеством сдвигов
ROL"""
        
        # Ассемблируем
        program = parse_assembly(source)
        intermediate = encode_to_intermediate(program)
        binary = encode_to_binary(intermediate)
        
        # Запускаем интерпретатор
        memory = UVMMemory()
        memory.write_data(1000, 1)  # Количество сдвигов = 1
        memory.load_code(binary)
        
        executor = UVMExecutor(memory)
        executor.run()
        
        # Проверяем результат
        # 0b10000001 (129) → ROL на 1 бит → 0b00000011 (3)
        self.assertEqual(len(memory.stack), 1)
        self.assertEqual(memory.stack[0], 3)
    
    def test_rol_two_shifts(self):
        """Тест ROL с двумя сдвигами."""
        source = """LOAD_CONST 204    ; 0b11001100
LOAD_CONST 1000
ROL"""
        
        program = parse_assembly(source)
        intermediate = encode_to_intermediate(program)
        binary = encode_to_binary(intermediate)
        
        memory = UVMMemory()
        memory.write_data(1000, 2)  # 2 сдвига
        memory.load_code(binary)
        
        executor = UVMExecutor(memory)
        executor.run()
        
        # 0b11001100 (204) → ROL на 2 бита → 0b00110011 (51)
        self.assertEqual(memory.stack[0], 51)
    
    def test_rol_full_rotation(self):
        """Тест ROL с полным оборотом (8 сдвигов)."""
        source = """LOAD_CONST 240    ; 0b11110000
LOAD_CONST 1000
ROL"""
        
        program = parse_assembly(source)
        intermediate = encode_to_intermediate(program)
        binary = encode_to_binary(intermediate)
        
        memory = UVMMemory()
        memory.write_data(1000, 8)  # 8 сдвигов
        memory.load_code(binary)
        
        executor = UVMExecutor(memory)
        executor.run()
        
        # После 8 сдвигов значение должно вернуться к исходному
        self.assertEqual(memory.stack[0], 240)
    
    def test_rol_zero_shifts(self):
        """Тест ROL с нулевым количеством сдвигов."""
        source = """LOAD_CONST 85     ; 0b01010101
LOAD_CONST 1000
ROL"""
        
        program = parse_assembly(source)
        intermediate = encode_to_intermediate(program)
        binary = encode_to_binary(intermediate)
        
        memory = UVMMemory()
        memory.write_data(1000, 0)  # 0 сдвигов
        memory.load_code(binary)
        
        executor = UVMExecutor(memory)
        executor.run()
        
        # При 0 сдвигов значение не должно измениться
        self.assertEqual(memory.stack[0], 85)
    
    def test_rol_chain(self):
        """Тест последовательных ROL операций."""
        source = """LOAD_CONST 15     ; 0b00001111
LOAD_CONST 1000
ROL
LOAD_CONST 1001
ROL"""
        
        program = parse_assembly(source)
        intermediate = encode_to_intermediate(program)
        binary = encode_to_binary(intermediate)
        
        memory = UVMMemory()
        memory.write_data(1000, 2)  # Первый ROL: 2 сдвига
        memory.write_data(1001, 2)  # Второй ROL: еще 2 сдвига
        memory.load_code(binary)
        
        executor = UVMExecutor(memory)
        executor.run()
        
        # 0b00001111 (15) → ROL(2) → 0b00111100 (60)
        # 0b00111100 (60) → ROL(2) → 0b11110000 (240)
        self.assertEqual(memory.stack[0], 240)
    
    def test_rol_with_store(self):
        """Тест ROL с сохранением результата в память."""
        source = """LOAD_CONST 170    ; 0b10101010
LOAD_CONST 1000
ROL
STORE_MEM 2000"""
        
        program = parse_assembly(source)
        intermediate = encode_to_intermediate(program)
        binary = encode_to_binary(intermediate)
        
        memory = UVMMemory()
        memory.write_data(1000, 3)  # 3 сдвига
        memory.load_code(binary)
        
        executor = UVMExecutor(memory)
        executor.run()
        
        # Проверяем, что результат сохранился в память
        # 0b10101010 (170) → ROL на 3 бита → 0b01010101 (85)
        result = memory.read_data(2000)
        self.assertEqual(result, 85)
    
    def test_vector_rol_program(self):
        """Тест полной программы для поэлементного ROL над векторами."""
        # Загружаем программу из файла
        with open('vector_rol.asm', 'r') as f:
            source = f.read()
        
        program = parse_assembly(source)
        intermediate = encode_to_intermediate(program)
        binary = encode_to_binary(intermediate)
        
        # Запускаем интерпретатор
        memory = UVMMemory()
        memory.load_code(binary)
        
        executor = UVMExecutor(memory)
        executor.run()
        
        # Проверяем результаты
        expected_results = [
            3,   # 129 ROL 1 = 3
            51,  # 204 ROL 2 = 51
            85,  # 170 ROL 3 = 85
            240, # 240 ROL 0 = 240 (не изменилось)
            240  # 15 ROL 4 = 240
        ]
        
        actual_results = [
            memory.read_data(500),
            memory.read_data(501),
            memory.read_data(502),
            memory.read_data(503),
            memory.read_data(504)
        ]
        
        for i, (expected, actual) in enumerate(zip(expected_results, actual_results)):
            self.assertEqual(actual, expected, f"Элемент {i}: ожидалось {expected}, получено {actual}")
        
        # Проверяем, что на стеке лежат результаты чтения
        self.assertEqual(len(memory.stack), 5)
        
        # Последний результат на стеке должен быть 240
        self.assertEqual(memory.stack[-1], 240)


def run_alu_demo():
    """Демонстрация работы АЛУ (ROL)."""
    print("=" * 60)
    print("ДЕМОНСТРАЦИЯ РАБОТЫ АЛУ: КОМАНДА ROL")
    print("=" * 60)
    
    # Тест 1: Простой ROL
    print("\n1. Тест простого ROL:")
    print("   Значение: 0b10000001 (129)")
    print("   Сдвигов: 1")
    print("   Ожидаемый результат: 0b00000011 (3)")
    
    memory = UVMMemory()
    memory.write_data(1000, 1)
    memory.push(129)
    memory.push(1000)
    
    executor = UVMExecutor(memory)
    executor.execute({'opcode': 'ROL'})
    
    print(f"   Полученный результат: {memory.stack[0]} ({bin(memory.stack[0])})")
    
    # Тест 2: Несколько тестов
    test_cases = [
        (0b11001100, 2, 0b00110011, 51),   # 204 → 2 сдвига → 51
        (0b10101010, 3, 0b01010101, 85),   # 170 → 3 сдвига → 85
        (0b11110000, 8, 0b11110000, 240),  # 240 → 8 сдвигов → 240
        (0b00001111, 4, 0b11110000, 240),  # 15 → 4 сдвига → 240
    ]
    
    print("\n2. Дополнительные тесты:")
    for i, (value, shifts, expected_bin, expected_dec) in enumerate(test_cases, 1):
        memory = UVMMemory()
        memory.write_data(1000, shifts)
        memory.push(value)
        memory.push(1000)
        
        executor = UVMExecutor(memory)
        executor.execute({'opcode': 'ROL'})
        
        result = memory.stack[0]
        status = "✓" if result == expected_dec else "✗"
        print(f"   Тест {i}: {value} ROL {shifts} = {result} {status}")
        if result != expected_dec:
            print(f"     Ожидалось: {expected_dec} ({bin(expected_bin)})")
            print(f"     Получено:  {result} ({bin(result)})")
    
    print("\n" + "=" * 60)
    print("Демонстрация завершена!")
    print("=" * 60)


if __name__ == '__main__':
    # Запускаем демонстрацию
    run_alu_demo()
    
    # Запускаем тесты
    print("\n\nЗапуск unit-тестов АЛУ...")
    unittest.main(argv=['first-arg-is-ignored'], exit=False)
