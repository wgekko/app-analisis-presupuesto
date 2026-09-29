import pandas as pd
from datetime import date

def format_currency(value: float, currency_symbol: str = "$") -> str:
    """
    Convierte un valor numérico a un formato de moneda limpio.
    Ejemplo: 15400.5 -> $15,400.50
    """
    try:
        val = float(value)
        return f"{currency_symbol}{val:,.2f}"
    except (ValueError, TypeError):
        return f"{currency_symbol}0.00"

def format_date_to_string(d: date) -> str:
    """
    Convierte un objeto fecha a formato legible DD/MM/YYYY.
    """
    if isinstance(d, (date, pd.Timestamp)):
        return pd.to_datetime(d).strftime('%d/%m/%Y')
    return str(d)

def clean_string(text: str) -> str:
    """
    Limpia espacios en blanco sobrantes y estandariza textos.
    """
    if not isinstance(text, str):
        return ""
    return text.strip().capitalize()