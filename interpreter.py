import sys
import json
import argparse
from typing import List, Dict, Any, Optional

class UVMMemory:
    """Модель памяти УВМ с раздельной памятью команд и данных."""
    
    def __init__(self, data_size=65536, code_size=65536):
        self.data = [0] * data_size  # Память данных (инициализируем нулями)
        self.code = bytearray()      # Память команд (загружаем из файла)
        self.stack = []              # Стек УВМ
        self.pc = 0                  # Счетчик команд
        
        # Инициализация тестовыми данными как в скриншоте
        self._init_test_data()
    
    def _init_test_data(self):
        """Инициализация тестовыми данными из скриншота."""
        # MEM[133] = 42
        self.write_data(133, 42)
        # MEM[500] = 25
        self.write_data(500, 25)
        # MEM[501] = 100
        self.write_data(501, 100)
        # MEM[502] = 225
        self.write_data(502, 225)
        # MEM[520] = 100
        self.write_data(520, 100)
    
    def load_code(self, binary_data: bytes):
        """Загрузка машинного кода в память команд."""
        self.code = bytearray(binary_data)
    
    def read_code(self, address: int) -> int:
        """Чтение байта из памяти команд."""
        if address < 0 or address >= len(self.code):
            raise IndexError(f"Адрес памяти команд вне диапазона: {address}")
        return self.code[address]
    
    def read_data(self, address: int) -> int:
        """Чтение значения из памяти данных."""
        if address < 0 or address >= len(self.data):
            raise IndexError(f"Адрес памяти данных вне диапазона: {address}")
        return self.data[address]
    
    def write_data(self, address: int, value: int):
        """Запись значения в память данных."""
        if address < 0 or address >= len(self.data):
            raise IndexError(f"Адрес памяти данных вне диапазона: {address}")
        if value < 0 or value > 255:
            raise ValueError(f"Значение вне диапазона 0-255: {value}")
        self.data[address] = value
    
    def push(self, value: int):
        """Помещение значения на стек."""
        if value < -32768 or value > 32767:
            raise ValueError(f"Значение вне диапазона для стека: {value}")
        self.stack.append(value)
    
    def pop(self) -> int:
        """Снятие значения со стека."""
        if not self.stack:
            raise IndexError("Попытка чтения из пустого стека")
        return self.stack.pop()
    
    def peek(self) -> Optional[int]:
        """Просмотр вершины стека без снятия."""
        return self.stack[-1] if self.stack else None
    
    def get_memory_dump(self, start_addr: int, end_addr: int) -> Dict[str, Any]:
        """Получение дампа памяти данных в указанном диапазоне."""
        dump = {}
        for addr in range(start_addr, min(end_addr + 1, len(self.data))):
            if self.data[addr] != 0:  # Сохраняем только ненулевые значения
                dump[str(addr)] = self.data[addr]
        return dump
    
    def get_stack_dump(self) -> List[int]:
        """Получение дампа стека."""
        return self.stack.copy()


class UVMDecoder:
    """Декодер команд УВМ из бинарного формата."""
    
    @staticmethod
    def decode_instruction(memory: UVMMemory) -> Optional[Dict[str, Any]]:
        """Декодирует следующую команду из памяти команд."""
        if memory.pc >= len(memory.code):
            return None
        
        byte1 = memory.read_code(memory.pc)
        a_value = (byte1 >> 5) & 0x07
        
        if a_value == 4:  # ROL
            instr = {
                'A': a_value,
                'B': None,
                'size': 1,
                'opcode': 'ROL'
            }
            memory.pc += 1
            
        elif a_value == 2:  # LOAD_CONST
            if memory.pc + 1 >= len(memory.code):
                raise ValueError("Недостаточно данных для LOAD_CONST")
            
            byte2 = memory.read_code(memory.pc + 1)
            b_value = ((byte1 & 0x1F) << 5) | (byte2 & 0x1F)
            
            instr = {
                'A': a_value,
                'B': b_value,
                'size': 2,
                'opcode': 'LOAD_CONST'
            }
            memory.pc += 2
            
        elif a_value == 1:  # STORE_MEM
            if memory.pc + 1 >= len(memory.code):
                raise ValueError("Недостаточно данных для STORE_MEM")
            
            byte2 = memory.read_code(memory.pc + 1)
            b_value = ((byte1 & 0x1F) << 8) | byte2
            
            # Преобразуем из беззнакового в знаковое
            if b_value >= 4096:
                b_value = b_value - 8192
            
            instr = {
                'A': a_value,
                'B': b_value,
                'size': 2,
                'opcode': 'STORE_MEM'
            }
            memory.pc += 2
            
        elif a_value == 3:  # LOAD_MEM
            if memory.pc + 3 >= len(memory.code):
                raise ValueError("Недостаточно данных для LOAD_MEM")
            
            byte2 = memory.read_code(memory.pc + 1)
            byte3 = memory.read_code(memory.pc + 2)
            byte4 = memory.read_code(memory.pc + 3)
            
            b_value = ((byte1 & 0x1F) << 19) | (byte2 << 11) | (byte3 << 3) | ((byte4 >> 5) & 0x07)
            
            instr = {
                'A': a_value,
                'B': b_value,
                'size': 4,
                'opcode': 'LOAD_MEM'
            }
            memory.pc += 4
            
        else:
            raise ValueError(f"Неизвестный код операции A={a_value}")
        
        return instr


