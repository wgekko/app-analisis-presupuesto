from datetime import date, timedelta
import streamlit as st
import pandas as pd
from components.kpi_cards import render_kpi
from analytics.metrics import get_core_kpis


def get_kpis(df: pd.DataFrame) -> dict:
    """Calcula los indicadores clave de rendimiento (KPIs) del DataFrame."""
    if df.empty:
        return {"ingresos": 0.0, "egresos": 0.0, "balance": 0.0, "pendientes": 0.0}
    
    ingresos = df[df['tipo'] == 'Ingreso']['importe'].sum()
    egresos = df[df['tipo'] == 'Egreso']['importe'].sum()
    balance = ingresos - egresos
    pendientes = df[df['estado'] == 'Pendiente']['importe'].sum()

    return {
        "ingresos": float(ingresos),
        "egresos": float(egresos),
        "balance": float(balance),
        "pendientes": float(pendientes)
    }

def get_alertas_vencimientos(df: pd.DataFrame) -> pd.DataFrame:
    """Filtra los movimientos 'Pendientes' que vencen en los próximos 10 días."""
    if df.empty:
        return pd.DataFrame()
    
    hoy = pd.to_datetime(date.today())
    df_copy = df.copy()
    df_copy['fecha_dt'] = pd.to_datetime(df_copy['fecha'])
    
    # Condición: Pendientes y fecha entre hoy y 10 días en el futuro
    mask = (df_copy['estado'] == 'Pendiente') & (df_copy['fecha_dt'] >= hoy) & (df_copy['fecha_dt'] <= hoy + timedelta(days=10))
    
    alertas = df_copy[mask].drop(columns=['fecha_dt']) # Limpiamos la columna auxiliar
    return alertas


def render_executive_summary(df: pd.DataFrame):
    """Dibuja la cinta superior del Dashboard con los totales."""
    kpis = get_core_kpis(df)
    
    col1, col2, col3 = st.columns(3)
    with col1:
        render_kpi("Ingresos Totales", kpis["ingresos"], delta="Acumulado")
    with col2:
        render_kpi("Egresos Totales", kpis["egresos"], delta="Acumulado", color_delta="inverse")
    with col3:
        color = "normal" if kpis["balance"] >= 0 else "inverse"
        render_kpi("Balance Neto", kpis["balance"], delta="Rentabilidad", color_delta=color)