import pandas as pd

def calcular_score_riesgo(df: pd.DataFrame, proyecto: str = "Todos") -> dict:
    """Calcula un índice de salud financiera de 0 (Crítico) a 100 (Excelente)."""
    df_calc = df if proyecto == "Todos" else df[df['proyecto'] == proyecto]
    if df_calc.empty:
        return {"score": 0, "nivel": "Sin Datos", "color": "gray"}

    ingresos = df_calc[df_calc['tipo'] == 'Ingreso']['importe'].sum()
    egresos = df_calc[df_calc['tipo'] == 'Egreso']['importe'].sum()
    pendientes = df_calc[df_calc['estado'] == 'Pendiente']['importe'].sum()

    score = 100.0
    
    # 1. Penalización por margen operativo
    if ingresos > 0:
        ratio_gasto = egresos / ingresos
        score -= (ratio_gasto * 50) 
    else:
        score = 20 if egresos > 0 else 50 

    # 2. Penalización por deudas pendientes
    total_movimientos = ingresos + egresos
    if total_movimientos > 0:
        ratio_pendiente = pendientes / total_movimientos
        score -= (ratio_pendiente * 30)

    score = max(0.0, min(100.0, score))

    if score >= 75:
        return {"score": round(score, 1), "nivel": "Saludable", "color": "green"}
    elif score >= 50:
        return {"score": round(score, 1), "nivel": "Precaución", "color": "orange"}
    else:
        return {"score": round(score, 1), "nivel": "Crítico", "color": "red"}