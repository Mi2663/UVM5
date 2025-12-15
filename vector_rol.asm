; Программа для поэлементного ROL над двумя векторами длины 5
; Этап 4: Тестовая задача
; Первый вектор (значения): адреса 300-304
; Второй вектор (адреса с количеством сдвигов): адреса 400-404
; Результат (второй вектор): адреса 500-504

; 1. Инициализация первого вектора (значения для сдвига)
LOAD_CONST 0b10000001  ; 129
STORE_MEM 300
LOAD_CONST 0b11001100  ; 204
STORE_MEM 301
LOAD_CONST 0b10101010  ; 170
STORE_MEM 302
LOAD_CONST 0b11110000  ; 240
STORE_MEM 303
LOAD_CONST 0b00001111  ; 15
STORE_MEM 304

; 2. Инициализация второго вектора (адреса с количеством сдвигов)
; В эти адреса записываем количество сдвигов
LOAD_CONST 1
STORE_MEM 400
LOAD_CONST 2
STORE_MEM 401
LOAD_CONST 3
STORE_MEM 402
LOAD_CONST 0
STORE_MEM 403
LOAD_CONST 4
STORE_MEM 404

; 3. Выполнение поэлементного ROL
; Элемент 0
LOAD_MEM 300          ; Значение из первого вектора
LOAD_CONST 400        ; Адрес с количеством сдвигов
ROL
STORE_MEM 500         ; Сохраняем результат

; Элемент 1
LOAD_MEM 301
LOAD_CONST 401
ROL
STORE_MEM 501

; Элемент 2
LOAD_MEM 302
LOAD_CONST 402
ROL
STORE_MEM 502

; Элемент 3
LOAD_MEM 303
LOAD_CONST 403
ROL
STORE_MEM 503

; Элемент 4
LOAD_MEM 304
LOAD_CONST 404
ROL
STORE_MEM 504

; 4. Проверка результатов (читаем результаты)
LOAD_MEM 500    ; Результат элемента 0
LOAD_MEM 501    ; Результат элемента 1
LOAD_MEM 502    ; Результат элемента 2
LOAD_MEM 503    ; Результат элемента 3
LOAD_MEM 504    ; Результат элемента 4
