import pandas as pd

def generar_insights_texto(df: pd.DataFrame) -> list:
    """
    Analiza el DataFrame y genera un listado de conclusiones y alertas financieras.
    """
    if df.empty:
        return ["No hay suficientes datos para generar insights analíticos."]
    
    insights = []
    ingresos = df[df['tipo'] == 'Ingreso']['importe'].sum()
    egresos = df[df['tipo'] == 'Egreso']['importe'].sum()
    
    # Balance general
    if ingresos > egresos:
        insights.append(":material/done_all: **Salud Financiera Positiva:** Tus ingresos totales superan cómodamente a tus egresos actuales.")
    else:
        insights.append(":material/warning:  **Alerta de Déficit:** Tus egresos superan o igualan a tus ingresos. Se recomienda un plan de contención de gastos.")
        
    # Categoría con mayor salida de dinero
    df_egresos = df[df['tipo'] == 'Egreso']
    if not df_egresos.empty:
        gasto_por_cat = df_egresos.groupby('categoria')['importe'].sum()
        top_cat = gasto_por_cat.idxmax()
        top_monto = gasto_por_cat.max()
        pct_top = (top_monto / egresos) * 100 if egresos > 0 else 0
        insights.append(f":material/fact_check: **Concentración de Gastos:** La categoría **'{top_cat}'** concentra el mayor volumen de egresos (${top_monto:,.2f}, {pct_top:.1f}% del total).")
        
    # Estado de pendientes
    pendientes = df[df['estado'] == 'Pendiente']
    if not pendientes.empty:
        total_pend = pendientes['importe'].sum()
        insights.append(f":material/: **Liquidez Comprometida:** Tienes {len(pendientes)} movimientos en estado 'Pendiente' por un valor total de ${total_pend:,.2f}.")
        
    return insights