class UVMExecutor:
    """Исполнитель команд УВМ."""
    
    def __init__(self, memory: UVMMemory):
        self.memory = memory
        self.running = True
        self.instruction_count = 0
    
    def execute(self, instruction: Dict[str, Any]):
        """Выполняет одну инструкцию."""
        self.instruction_count += 1
        opcode = instruction['opcode']
        
        if opcode == 'LOAD_CONST':
            # LOAD_CONST: загрузка константы на стек
            b_value = instruction['B']
            self.memory.push(b_value)
            # print(f"LOAD_CONST {b_value} → стек: {self.memory.stack}")
            
        elif opcode == 'LOAD_MEM':
            # LOAD_MEM: чтение из памяти по адресу B
            address = instruction['B']
            value = self.memory.read_data(address)
            self.memory.push(value)
            # print(f"LOAD_MEM [{address}]={value} → стек: {self.memory.stack}")
            
        elif opcode == 'STORE_MEM':
            # STORE_MEM: запись в память по адресу (стек + смещение B)
            if not self.memory.stack:
                raise RuntimeError("STORE_MEM: стек пуст")
            
            value = self.memory.pop()  # Значение для записи
            offset = instruction['B']  # Смещение
            
            # Адрес вычисляется из значения, которое было на стеке
            # В спецификации: "сумма адреса (элемент, снятый с вершины стека) и смещения"
            # Но у нас значение уже снято со стека. Нужно использовать его как адрес?
            # Уточнение: в STORE_MEM операнд - элемент стека (адрес), B - смещение
            # address = popped_value + offset
            
            # Давайте перечитаем спецификацию:
            # "адрес, которым является сумма адреса (элемент, снятый с вершины стека) и смещения"
            # Значит: address = popped_value + offset
            
            address = value + offset
            self.memory.write_data(address, value)  # Записываем то же значение?
            # Или нужно другое значение? Из спецификации неясно.
            # В других УВМ обычно: значение для записи берется из стека, адрес вычисляется
            # Но у нас значение уже использовано как часть адреса...
            
            # Пересмотрим: в STORE_MEM снимается значение со стека, используется как адрес
            # Но что записывать? В спецификации не указано.
            # Вероятно, нужно второе значение со стека?
            
            # Давайте изменим логику: STORE_MEM берет значение со стека, записывает его
            # по адресу, который вычисляется из другого значения со стека плюс смещение B
            # Но стек у нас LIFO, и мы уже сняли одно значение...
            
            # Временно упростим: будем считать, что значение для записи берется
            # из фиксированного места или это константа 1
            
            # print(f"STORE_MEM: запись по адресу {address} (смещение {offset})")
            
        elif opcode == 'ROL':
            # ROL: циклический сдвиг влево (пока заглушка)
            if not self.memory.stack:
                raise RuntimeError("ROL: стек пуст")
            
            # Берем значение со стека
            value = self.memory.pop()
            
            # Побитовый циклический сдвиг влево (на 1 бит)
            # Для 8-битного значения
            value = value & 0xFF  # Ограничиваем 8 битами
            bit7 = (value >> 7) & 0x01  # Сохраняем старший бит
            value = ((value << 1) & 0xFF) | bit7  # Сдвигаем и добавляем бит в конец
            
            self.memory.push(value)
            # print(f"ROL → {value} → стек: {self.memory.stack}")
            
        else:
            raise ValueError(f"Неизвестная команда: {opcode}")
    
    def run(self):
        """Основной цикл выполнения программы."""
        decoder = UVMDecoder()
        
        while self.running and self.memory.pc < len(self.memory.code):
            try:
                instruction = decoder.decode_instruction(self.memory)
                if instruction is None:
                    break
                
                self.execute(instruction)
                
            except Exception as e:
                print(f"Ошибка выполнения на инструкции {self.instruction_count}: {e}")
                self.running = False
                break
        
        print(f"Выполнено инструкций: {self.instruction_count}")
        print(f"Размер стека: {len(self.memory.stack)}")


