import unittest
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from parser import parse_assembly

class TestParser(unittest.TestCase):
    
    def test_empty_program(self):
        """Парсинг пустой программы"""
        source = ""
        program = parse_assembly(source)
        self.assertEqual(len(program), 0)
        
        source = "; Комментарий\n\n  \n; Еще комментарий"
        program = parse_assembly(source)
        self.assertEqual(len(program), 0)
    
    def test_comments(self):
        """Парсинг строк с комментариями"""
        source = "LOAD_CONST 100 ; Загрузить константу"
        program = parse_assembly(source)
        self.assertEqual(len(program), 1)
        self.assertEqual(program[0]['opcode'], 'LOAD_CONST')
        self.assertEqual(program[0]['operand'], 100)
    
    def test_case_insensitive(self):
        """Проверка нечувствительности к регистру"""
        source = "load_const 100\nLoad_Mem 200\nstore_mem 300\nrol"
        program = parse_assembly(source)
        self.assertEqual(len(program), 4)
        self.assertEqual(program[0]['opcode'], 'LOAD_CONST')
        self.assertEqual(program[1]['opcode'], 'LOAD_MEM')
        self.assertEqual(program[2]['opcode'], 'STORE_MEM')
        self.assertEqual(program[3]['opcode'], 'ROL')
    
    def test_whitespace(self):
        """Проверка обработки пробелов"""
        source = "  LOAD_CONST   100   "
        program = parse_assembly(source)
        self.assertEqual(len(program), 1)
        self.assertEqual(program[0]['opcode'], 'LOAD_CONST')
        self.assertEqual(program[0]['operand'], 100)
    
    def test_multiple_instructions(self):
        """Парсинг нескольких инструкций"""
        source = """LOAD_CONST 10
LOAD_MEM 20
STORE_MEM 30
ROL"""
        program = parse_assembly(source)
        self.assertEqual(len(program), 4)
        self.assertEqual(program[0]['line'], 1)
        self.assertEqual(program[1]['line'], 2)
        self.assertEqual(program[2]['line'], 3)
        self.assertEqual(program[3]['line'], 4)
    
    def test_invalid_opcode(self):
        """Проверка обработки неверной команды"""
        source = "INVALID 100"
        with self.assertRaises(ValueError):
            parse_assembly(source)
    
    def test_rol_with_operand_warning(self):
        """Проверка предупреждения для ROL с операндом"""
        source = "ROL 100"
        program = parse_assembly(source)
        self.assertEqual(len(program), 1)
        self.assertEqual(program[0]['opcode'], 'ROL')

if __name__ == '__main__':
    unittest.main()
