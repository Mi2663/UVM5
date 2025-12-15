import unittest
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from parser import parse_assembly
from encoder import encode_to_intermediate, encode_to_binary, decode_from_binary

class TestBinaryEncoding(unittest.TestCase):
    
    def test_rol_encoding(self):
        """Тестирование кодирования ROL"""
        source = "ROL"
        program = parse_assembly(source)
        intermediate = encode_to_intermediate(program)
        binary = encode_to_binary(intermediate)
        
        # ROL: A=4 → 0b100 << 5 = 0b10000000 = 0x80
        self.assertEqual(len(binary), 1)
        self.assertEqual(binary[0], 0x80)
        
        # Проверка обратного декодирования
        decoded = decode_from_binary(binary)
        self.assertEqual(len(decoded), 1)
        self.assertEqual(decoded[0]['A'], 4)
        self.assertEqual(decoded[0]['opcode'], 'ROL')
    
    def test_load_const_encoding(self):
        """Тестирование кодирования LOAD_CONST"""
        source = "LOAD_CONST 343"  # 343 = 0x157
        program = parse_assembly(source)
        intermediate = encode_to_intermediate(program)
        binary = encode_to_binary(intermediate)
        
        # LOAD_CONST: A=2, B=343
        # 343 = 0x157 = 0b0101010111
        # A=2 = 0b010
        # Байт1: A<<5 = 0b01000000 | (B>>5 & 0x1F) = 0b0101010 = 0x4A
        # Байт2: B & 0x1F = 0b10111 = 0x17
        self.assertEqual(len(binary), 2)
        self.assertEqual(binary[0], 0x4A)  # Ожидается 0x4A
        self.assertEqual(binary[1], 0x17)  # Ожидается 0xB7? Проверим
        
        # Пересчитаем: 343 = 0x157
        # Старшие 5 бит: 0x157 >> 5 = 0x2A >> 5? Подожди, пересчитаем
        # 343 в бинарном: 0101010111
        # Старшие 5 бит: 01010 (0x0A)
        # Байт1: A=010, + старшие 5 бит B=01010 → 01001010 = 0x4A ✓
        # Младшие 5 бит: 10111 (0x17) ✓
        
        # Проверка обратного декодирования
        decoded = decode_from_binary(binary)
        self.assertEqual(len(decoded), 1)
        self.assertEqual(decoded[0]['A'], 2)
        self.assertEqual(decoded[0]['B'], 343)
        self.assertEqual(decoded[0]['opcode'], 'LOAD_CONST')
    
    def test_store_mem_encoding(self):
        """Тестирование кодирования STORE_MEM"""
        source = "STORE_MEM 899"  # 899 = 0x383
        program = parse_assembly(source)
        intermediate = encode_to_intermediate(program)
        binary = encode_to_binary(intermediate)
        
        # STORE_MEM: A=1, B=899 (положительное)
        # 899 = 0x383 = 0b01110000011
        # A=1 = 0b001
        # Байт1: A<<5 = 0b00100000 | (B>>8 & 0x1F) = 0b00101110 = 0x2E
        # Байт2: B & 0xFF = 0x83 = 0b10000011
        self.assertEqual(len(binary), 2)
        self.assertEqual(binary[0], 0x2E)
        self.assertEqual(binary[1], 0x83)
        
        # Проверка обратного декодирования
        decoded = decode_from_binary(binary)
        self.assertEqual(len(decoded), 1)
        self.assertEqual(decoded[0]['A'], 1)
        self.assertEqual(decoded[0]['B'], 899)
        self.assertEqual(decoded[0]['opcode'], 'STORE_MEM')
    
    def test_store_mem_negative_encoding(self):
        """Тестирование кодирования STORE_MEM с отрицательным смещением"""
        source = "STORE_MEM -100"
        program = parse_assembly(source)
        intermediate = encode_to_intermediate(program)
        binary = encode_to_binary(intermediate)
        
        # Проверка обратного декодирования
        decoded = decode_from_binary(binary)
        self.assertEqual(len(decoded), 1)
        self.assertEqual(decoded[0]['A'], 1)
        self.assertEqual(decoded[0]['B'], -100)
        self.assertEqual(decoded[0]['opcode'], 'STORE_MEM')
    
    def test_load_mem_encoding(self):
        """Тестирование кодирования LOAD_MEM"""
        source = "LOAD_MEM 365"  # 365 = 0x16D
        program = parse_assembly(source)
        intermediate = encode_to_intermediate(program)
        binary = encode_to_binary(intermediate)
        
        # LOAD_MEM: A=3, B=365
        # 365 = 0x16D = 0b00000000000000000101101101
        # A=3 = 0b011
        # Байт1: A<<5 = 0b01100000 | (B>>19 & 0x1F) = 0b01100000 = 0x60
        # Байт2: (B>>11) & 0xFF = 0x00
        # Байт3: (B>>3) & 0xFF = 0x01 (365>>3=45, 0x2D? Проверим)
        # Байт4: (B & 0x07) << 5 = 0x6D? Подожди, пересчитаем
        
        # Давайте посчитаем аккуратно:
        # 365 в двоичном: 0000 0000 0000 0000 0001 0110 1101
        # Разбиваем на байты согласно формату:
        # Байт1: A=011 + старшие 5 бит B: 00000 → 01100000 = 0x60 ✓
        # Байт2: следующие 8 бит: 00000000 = 0x00 ✓
        # Байт3: следующие 8 бит: 00000001 = 0x01 ✓
        # Байт4: младшие 3 бита: 101 (0x5) сдвиг на 5: 10100000 = 0xA0? 
        # Но в спецификации ожидается 0x6D... Давай проверим другой расчет
        
        # По спецификации из скриншота ожидается: 0x60, 0x00, 0x01, 0x6D
        # Значит наш расчет неверен. Пересчитаем по формуле из encode_to_binary:
        
        self.assertEqual(len(binary), 4)
        # Проверим по ожидаемым значениям из спецификации
        expected_bytes = [0x60, 0x00, 0x01, 0x6D]
        for i, (actual, expected) in enumerate(zip(binary, expected_bytes)):
            self.assertEqual(actual, expected, f"Байт {i}: ожидалось 0x{expected:02X}, получено 0x{actual:02X}")
        
        # Проверка обратного декодирования
        decoded = decode_from_binary(binary)
        self.assertEqual(len(decoded), 1)
        self.assertEqual(decoded[0]['A'], 3)
        self.assertEqual(decoded[0]['B'], 365)
        self.assertEqual(decoded[0]['opcode'], 'LOAD_MEM')
    
    def test_full_program_encoding(self):
        """Тестирование кодирования полной программы"""
        source = """LOAD_CONST 343
LOAD_MEM 365
STORE_MEM 899
ROL"""
        
        program = parse_assembly(source)
        intermediate = encode_to_intermediate(program)
        binary = encode_to_binary(intermediate)
        
        # Проверяем размер
        expected_size = 2 + 4 + 2 + 1  # 9 байт
        self.assertEqual(len(binary), expected_size)
        
        # Проверяем обратное декодирование
        decoded = decode_from_binary(binary)
        self.assertEqual(len(decoded), 4)
        
        # Проверяем команды
        self.assertEqual(decoded[0]['opcode'], 'LOAD_CONST')
        self.assertEqual(decoded[0]['B'], 343)
        
        self.assertEqual(decoded[1]['opcode'], 'LOAD_MEM')
        self.assertEqual(decoded[1]['B'], 365)
        
        self.assertEqual(decoded[2]['opcode'], 'STORE_MEM')
        self.assertEqual(decoded[2]['B'], 899)
        
        self.assertEqual(decoded[3]['opcode'], 'ROL')

if __name__ == '__main__':
    unittest.main()