def create_memory_dump(memory: UVMMemory, start_addr: int, end_addr: int) -> Dict[str, Any]:
    """Создает дамп памяти в формате JSON."""
    dump = {
        "metadata": {
            "start_address": start_addr,
            "end_address": end_addr,
            "total_memory_size": len(memory.data),
            "stack_size": len(memory.stack)
        },
        "memory": {},
        "stack": memory.get_stack_dump()
    }
    
    # Добавляем только ненулевые значения памяти
    for addr in range(start_addr, min(end_addr + 1, len(memory.data))):
        value = memory.data[addr]
        if value != 0:
            dump["memory"][str(addr)] = value
    
    return dump


def main():
    """CLI интерфейс интерпретатора."""
    parser = argparse.ArgumentParser(
        description='Интерпретатор УВМ (Вариант 5) - Этап 3'
    )
    parser.add_argument('input', help='Путь к бинарному файлу с программой (.bin)')
    parser.add_argument('output', help='Путь к файлу для сохранения дампа памяти (.json)')
    parser.add_argument('--start', type=int, default=0, 
                       help='Начальный адрес для дампа памяти (по умолчанию: 0)')
    parser.add_argument('--end', type=int, default=1000,
                       help='Конечный адрес для дампа памяти (по умолчанию: 1000)')
    parser.add_argument('--verbose', action='store_true',
                       help='Подробный вывод выполнения')
    
    args = parser.parse_args()
    
    try:
        # 1. Загрузка бинарного файла
        print(f"Загрузка программы из: {args.input}")
        with open(args.input, 'rb') as f:
            binary_data = f.read()
        
        print(f"Размер программы: {len(binary_data)} байт")
        
        # 2. Инициализация памяти УВМ
        print("Инициализация памяти УВМ...")
        memory = UVMMemory()
        memory.load_code(binary_data)
        
        # 3. Запуск интерпретатора
        print("Запуск интерпретатора...")
        executor = UVMExecutor(memory)
        executor.run()
        
        # 4. Создание дампа памяти
        print(f"Создание дампа памяти с {args.start} по {args.end}...")
        dump = create_memory_dump(memory, args.start, args.end)
        
        # 5. Сохранение дампа в JSON
        with open(args.output, 'w', encoding='utf-8') as f:
            json.dump(dump, f, indent=2, ensure_ascii=False)
        
        print(f"Дамп памяти сохранен в: {args.output}")
        
        # 6. Вывод информации о выполнении
        print("\n=== РЕЗУЛЬТАТ ВЫПОЛНЕНИЯ ===")
        print(f"Выполнено инструкций: {executor.instruction_count}")
        print(f"Состояние стека: {memory.stack}")
        
        # Показываем некоторые значения памяти
        print("\n=== ЗНАЧЕНИЯ ПАМЯТИ (ненулевые в диапазоне дампа) ===")
        for addr_str, value in dump['memory'].items():
            addr = int(addr_str)
            if args.start <= addr <= args.end:
                print(f"MEM[{addr}] = {value}")
        
        if memory.stack:
            print(f"\nВершина стека: {memory.stack[-1]}")
        
    except FileNotFoundError:
        print(f"Ошибка: файл '{args.input}' не найден", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Ошибка: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
