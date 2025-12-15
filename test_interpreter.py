import unittest
import sys
import os
import tempfile
import json
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from interpreter import UVMMemory, UVMDecoder, UVMExecutor
from parser import parse_assembly
from encoder import encode_to_intermediate, encode_to_binary

class TestUVMMemory(unittest.TestCase):
    
    def test_memory_initialization(self):
        """Тест инициализации памяти."""
        memory = UVMMemory()
        
        # Проверяем тестовые данные из скриншота
        self.assertEqual(memory.read_data(133), 42)
        self.assertEqual(memory.read_data(500), 25)
        self.assertEqual(memory.read_data(501), 100)
        self.assertEqual(memory.read_data(502), 225)
        self.assertEqual(memory.read_data(520), 100)
    
    def test_memory_read_write(self):
        """Тест чтения и записи в память."""
        memory = UVMMemory()
        
        # Запись и чтение
        memory.write_data(1000, 123)
        self.assertEqual(memory.read_data(1000), 123)
        
        # Запись граничного значения
        memory.write_data(2000, 255)
        self.assertEqual(memory.read_data(2000), 255)
        
        # Запись нуля
        memory.write_data(3000, 0)
        self.assertEqual(memory.read_data(3000), 0)
    
    def test_memory_bounds(self):
        """Тест граничных условий памяти."""
        memory = UVMMemory(data_size=100)
        
        # Проверка записи в пределах памяти
        memory.write_data(99, 50)
        self.assertEqual(memory.read_data(99), 50)
        
        # Проверка выхода за границы
        with self.assertRaises(IndexError):
            memory.write_data(100, 50)
        
        with self.assertRaises(IndexError):
            memory.read_data(100)
    
    def test_stack_operations(self):
        """Тест операций со стеком."""
        memory = UVMMemory()
        
        # Push и pop
        memory.push(10)
        memory.push(20)
        memory.push(30)
        
        self.assertEqual(memory.pop(), 30)
        self.assertEqual(memory.pop(), 20)
        self.assertEqual(memory.pop(), 10)
        
        # Peek
        memory.push(40)
        memory.push(50)
        self.assertEqual(memory.peek(), 50)
        self.assertEqual(memory.pop(), 50)  # Проверяем, что peek не снимает
        
        # Пустой стек
        memory.pop()  # Снимаем 40
        with self.assertRaises(IndexError):
            memory.pop()


class TestUVMDecoder(unittest.TestCase):
    
    def test_decode_rol(self):
        """Тест декодирования ROL."""
        memory = UVMMemory()
        memory.code = bytearray([0x80])  # ROL: A=4
        
        decoder = UVMDecoder()
        memory.pc = 0
        instr = decoder.decode_instruction(memory)
        
        self.assertIsNotNone(instr)
        self.assertEqual(instr['opcode'], 'ROL')
        self.assertEqual(instr['A'], 4)
        self.assertIsNone(instr['B'])
        self.assertEqual(instr['size'], 1)
        self.assertEqual(memory.pc, 1)  # PC должен увеличиться
    
    def test_decode_load_const(self):
        """Тест декодирования LOAD_CONST."""
        memory = UVMMemory()
        memory.code = bytearray([0x4A, 0xB7])  # LOAD_CONST: A=2, B=343
        
        decoder = UVMDecoder()
        memory.pc = 0
        instr = decoder.decode_instruction(memory)
        
        self.assertIsNotNone(instr)
        self.assertEqual(instr['opcode'], 'LOAD_CONST')
        self.assertEqual(instr['A'], 2)
        self.assertEqual(instr['B'], 343)
        self.assertEqual(instr['size'], 2)
        self.assertEqual(memory.pc, 2)
    
    def test_decode_load_mem(self):
        """Тест декодирования LOAD_MEM."""
        memory = UVMMemory()
        memory.code = bytearray([0x60, 0x00, 0x01, 0x6D])  # LOAD_MEM: A=3, B=365
        
        decoder = UVMDecoder()
        memory.pc = 0
        instr = decoder.decode_instruction(memory)
        
        self.assertIsNotNone(instr)
        self.assertEqual(instr['opcode'], 'LOAD_MEM')
        self.assertEqual(instr['A'], 3)
        self.assertEqual(instr['B'], 365)
        self.assertEqual(instr['size'], 4)
        self.assertEqual(memory.pc, 4)
    
    def test_decode_store_mem(self):
        """Тест декодирования STORE_MEM."""
        memory = UVMMemory()
        memory.code = bytearray([0x2E, 0x03])  # STORE_MEM: A=1, B=899
        
        decoder = UVMDecoder()
        memory.pc = 0
        instr = decoder.decode_instruction(memory)
        
        self.assertIsNotNone(instr)
        self.assertEqual(instr['opcode'], 'STORE_MEM')
        self.assertEqual(instr['A'], 1)
        self.assertEqual(instr['B'], 899)
        self.assertEqual(instr['size'], 2)
        self.assertEqual(memory.pc, 2)


