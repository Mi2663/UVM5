#!/usr/bin/env python3
"""
Скрипт сборки УВМ для всех платформ:
- Windows (exe)
- Linux (исполняемый файл)
- Web/WASM (html + pyscript)
"""

import os
import sys
import shutil
import subprocess
import platform
import zipfile
from pathlib import Path
from datetime import datetime

class UVMBuilder:
    """Сборщик УВМ для всех платформ."""
    
    def __init__(self):
        self.project_dir = Path(__file__).parent
        self.build_dir = self.project_dir / "build"
        self.dist_dir = self.project_dir / "dist"
        
        # Создаем директории сборки
        self.build_dir.mkdir(exist_ok=True)
        self.dist_dir.mkdir(exist_ok=True)
        
        # Файлы проекта
        self.core_files = [
            'main.py',
            'parser.py', 
            'encoder.py',
            'utils.py',
            'interpreter.py',
            'gui_app.py',
            'web_uvm.html',
            'README.md',
            'LICENSE',
            '.gitignore'
        ]
        
        self.example_files = [
            'example1.asm',
            'spec_test.asm',
            'rol_demo.asm',
            'vector_rol.asm',
            'test_task.asm',
            'calc_demo.asm',
            'simple_rol.asm'
        ]
        
        self.test_files = [
            'test_parser.py',
            'test_encoder.py',
            'test_binary_encoding.py',
            'test_interpreter.py',
            'test_alu.py'
        ]
        
        self.script_files = [
            'demo_stage3.py',
            'demo_stage4.py',
            'verify_task.py',
            'execute_stage5.py'
        ]
    
    def clean_build(self):
        """Очистка директорий сборки."""
        print("Очистка директорий сборки...")
        
        for dir_path in [self.build_dir, self.dist_dir]:
            if dir_path.exists():
                shutil.rmtree(dir_path)
                print(f"  Удалено: {dir_path}")
        
        self.build_dir.mkdir(exist_ok=True)
        self.dist_dir.mkdir(exist_ok=True)
    
    def copy_project_files(self):
        """Копирует файлы проекта в build директорию."""
        print("\nКопирование файлов проекта...")
        
        # Копируем основные файлы
        for file_name in self.core_files:
            src = self.project_dir / file_name
            if src.exists():
                dst = self.build_dir / file_name
                shutil.copy2(src, dst)
                print(f"  Скопирован: {file_name}")
        
        # Создаем директорию примеров
        examples_dir = self.build_dir / "examples"
        examples_dir.mkdir(exist_ok=True)
        
        for file_name in self.example_files:
            src = self.project_dir / file_name
            if src.exists():
                dst = examples_dir / file_name
                shutil.copy2(src, dst)
                print(f"  Скопирован в examples: {file_name}")
        
        # Создаем директорию тестов
        tests_dir = self.build_dir / "tests"
        tests_dir.mkdir(exist_ok=True)
        
        for file_name in self.test_files:
            src = self.project_dir / file_name
            if src.exists():
                dst = tests_dir / file_name
                shutil.copy2(src, dst)
                print(f"  Скопирован в tests: {file_name}")
        
        # Копируем скрипты
        for file_name in self.script_files:
            src = self.project_dir / file_name
            if src.exists():
                dst = self.build_dir / file_name
                shutil.copy2(src, dst)
                print(f"  Скопирован: {file_name}")
    
    def create_requirements_file(self):
        """Создает файл requirements.txt."""
        requirements = """# Требования для УВМ
# Базовые зависимости

# Для GUI приложения (Tkinter обычно входит в стандартную поставку Python)
# Для сборки в exe:
# pip install pyinstaller

# Для Web версии требуется только браузер с поддержкой PyScript
"""
        
        req_file = self.build_dir / "requirements.txt"
        req_file.write_text(requirements, encoding='utf-8')
        print("  Создан: requirements.txt")
    
    def create_readme_for_dist(self):
        """Создает README для дистрибутива."""
        readme_content = """# УВМ (Учебная Виртуальная Машина) - Вариант 5

## Кроссплатформенный дистрибутив

### Доступные версии:
1. **GUI приложение** (Windows/Linux/macOS)
   - Запуск: `python gui_app.py` или запустите исполняемый файл
   - Полноценный графический интерфейс
   - Редактор кода, выполнение, дамп памяти

2. **CLI приложение** (Windows/Linux/macOS)
   - Ассемблер: `python main.py <input.asm> <output.bin> [--test]`
   - Интерпретатор: `python interpreter.py <input.bin> <output.json> [--start N --end M]`

3. **Web версия** (браузер)
   - Откройте `web_uvm.html` в браузере
   - Работает через PyScript/WASM
   - Не требует установки Python

### Быстрый старт:

#### GUI версия:
```bash
# Установите Python 3.8+
# Перейдите в директорию с файлами
python gui_app.py
