def is_non_empty_string(value: str) -> bool:
    return isinstance(value, str) and value.strip() != ""

def is_positive_int(value) -> bool:
    try:
        return int(value) > 0
    except (TypeError, ValueError):
        return False
