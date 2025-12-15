def validate_range(value, min_val, max_val, name="значение"):
    """
    Проверяет, находится ли значение в заданном диапазоне.
    """
    if not (min_val <= value <= max_val):
        raise ValueError(f"{name} {value} вне диапазона {min_val}..{max_val}")
    return value

def to_signed(value, bits):
    """
    Преобразует значение в знаковое.
    """
    if value >= (1 << (bits - 1)):
        value -= (1 << bits)
    return value

def from_signed(value, bits):
    """
    Преобразует знаковое значение в беззнаковое для хранения.
    """
    if value < 0:
        value += (1 << bits)
    return value & ((1 << bits) - 1)

def bytes_to_hex_string(byte_array):
    """Конвертирует массив байт в строку hex значений."""
    return ', '.join(f'0x{b:02X}' for b in byte_array)

def format_binary_for_spec(binary_data):
    """
    Форматирует бинарные данные в формате как в спецификации УВМ.
    """
    result = []
    for byte in binary_data:
        # Преобразуем байт в двоичное представление
        bin_str = format(byte, '08b')
        # Группируем по 4 бита для читаемости
        grouped = ' '.join([bin_str[i:i+4] for i in range(0, len(bin_str), 4)])
        result.append(f"{grouped} (0x{byte:02X})")
    return '\n'.join(result)
