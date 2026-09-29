def calc_variation(current_value: float, previous_value: float) -> float:
    """
    Calcula la variación porcentual entre dos periodos (Ej: Crecimiento MoM o YoY).
    """
    if previous_value == 0:
        return 0.0 if current_value == 0 else 100.0
    return ((current_value - previous_value) / previous_value) * 100.0

def calc_compound_projection(base_amount: float, annual_rate_pct: float, months: int) -> float:
    """
    Calcula el valor futuro utilizando una tasa de crecimiento compuesto.
    Ideal para proyectar inflación o aumento de ingresos en el simulador.
    """
    if months <= 0:
        return base_amount
    
    monthly_rate = (annual_rate_pct / 100) / 12
    return base_amount * ((1 + monthly_rate) ** months)

def calc_roi(net_profit: float, investment: float) -> float:
    """
    Calcula el Retorno de Inversión (ROI) en porcentaje.
    """
    if investment <= 0:
        return 0.0
    return (net_profit / investment) * 100.0