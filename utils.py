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
