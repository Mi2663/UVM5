; Демонстрационная программа с вычислениями Этапа 5
; Три различных примера программ с вычислениями

; ПРИМЕР 1: Последовательные вычисления с ROL

; Инициализация данных
LOAD_CONST 1
STORE_MEM 10   ; MEM[10] = 1 (базовое значение)

; Цепочка вычислений: (((1 ROL 1) ROL 2) ROL 3)
LOAD_MEM 10    ; Загружаем 1
LOAD_CONST 20  ; Адрес с количеством сдвигов (1)
ROL           ; 1 ROL 1 = 2
STORE_MEM 11   ; Сохраняем промежуточный результат

LOAD_MEM 11    ; Загружаем 2
LOAD_CONST 21  ; Адрес с количеством сдвигов (2)
ROL           ; 2 ROL 2 = 8
STORE_MEM 12   ; Сохраняем

LOAD_MEM 12    ; Загружаем 8
LOAD_CONST 22  ; Адрес с количеством сдвигов (3)
ROL           ; 8 ROL 3 = 64
STORE_MEM 13   ; Финальный результат

; Записываем количество сдвигов в память
LOAD_CONST 1
STORE_MEM 20
LOAD_CONST 2
STORE_MEM 21
LOAD_CONST 3
STORE_MEM 22

; ПРИМЕР 2: Вычисление паттернов

; Генерация паттерна 01010101 ROL N для разных N
LOAD_CONST 0b01010101  ; 85
STORE_MEM 30

; Вычисляем для N = 1, 2, 4
LOAD_MEM 30
LOAD_CONST 40
ROL           ; 85 ROL 1 = 170
STORE_MEM 31

LOAD_MEM 30
LOAD_CONST 41
ROL           ; 85 ROL 2 = 85? Проверим: 01010101 ROL 2 = 01010101
STORE_MEM 32

LOAD_MEM 30
LOAD_CONST 42
ROL           ; 85 ROL 4 = 85 (симметрия)
STORE_MEM 33

; Записываем количества сдвигов
LOAD_CONST 1
STORE_MEM 40
LOAD_CONST 2
STORE_MEM 41
LOAD_CONST 4
STORE_MEM 42

; ПРИМЕР 3: Работа с массивами данных

; Инициализация массива из 3 элементов
LOAD_CONST 0b00001111  ; 15
STORE_MEM 50
LOAD_CONST 0b00111100  ; 60
STORE_MEM 51
LOAD_CONST 0b11110000  ; 240
STORE_MEM 52

; Количество сдвигов для каждого элемента
LOAD_CONST 2
STORE_MEM 60
LOAD_CONST 4
STORE_MEM 61
LOAD_CONST 6
STORE_MEM 62

; Выполняем ROL для каждого элемента
LOAD_MEM 50
LOAD_CONST 60
ROL           ; 15 ROL 2 = 60
STORE_MEM 70

LOAD_MEM 51
LOAD_CONST 61
ROL           ; 60 ROL 4 = 60 (240 после сдвига, но 60 & 0xFF = 60)
STORE_MEM 71

LOAD_MEM 52
LOAD_CONST 62
ROL           ; 240 ROL 6 = 15
STORE_MEM 72

; Чтение всех результатов для дампа
LOAD_MEM 13   ; Результат примера 1
LOAD_MEM 31   ; Результат примера 2.1
LOAD_MEM 32   ; Результат примера 2.2
LOAD_MEM 33   ; Результат примера 2.3
LOAD_MEM 70   ; Результат примера 3.1
LOAD_MEM 71   ; Результат примера 3.2
LOAD_MEM 72   ; Результат примера 3.3
