import streamlit as st

def render_kpi(titulo: str, valor: float, prefijo: str = "$", delta: str = None, color_delta: str = "normal"):
    """
    Renderiza una tarjeta KPI utilizando st.metric.
    color_delta puede ser 'normal', 'inverse' o 'off'.
    """
    st.metric(
        label=titulo, 
        value=f"{prefijo}{valor:,.2f}", 
        delta=delta, 
        delta_color=color_delta
    )