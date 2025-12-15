#!/usr/bin/env python3
"""
GUI-приложение для УВМ (Вариант 5)
Кроссплатформенная версия с поддержкой Windows, Linux и Web/WASM (чесли PyScript)
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, filedialog
import os
import sys
import subprocess
import json
import threading
from datetime import datetime

# Добавляем путь к модулям проекта
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from parser import parse_assembly
    from encoder import encode_to_intermediate, encode_to_binary
    from interpreter import UVMMemory, UVMExecutor, create_memory_dump
except ImportError:
    # Для случая, если модули не импортируются (Web версия)
    pass

class UVMGUIApp:
    """Основной класс GUI-приложения УВМ."""
    
    def __init__(self, root):
        self.root = root
        self.root.title("УВМ (Учебная Виртуальная Машина) - Вариант 5")
        self.root.geometry("1200x700")
        
        # Инициализация переменных
        self.current_file = None
        self.memory_dump = None
        self.is_running = False
        
        # Создание интерфейса
        self.create_widgets()
        self.setup_layout()
        
        # Загрузка примера программы
        self.load_example()
        
        # Связываем горячие клавиши
        self.bind_shortcuts()
    
    def create_widgets(self):
        """Создает все виджеты интерфейса."""
        
        # Панель вкладок
        self.notebook = ttk.Notebook(self.root)
        
        # Вкладка 1: Редактор программы
        self.editor_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.editor_frame, text="Программа")
        
        # Панель инструментов редактора
        self.toolbar = ttk.Frame(self.editor_frame)
        
        self.btn_new = ttk.Button(self.toolbar, text="Новый", command=self.new_file)
        self.btn_open = ttk.Button(self.toolbar, text="Открыть", command=self.open_file)
        self.btn_save = ttk.Button(self.toolbar, text="Сохранить", command=self.save_file)
        self.btn_save_as = ttk.Button(self.toolbar, text="Сохранить как", command=self.save_file_as)
        
        self.btn_new.pack(side=tk.LEFT, padx=2, pady=2)
        self.btn_open.pack(side=tk.LEFT, padx=2, pady=2)
        self.btn_save.pack(side=tk.LEFT, padx=2, pady=2)
        self.btn_save_as.pack(side=tk.LEFT, padx=2, pady=2)
        
        ttk.Separator(self.toolbar, orient=tk.VERTICAL).pack(side=tk.LEFT, padx=5, fill=tk.Y)
        
        self.btn_load_example = ttk.Button(self.toolbar, text="Загрузить пример", 
                                          command=self.load_example)
        self.btn_clear = ttk.Button(self.toolbar, text="Очистить", command=self.clear_editor)
        self.btn_load_example.pack(side=tk.LEFT, padx=2, pady=2)
        self.btn_clear.pack(side=tk.LEFT, padx=2, pady=2)
        
        self.toolbar.pack(fill=tk.X, padx=5, pady=5)
        
        # Редактор кода
        self.editor = scrolledtext.ScrolledText(self.editor_frame, 
                                               wrap=tk.WORD,
                                               font=("Courier New", 10),
                                               undo=True)
        self.editor.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Вкладка 2: Вывод и память
        self.output_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.output_frame, text="Память и вывод")
        
        # Панель вывода
        self.output_label = ttk.Label(self.output_frame, text="Вывод ассемблера и интерпретатора:")
        self.output_label.pack(anchor=tk.W, padx=5, pady=(5,0))
        
        self.output_text = scrolledtext.ScrolledText(self.output_frame,
                                                    wrap=tk.WORD,
                                                    font=("Courier New", 9),
                                                    height=10)
        self.output_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Панель дампа памяти
        self.memory_frame = ttk.LabelFrame(self.output_frame, text="Дамп памяти")
        self.memory_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Панель управления диапазоном памяти
        self.memory_control = ttk.Frame(self.memory_frame)
        self.memory_control.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(self.memory_control, text="Начало:").pack(side=tk.LEFT, padx=2)
        self.start_addr = tk.StringVar(value="0")
        self.entry_start = ttk.Entry(self.memory_control, textvariable=self.start_addr, width=10)
        self.entry_start.pack(side=tk.LEFT, padx=2)
        
        ttk.Label(self.memory_control, text="Конец:").pack(side=tk.LEFT, padx=2)
        self.end_addr = tk.StringVar(value="100")
        self.entry_end = ttk.Entry(self.memory_control, textvariable=self.end_addr, width=10)
        self.entry_end.pack(side=tk.LEFT, padx=2)
        
        self.btn_refresh_memory = ttk.Button(self.memory_control, text="Обновить", 
                                            command=self.refresh_memory_dump)
        self.btn_refresh_memory.pack(side=tk.LEFT, padx=10)
        
        self.btn_save_dump = ttk.Button(self.memory_control, text="Сохранить дамп", 
                                       command=self.save_memory_dump)
        self.btn_save_dump.pack(side=tk.LEFT, padx=2)
        
        # Текстовое поле для дампа памяти
        self.memory_text = scrolledtext.ScrolledText(self.memory_frame,
                                                    wrap=tk.WORD,
                                                    font=("Courier New", 9),
                                                    height=15)
        self.memory_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Вкладка 3: Справка
        self.help_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.help_frame, text="Справка")
        
        help_text = """
