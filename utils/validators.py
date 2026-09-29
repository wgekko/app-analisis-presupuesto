def validate_amount(amount_str) -> tuple[bool, float]:
    """
    Valida que el importe introducido sea un número válido y mayor que cero.
    Devuelve: (es_valido, valor_convertido_a_float)
    """
    try:
        # Reemplazar comas por puntos por si el usuario usa formato europeo
        if isinstance(amount_str, str):
            amount_str = amount_str.replace(',', '.')
        
        val = float(amount_str)
        if val <= 0:
            return False, 0.0
        return True, val
    except (ValueError, TypeError):
        return False, 0.0

def validate_required_field(value: str) -> bool:
    """
    Verifica que un campo de texto obligatorio no esté vacío.
    """
    if not value or not str(value).strip():
        return False
    return True