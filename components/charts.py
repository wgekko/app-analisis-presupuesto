import streamlit as st
import plotly.express as px
import pandas as pd

def render_bar_chart(df: pd.DataFrame, x_col: str, y_cols: list, title: str):
    """Genera un gráfico de barras agrupadas."""
    if df.empty:
        st.info("No hay datos para graficar.")
        return
    fig = px.bar(df, x=x_col, y=y_cols, barmode='group', title=title)
    fig.update_layout(xaxis_title="", yaxis_title="Monto ($)")
    st.plotly_chart(fig, width='stretch')

def render_donut_chart(df: pd.DataFrame, names_col: str, values_col: str, title: str):
    """Genera un gráfico de dona (Pastel con hueco)."""
    if df.empty:
        st.info("No hay datos para graficar.")
        return
    fig = px.pie(df, names=names_col, values=values_col, hole=0.4, title=title)
    st.plotly_chart(fig, width='stretch')