УВМ (Учебная Виртуальная Машина) - Вариант 5

ДОСТУПНЫЕ КОМАНДЫ:

1. LOAD_CONST <value>    - Загрузка константы на стек
   Диапазон: 0-1023
   Пример: LOAD_CONST 100

2. LOAD_MEM <address>    - Чтение из памяти по адресу
   Диапазон: 0-16777215
   Пример: LOAD_MEM 500

3. STORE_MEM <offset>    - Запись в память (стек + смещение)
   Диапазон: -4096..4095
   Пример: STORE_MEM 10

4. ROL                    - Циклический сдвиг влево
   Пример: ROL

ФОРМАТ ПРОГРАММЫ:
- Одна команда на строку
- Комментарии начинаются с ; 
- Регистр команд не важен
- Пробелы и табуляции игнорируются

ПРИМЕР ПРОГРАММЫ:
; Загрузка константы
LOAD_CONST 100
; Чтение из памяти
LOAD_MEM 500
; Запись в память
STORE_MEM 0
; Циклический сдвиг
ROL

ГОРЯЧИЕ КЛАВИШИ:
Ctrl+N - Новый файл
Ctrl+O - Открыть файл
Ctrl+S - Сохранить файл
Ctrl+R - Запустить программу
F5     - Ассемблировать и выполнить
F1     - Справка
"""
        
        self.help_text = scrolledtext.ScrolledText(self.help_frame,
                                                  wrap=tk.WORD,
                                                  font=("Arial", 10))
        self.help_text.insert(1.0, help_text)
        self.help_text.config(state=tk.DISABLED)
        self.help_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Панель управления (внизу окна)
        self.control_frame = ttk.Frame(self.root)
        
        self.status_label = ttk.Label(self.control_frame, text="Готово")
        self.status_label.pack(side=tk.LEFT, padx=10)
        
        self.btn_assemble = ttk.Button(self.control_frame, text="Ассемблировать", 
                                      command=self.assemble_program)
        self.btn_assemble.pack(side=tk.RIGHT, padx=5, pady=5)
        
        self.btn_run = ttk.Button(self.control_frame, text="Выполнить", 
                                 command=self.run_program, style="Accent.TButton")
        self.btn_run.pack(side=tk.RIGHT, padx=5, pady=5)
        
        self.btn_asm_run = ttk.Button(self.control_frame, text="Ассемблировать и выполнить",
                                     command=self.assemble_and_run)
        self.btn_asm_run.pack(side=tk.RIGHT, padx=5, pady=5)
    
    def setup_layout(self):
        """Настраивает layout интерфейса."""
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=(5,0))
        self.control_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Стиль для акцентной кнопки
        style = ttk.Style()
        style.configure("Accent.TButton", foreground="white", background="#007acc")
    
    def bind_shortcuts(self):
        """Привязывает горячие клавиши."""
        self.root.bind('<Control-n>', lambda e: self.new_file())
        self.root.bind('<Control-o>', lambda e: self.open_file())
        self.root.bind('<Control-s>', lambda e: self.save_file())
        self.root.bind('<F5>', lambda e: self.assemble_and_run())
        self.root.bind('<Control-r>', lambda e: self.run_program())
        self.root.bind('<F1>', lambda e: self.notebook.select(2))  # Переход к справке
    
    def load_example(self):
        """Загружает пример программы."""
        example_code = """; Пример программы для УВМ (Вариант 5)
