def is_float(value):
    try:
        float(value)
        return True
    except ValueError:
        return False

def is_integer(value):
    """Перевіряє, чи є значення цілим числом."""
    try:
        int(value)
        return True
    except ValueError:
        return False