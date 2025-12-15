; Тестовая задача Этапа 5: поэлементный ROL над двумя векторами длины 5
; Вариант 5: ROL (побитовый циклический сдвиг влево)

; ПЕРВЫЙ ПРИМЕР: базовый тест

; 1. Инициализация первого вектора (значения для сдвига)
LOAD_CONST 0b10000001  ; 129 - элемент 0
STORE_MEM 100
LOAD_CONST 0b11001100  ; 204 - элемент 1
STORE_MEM 101
LOAD_CONST 0b10101010  ; 170 - элемент 2
STORE_MEM 102
LOAD_CONST 0b11110000  ; 240 - элемент 3
STORE_MEM 103
LOAD_CONST 0b00001111  ; 15  - элемент 4
STORE_MEM 104

; 2. Инициализация второго вектора (количество сдвигов)
LOAD_CONST 1           ; 1 сдвиг для элемента 0
STORE_MEM 200
LOAD_CONST 2           ; 2 сдвига для элемента 1
STORE_MEM 201
LOAD_CONST 3           ; 3 сдвига для элемента 2
STORE_MEM 202
LOAD_CONST 0           ; 0 сдвигов для элемента 3
STORE_MEM 203
LOAD_CONST 4           ; 4 сдвига для элемента 4
STORE_MEM 204

; 3. Выполнение поэлементного ROL
; Элемент 0: MEM[100] ROL MEM[200] → MEM[300]
LOAD_MEM 100          ; Значение элемента 0
LOAD_CONST 200        ; Адрес с количеством сдвигов
ROL                   ; Выполняем ROL
STORE_MEM 300         ; Сохраняем результат

; Элемент 1: MEM[101] ROL MEM[201] → MEM[301]
LOAD_MEM 101
LOAD_CONST 201
ROL
STORE_MEM 301

; Элемент 2: MEM[102] ROL MEM[202] → MEM[302]
LOAD_MEM 102
LOAD_CONST 202
ROL
STORE_MEM 302

; Элемент 3: MEM[103] ROL MEM[203] → MEM[303]
LOAD_MEM 103
LOAD_CONST 203
ROL
STORE_MEM 303

; Элемент 4: MEM[104] ROL MEM[204] → MEM[304]
LOAD_MEM 104
LOAD_CONST 204
ROL
STORE_MEM 304

; ВТОРОЙ ПРИМЕР: все элементы с одинаковым сдвигом

; Инициализация третьего вектора
LOAD_CONST 0b01010101  ; 85 - элемент 0
STORE_MEM 400
LOAD_CONST 0b00110011  ; 51 - элемент 1
STORE_MEM 401
LOAD_CONST 0b00001111  ; 15 - элемент 2
STORE_MEM 402
LOAD_CONST 0b11111111  ; 255 - элемент 3
STORE_MEM 403
LOAD_CONST 0b00000001  ; 1 - элемент 4
STORE_MEM 404

; Количество сдвигов = 1 для всех
LOAD_CONST 1
STORE_MEM 500
LOAD_CONST 1
STORE_MEM 501
LOAD_CONST 1
STORE_MEM 502
LOAD_CONST 1
STORE_MEM 503
LOAD_CONST 1
STORE_MEM 504

; Выполнение ROL
LOAD_MEM 400
LOAD_CONST 500
ROL
STORE_MEM 600

LOAD_MEM 401
LOAD_CONST 501
ROL
STORE_MEM 601

LOAD_MEM 402
LOAD_CONST 502
ROL
STORE_MEM 602

LOAD_MEM 403
LOAD_CONST 503
ROL
STORE_MEM 603

LOAD_MEM 404
LOAD_CONST 504
ROL
STORE_MEM 604

; ТРЕТИЙ ПРИМЕР: граничные случаи

; Вектор с крайними значениями
LOAD_CONST 0b00000001  ; 1 - минимальное ненулевое
STORE_MEM 700
LOAD_CONST 0b10000000  ; 128 - старший бит = 1
STORE_MEM 701
LOAD_CONST 0b11111111  ; 255 - все биты = 1
STORE_MEM 702
LOAD_CONST 0b00000000  ; 0 - все биты = 0
STORE_MEM 703
LOAD_CONST 0b01010101  ; 85 - паттерн 0101
STORE_MEM 704

; Количество сдвигов: 7, 15, 0, 8, 1
LOAD_CONST 7
STORE_MEM 800
LOAD_CONST 15          ; 15 mod 8 = 7
STORE_MEM 801
LOAD_CONST 0
STORE_MEM 802
LOAD_CONST 8
STORE_MEM 803
LOAD_CONST 1
STORE_MEM 804

; Выполнение ROL
LOAD_MEM 700
LOAD_CONST 800
ROL
STORE_MEM 900

LOAD_MEM 701
LOAD_CONST 801
ROL
STORE_MEM 901

LOAD_MEM 702
LOAD_CONST 802
ROL
STORE_MEM 902

LOAD_MEM 703
LOAD_CONST 803
ROL
STORE_MEM 903

LOAD_MEM 704
LOAD_CONST 804
ROL
STORE_MEM 904

; Чтение результатов для проверки (оставляем на стеке)
LOAD_MEM 300  ; Результат примера 1, элемент 0
LOAD_MEM 301  ; элемент 1
LOAD_MEM 302  ; элемент 2
LOAD_MEM 303  ; элемент 3
LOAD_MEM 304  ; элемент 4

LOAD_MEM 600  ; Результат примера 2, элемент 0
LOAD_MEM 601  ; элемент 1
LOAD_MEM 602  ; элемент 2
LOAD_MEM 603  ; элемент 3
LOAD_MEM 604  ; элемент 4

LOAD_MEM 900  ; Результат примера 3, элемент 0
LOAD_MEM 901  ; элемент 1
LOAD_MEM 902  ; элемент 2
LOAD_MEM 903  ; элемент 3
LOAD_MEM 904  ; элемент 4
