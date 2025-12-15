import unittest
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from parser import parse_assembly
from encoder import encode_to_intermediate, OPCODE_TO_A

class TestEncoder(unittest.TestCase):
    
    def test_opcode_mapping(self):
        """Проверка соответствия мнемоник кодам A"""
        self.assertEqual(OPCODE_TO_A['LOAD_CONST'], 2)
        self.assertEqual(OPCODE_TO_A['LOAD_MEM'], 3)
        self.assertEqual(OPCODE_TO_A['STORE_MEM'], 1)
        self.assertEqual(OPCODE_TO_A['ROL'], 4)
    
    def test_encode_spec_test(self):
        """Кодирование тестовой программы из спецификации"""
        source = """LOAD_CONST 343
LOAD_MEM 365
STORE_MEM 899
ROL"""
        
        program = parse_assembly(source)
        intermediate = encode_to_intermediate(program)
        
        # Проверяем количество инструкций
        self.assertEqual(len(intermediate), 4)
        
        # Проверяем LOAD_CONST
        self.assertEqual(intermediate[0]['opcode'], 'LOAD_CONST')
        self.assertEqual(intermediate[0]['A'], 2)
        self.assertEqual(intermediate[0]['B'], 343)
        self.assertEqual(intermediate[0]['size'], 2)
        
        # Проверяем LOAD_MEM
        self.assertEqual(intermediate[1]['opcode'], 'LOAD_MEM')
        self.assertEqual(intermediate[1]['A'], 3)
        self.assertEqual(intermediate[1]['B'], 365)
        self.assertEqual(intermediate[1]['size'], 4)
        
        # Проверяем STORE_MEM
        self.assertEqual(intermediate[2]['opcode'], 'STORE_MEM')
        self.assertEqual(intermediate[2]['A'], 1)
        self.assertEqual(intermediate[2]['B'], 899)
        self.assertEqual(intermediate[2]['size'], 2)
        
        # Проверяем ROL
        self.assertEqual(intermediate[3]['opcode'], 'ROL')
        self.assertEqual(intermediate[3]['A'], 4)
        self.assertIsNone(intermediate[3]['B'])
        self.assertEqual(intermediate[3]['size'], 1)
    
    def test_range_validation(self):
        """Проверка валидации диапазонов"""
        # LOAD_CONST вне диапазона
        source = "LOAD_CONST 2000"
        program = parse_assembly(source)
        with self.assertRaises(ValueError):
            encode_to_intermediate(program)
        
        # LOAD_MEM вне диапазона
        source = "LOAD_MEM 20000000"
        program = parse_assembly(source)
        with self.assertRaises(ValueError):
            encode_to_intermediate(program)
        
        # STORE_MEM вне диапазона
        source = "STORE_MEM 5000"
        program = parse_assembly(source)
        with self.assertRaises(ValueError):
            encode_to_intermediate(program)
    
    def test_missing_operand(self):
        """Проверка обработки отсутствия операнда"""
        source = "LOAD_CONST"
        program = parse_assembly(source)
        with self.assertRaises(ValueError):
            encode_to_intermediate(program)

if __name__ == '__main__':
    unittest.main()