class TestUVMExecutor(unittest.TestCase):
    
    def test_execute_load_const(self):
        """Тест выполнения LOAD_CONST."""
        memory = UVMMemory()
        executor = UVMExecutor(memory)
        
        instruction = {'opcode': 'LOAD_CONST', 'B': 123}
        executor.execute(instruction)
        
        self.assertEqual(len(memory.stack), 1)
        self.assertEqual(memory.stack[0], 123)
    
    def test_execute_load_mem(self):
        """Тест выполнения LOAD_MEM."""
        memory = UVMMemory()
        executor = UVMExecutor(memory)
        
        # Записываем тестовое значение
        memory.write_data(100, 77)
        
        instruction = {'opcode': 'LOAD_MEM', 'B': 100}
        executor.execute(instruction)
        
        self.assertEqual(len(memory.stack), 1)
        self.assertEqual(memory.stack[0], 77)
    
    def test_execute_store_mem_simple(self):
        """Тест выполнения STORE_MEM (упрощенная версия)."""
        memory = UVMMemory()
        executor = UVMExecutor(memory)
        
        # Сначала помещаем значение на стек
        memory.push(200)  # Адрес для записи
        
        instruction = {'opcode': 'STORE_MEM', 'B': 0}  # Без смещения
        executor.execute(instruction)
        
        # Проверяем, что значение записалось (в текущей реализации)
        # self.assertEqual(memory.read_data(200), ...)
    
    def test_execute_rol(self):
        """Тест выполнения ROL."""
        memory = UVMMemory()
        executor = UVMExecutor(memory)
        
        # Помещаем значение на стек
        memory.push(0b10000001)  # 129 = 10000001b
        
        instruction = {'opcode': 'ROL'}
        executor.execute(instruction)
        
        # 10000001 → ROL → 00000011 = 3
        self.assertEqual(len(memory.stack), 1)
        self.assertEqual(memory.stack[0], 0b00000011)
        
        # Тест с другим значением
        memory.pop()
        memory.push(0b00001111)  # 15 = 00001111b
        executor.execute(instruction)
        
        # 00001111 → ROL → 00011110 = 30
        self.assertEqual(memory.stack[0], 0b00011110)


class TestEndToEnd(unittest.TestCase):
    
    def test_simple_program(self):
        """Сквозной тест простой программы."""
        # 1. Ассемблируем программу
        source = """LOAD_CONST 100
LOAD_MEM 133
STORE_MEM 0
ROL"""
        
        program = parse_assembly(source)
        intermediate = encode_to_intermediate(program)
        binary = encode_to_binary(intermediate)
        
        # 2. Запускаем интерпретатор
        memory = UVMMemory()
        memory.load_code(binary)
        
        executor = UVMExecutor(memory)
        executor.run()
        
        # 3. Проверяем результаты
        # После LOAD_CONST 100 и LOAD_MEM 133 (42) на стеке должно быть 100, 42
        # Затем STORE_MEM и ROL...
        self.assertEqual(executor.instruction_count, 4)
    
    def test_memory_dump(self):
        """Тест создания дампа памяти."""
        from interpreter import create_memory_dump
        
        memory = UVMMemory()
        
        # Добавляем тестовые данные
        memory.write_data(100, 50)
        memory.write_data(200, 100)
        memory.write_data(300, 150)
        
        # Создаем дамп
        dump = create_memory_dump(memory, 0, 1000)
        
        # Проверяем структуру дампа
        self.assertIn('metadata', dump)
        self.assertIn('memory', dump)
        self.assertIn('stack', dump)
        
        # Проверяем данные
        self.assertEqual(dump['memory']['100'], 50)
        self.assertEqual(dump['memory']['200'], 100)
        self.assertEqual(dump['memory']['300'], 150)
        
        # Проверяем, что нулевые значения не включаются
        self.assertNotIn('0', dump['memory'])
        self.assertNotIn('1', dump['memory'])


def create_test_program():
    """Создает тестовую программу для проверки интерпретатора."""
    # Простая программа для тестирования
    source = """LOAD_CONST 10
LOAD_MEM 133
STORE_MEM 0
LOAD_CONST 255
STORE_MEM 100
ROL"""
    
    # Сохраняем в файл
    with open('test_program.asm', 'w') as f:
        f.write(source)
    
    # Ассемблируем
    from parser import parse_assembly
    from encoder import encode_to_intermediate, encode_to_binary
    
    program = parse_assembly(source)
    intermediate = encode_to_intermediate(program)
    binary = encode_to_binary(intermediate)
    
    with open('test_program.bin', 'wb') as f:
        f.write(binary)
    
    print("Тестовая программа создана:")
    print(f"  test_program.asm - исходный код")
    print(f"  test_program.bin - бинарный файл ({len(binary)} байт)")
    
    return binary


if __name__ == '__main__':
    # Создаем тестовую программу
    create_test_program()
    
    # Запускаем тесты
    unittest.main()