; Тестовая программа из спецификации

LOAD_CONST 343   ; Тест: A=2, B=343 → 0x4A, 0xB7
LOAD_MEM   365   ; Тест: A=3, B=365 → 0x60, 0x00, 0x01, 0x6D
STORE_MEM  899   ; Тест: A=1, B=899 → 0x2E, 0x03
ROL             ; Тест: A=4 → 0x80

; Дополнительные тестовые операции
LOAD_CONST 100   ; Загрузка константы 100
STORE_MEM  0     ; Запись по адресу 0
LOAD_MEM   133   ; Чтение MEM[133] (должно быть 42)
"""
        
        self.editor.delete(1.0, tk.END)
        self.editor.insert(1.0, example_code)
        self.current_file = None
        self.update_status("Загружен пример программы")
    
    def clear_editor(self):
        """Очищает редактор."""
        if messagebox.askyesno("Очистка", "Очистить редактор кода?"):
            self.editor.delete(1.0, tk.END)
            self.current_file = None
            self.update_status("Редактор очищен")
    
    def new_file(self):
        """Создает новый файл."""
        if self.current_file or self.editor.get(1.0, tk.END).strip():
            if not messagebox.askyesno("Новый файл", "Сохранить текущий файл?"):
                self.editor.delete(1.0, tk.END)
                self.current_file = None
                self.update_status("Создан новый файл")
        else:
            self.editor.delete(1.0, tk.END)
            self.current_file = None
            self.update_status("Создан новый файл")
    
    def open_file(self):
        """Открывает файл с программой."""
        filepath = filedialog.askopenfilename(
            title="Открыть файл программы",
            filetypes=[("Ассемблерные файлы", "*.asm"), ("Все файлы", "*.*")]
        )
        
        if filepath:
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                self.editor.delete(1.0, tk.END)
                self.editor.insert(1.0, content)
                self.current_file = filepath
                self.update_status(f"Открыт файл: {os.path.basename(filepath)}")
                
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось открыть файл:\n{str(e)}")
    
    def save_file(self):
        """Сохраняет текущий файл."""
        if self.current_file:
            self._save_to_file(self.current_file)
        else:
            self.save_file_as()
    
    def save_file_as(self):
        """Сохраняет файл под новым именем."""
        filepath = filedialog.asksaveasfilename(
            title="Сохранить файл",
            defaultextension=".asm",
            filetypes=[("Ассемблерные файлы", "*.asm"), ("Все файлы", "*.*")]
        )
        
        if filepath:
            self._save_to_file(filepath)
            self.current_file = filepath
    
    def _save_to_file(self, filepath):
        """Сохраняет содержимое редактора в файл."""
        try:
            content = self.editor.get(1.0, tk.END)
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            
            self.update_status(f"Файл сохранен: {os.path.basename(filepath)}")
            return True
            
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось сохранить файл:\n{str(e)}")
            return False
    
    def assemble_program(self):
        """Ассемблирует программу без выполнения."""
        self.output_text.delete(1.0, tk.END)
        
        try:
            source = self.editor.get(1.0, tk.END)
            
            # Парсинг и ассемблирование
            program = parse_assembly(source)
            intermediate = encode_to_intermediate(program)
            binary = encode_to_binary(intermediate)
            
            # Вывод результатов
            self.output_text.insert(tk.END, "=== РЕЗУЛЬТАТ АССЕМБЛИРОВАНИЯ ===\n\n")
            self.output_text.insert(tk.END, f"Инструкций найдено: {len(program)}\n")
            self.output_text.insert(tk.END, f"Размер бинарного кода: {len(binary)} байт\n\n")
            
            self.output_text.insert(tk.END, "Промежуточное представление:\n")
            for i, instr in enumerate(intermediate):
                self.output_text.insert(tk.END, 
                    f"  [{i}] {instr['opcode']}: A={instr['A']}, B={instr.get('B', 'N/A')}\n")
            
            self.output_text.insert(tk.END, "\nБинарный код (hex):\n")
            hex_str = ' '.join(f'{b:02X}' for b in binary)
            self.output_text.insert(tk.END, f"  {hex_str}\n")
            
            self.update_status(f"Программа ассемблирована успешно ({len(program)} инструкций)")
            
            # Переключение на вкладку вывода
            self.notebook.select(1)
            
            return binary
            
        except Exception as e:
            self.output_text.insert(tk.END, f"ОШИБКА АССЕМБЛИРОВАНИЯ:\n{str(e)}\n")
            self.update_status("Ошибка ассемблирования")
            return None
    
    def run_program(self):
        """Выполняет программу (требует предварительного ассемблирования)."""
        if not hasattr(self, 'last_binary') or not self.last_binary:
            messagebox.showwarning("Предупреждение", 
                                 "Сначала ассемблируйте программу!")
            return
        
        self.output_text.insert(tk.END, "\n\n=== ВЫПОЛНЕНИЕ ПРОГРАММЫ ===\n")
        
        try:
            # Инициализация и выполнение
            memory = UVMMemory()
            memory.load_code(self.last_binary)
            
            executor = UVMExecutor(memory)
            
            # Выполняем в отдельном потоке
            def run_in_thread():
                self.is_running = True
                self.btn_run.config(state=tk.DISABLED)
                self.update_status("Выполнение программы...")
                
                try:
                    executor.run()
                    
                    # Получаем дамп памяти
                    start = int(self.start_addr.get())
                    end = int(self.end_addr.get())
                    self.memory_dump = create_memory_dump(memory, start, end)
                    
                    # Обновляем интерфейс в основном потоке
                    self.root.after(0, self._update_after_execution, executor, memory)
                    
                except Exception as e:
                    self.root.after(0, self._execution_error, str(e))
                
                finally:
                    self.is_running = False
                    self.root.after(0, lambda: self.btn_run.config(state=tk.NORMAL))
            
            # Запускаем в отдельном потоке
            thread = threading.Thread(target=run_in_thread)
            thread.daemon = True
            thread.start()
            
        except Exception as e:
            self.output_text.insert(tk.END, f"ОШИБКА ВЫПОЛНЕНИЯ:\n{str(e)}\n")
            self.update_status("Ошибка выполнения")
    
    def _update_after_execution(self, executor, memory):
        """Обновляет интерфейс после выполнения программы."""
        self.output_text.insert(tk.END, f"\nВыполнено инструкций: {executor.instruction_count}\n")
        self.output_text.insert(tk.END, f"Размер стека: {len(memory.stack)}\n")
        
        if memory.stack:
            self.output_text.insert(tk.END, f"Состояние стека: {memory.stack}\n")
        
        self.update_status(f"Программа выполнена ({executor.instruction_count} инструкций)")
        
        # Обновляем дамп памяти
        self.refresh_memory_dump()
        
        # Показываем вкладку с результатами
        self.notebook.select(1)
    
    def _execution_error(self, error_msg):
        """Обрабатывает ошибку выполнения."""
        self.output_text.insert(tk.END, f"\nОШИБКА ВЫПОЛНЕНИЯ:\n{error_msg}\n")
        self.update_status("Ошибка выполнения")
    
    def assemble_and_run(self):
        """Ассемблирует и выполняет программу."""
        self.output_text.delete(1.0, tk.END)
        
        # Ассемблируем
        binary = self.assemble_program()
        
        if binary is not None:
            # Сохраняем бинарный код для выполнения
            self.last_binary = binary
            
            # Выполняем
            self.run_program()
    
    def refresh_memory_dump(self):
        """Обновляет отображение дампа памяти."""
        if self.memory_dump is None:
            self.memory_text.delete(1.0, tk.END)
            self.memory_text.insert(tk.END, "Память не загружена.\nЗапустите программу для получения дампа памяти.")
            return
        
        try:
            start = int(self.start_addr.get())
            end = int(self.end_addr.get())
            
            self.memory_text.delete(1.0, tk.END)
            
            # Форматируем дамп памяти
            self.memory_text.insert(tk.END, f"Дамп памяти с адреса {start} по {end}:\n")
            self.memory_text.insert(tk.END, "=" * 50 + "\n")
            
            memory = self.memory_dump.get('memory', {})
            
            if not memory:
                self.memory_text.insert(tk.END, "Нет ненулевых значений в указанном диапазоне.\n")
            else:
                # Сортируем адреса
                sorted_addrs = sorted(memory.keys(), key=lambda x: int(x))
                
                for addr in sorted_addrs:
                    addr_int = int(addr)
                    if start <= addr_int <= end:
                        value = memory[addr]
                        self.memory_text.insert(tk.END, 
                            f"MEM[{addr:>4}] = {value:>3} (0x{value:02X}, 0b{value:08b})\n")
            
            # Показываем стек
            stack = self.memory_dump.get('stack', [])
            if stack:
                self.memory_text.insert(tk.END, "\nСодержимое стека:\n")
                self.memory_text.insert(tk.END, f"  {stack}\n")
                self.memory_text.insert(tk.END, f"  Размер: {len(stack)}, Вершина: {stack[-1] if stack else 'N/A'}\n")
            
            # Показываем метаданные
            metadata = self.memory_dump.get('metadata', {})
            if metadata:
                self.memory_text.insert(tk.END, "\nМетаданные:\n")
                for key, value in metadata.items():
                    self.memory_text.insert(tk.END, f"  {key}: {value}\n")
            
        except ValueError:
            messagebox.showerror("Ошибка", "Некорректный диапазон адресов!")
        except Exception as e:
            self.memory_text.insert(tk.END, f"Ошибка обновления дампа: {str(e)}\n")
    
    def save_memory_dump(self):
        """Сохраняет дамп памяти в файл."""
        if self.memory_dump is None:
            messagebox.showwarning("Предупреждение", "Нет данных дампа памяти для сохранения!")
            return
        
        filepath = filedialog.asksaveasfilename(
            title="Сохранить дамп памяти",
            defaultextension=".json",
            filetypes=[("JSON файлы", "*.json"), ("Все файлы", "*.*")]
        )
        
        if filepath:
            try:
                with open(filepath, 'w', encoding='utf-8') as f:
                    json.dump(self.memory_dump, f, indent=2, ensure_ascii=False)
                
                self.update_status(f"Дамп памяти сохранен: {os.path.basename(filepath)}")
                messagebox.showinfo("Успех", "Дамп памяти успешно сохранен!")
                
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось сохранить дамп памяти:\n{str(e)}")
    
    def update_status(self, message):
        """Обновляет статусную строку."""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.status_label.config(text=f"[{timestamp}] {message}")
        self.root.update_idletasks()

def main():
    """Запуск GUI-приложения."""
    root = tk.Tk()
    
    # Настройка иконки (если есть)
    try:
        if sys.platform == "win32":
            root.iconbitmap(default="uvm_icon.ico")
    except:
        pass
    
    app = UVMGUIApp(root)
    
    # Центрирование окна
    root.update_idletasks()
    width = root.winfo_width()
    height = root.winfo_height()
    x = (root.winfo_screenwidth() // 2) - (width // 2)
    y = (root.winfo_screenheight() // 2) - (height // 2)
    root.geometry(f'{width}x{height}+{x}+{y}')
    
    root.mainloop()

if __name__ == "__main__":
    main()
