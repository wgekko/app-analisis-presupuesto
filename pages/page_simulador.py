import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import date
from dateutil.relativedelta import relativedelta
from database.db_session import SessionLocal
from services.mov_service import MovimientoService
from components.kpi_cards import render_kpi
from ml_models.risk_scorer import calcular_score_riesgo

def render_page():
    st.subheader(":material/simulation: Simulador Financiero de Escenarios")
    st.markdown("Analiza tu nivel de riesgo actual y proyecta escenarios macroeconómicos a corto y largo plazo.")
    
    # 1. Carga de datos base
    db = SessionLocal()
    mov_service = MovimientoService(db)
    df = mov_service.get_all_df()
    db.close()
    
    if df.empty:
        st.warning("No hay suficientes datos. Registra movimientos para establecer un punto de partida.")
        return
        
    # --- INTEGRACIÓN DEL MODELO DE RIESGO ---
    score_actual = calcular_score_riesgo(df)
    st.info(f":material/readiness_score: **Score de Riesgo Actual:** {score_actual['score']}/100 ({score_actual['nivel']})")
    
    # Crear pestañas para no perder el código anterior y sumar el nuevo
    tab_proyeccion, tab_inmediato = st.tabs([
        ":material/calendar_month: Proyección a 12 Meses", 
        ":material/calendar_check: Impacto Inmediato (What-If)"
    ])

    # ==========================================
    # PESTAÑA 1: PROYECCIÓN A 12 MESES (CÓDIGO ANTERIOR)
    # ==========================================
    with tab_proyeccion:
        # Calcular promedios mensuales actuales
        df_fechas = df.copy()
        df_fechas['fecha'] = pd.to_datetime(df_fechas['fecha'])
        df_fechas['mes_anio'] = df_fechas['fecha'].dt.to_period('M')
        meses_activos = df_fechas['mes_anio'].nunique()
        meses_activos = meses_activos if meses_activos > 0 else 1

        ingreso_mensual_base = df[df['tipo'] == 'Ingreso']['importe'].sum() / meses_activos
        egreso_mensual_base = df[df['tipo'] == 'Egreso']['importe'].sum() / meses_activos
        
        st.markdown(f"**Punto de partida (Promedio mensual):** Ingresos: ${ingreso_mensual_base:,.2f} / Egresos: ${egreso_mensual_base:,.2f}")

        st.markdown("### :material/settings: Parámetros de Simulación (Anual)")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.caption("Crecimiento de Ingresos (%)")
            var_ingresos_proy = st.slider("Aumento esperado en ventas/cobros", min_value=-50.0, max_value=100.0, value=10.0, step=1.0)
        with col2:
            st.caption("Optimización de Gastos (%)")
            var_gastos_proy = st.slider("Reducción de costos operativos", min_value=-50.0, max_value=50.0, value=5.0, step=1.0, help="Valores positivos = ahorro. Valores negativos = aumento de gastos.")
        with col3:
            st.caption("Inflación Esperada (%)")
            var_inflacion_proy = st.slider("Impacto inflacionario sobre gastos", min_value=0.0, max_value=150.0, value=5.0, step=1.0)

        # Motor de Simulación (Cálculo a 12 meses)
        meses_proyeccion = 12
        fechas = [(date.today() + relativedelta(months=i)).strftime('%Y-%m') for i in range(1, meses_proyeccion + 1)]
        
        tasa_ingreso_mes = (var_ingresos_proy / 100) / 12
        tasa_gasto_mes = ((-var_gastos_proy) / 100) / 12
        tasa_inflacion_mes = (var_inflacion_proy / 100) / 12

        datos_simulacion = []
        ingreso_acum_real = ingreso_mensual_base
        egreso_acum_real = egreso_mensual_base
        ingreso_acum_sim = ingreso_mensual_base
        egreso_acum_sim = egreso_mensual_base
        
        for mes in fechas:
            ingreso_acum_real *= (1 + 0.0) 
            egreso_acum_real *= (1 + (0.03/12))
            balance_real = ingreso_acum_real - egreso_acum_real
            
            ingreso_acum_sim *= (1 + tasa_ingreso_mes)
            egreso_acum_sim *= (1 + tasa_gasto_mes + tasa_inflacion_mes)
            balance_sim = ingreso_acum_sim - egreso_acum_sim
            
            datos_simulacion.append({
                "Mes": mes,
                "Balance Base": balance_real,
                "Balance Simulado": balance_sim
            })

        df_sim = pd.DataFrame(datos_simulacion)

        # Visualización Comparativa a 12 meses
        st.markdown("### :material/finance_mode: Proyección del Balance Neto (12 Meses)")
        
        fig = go.Figure()
        fig.add_trace(go.Bar(x=df_sim['Mes'], y=df_sim['Balance Base'], name='Escenario Base (Sin cambios)', marker_color='lightgray'))
        fig.add_trace(go.Bar(x=df_sim['Mes'], y=df_sim['Balance Simulado'], name='Escenario Simulado', marker_color='#02ab21'))
        
        fig.update_layout(barmode='group', xaxis_title="Meses", yaxis_title="Balance Neto ($)")
        st.plotly_chart(fig, width='stretch')

        # Impacto Final
        balance_final_base = df_sim.iloc[-1]['Balance Base']
        balance_final_sim = df_sim.iloc[-1]['Balance Simulado']
        diferencia = balance_final_sim - balance_final_base
        
        st.markdown("### :material/data_exploration: Conclusión al final del Año")
        c1, c2, c3 = st.columns(3)
        with c1:
            render_kpi("Balance Final Base", balance_final_base, color_delta="off")
        with c2:
            render_kpi("Balance Final Simulado", balance_final_sim, color_delta="off")
        with c3:
            color_d = "normal" if diferencia >= 0 else "inverse"
            render_kpi("Impacto de la Estrategia", diferencia, delta="Diferencia a favor" if diferencia >=0 else "Pérdida", color_delta=color_d)

    # ==========================================
    # PESTAÑA 2: IMPACTO INMEDIATO (CÓDIGO NUEVO)
    # ==========================================
    with tab_inmediato:
        ingresos_actuales = df[df['tipo'] == 'Ingreso']['importe'].sum()
        egresos_actuales = df[df['tipo'] == 'Egreso']['importe'].sum()

        col_sliders, col_metricas = st.columns([1, 2])
        
        with col_sliders:
            st.markdown("#### :material/dashboard_2_gear:  Variables Inmediatas")
            var_ingresos = st.slider("Variación Esperada de Ingresos (%)", min_value=-50, max_value=100, value=0, step=5, key="vi_inm")
            var_egresos = st.slider("Variación Esperada de Gastos (%)", min_value=-30, max_value=150, value=0, step=5, key="ve_inm")
            
        with col_metricas:
            ingresos_sim = ingresos_actuales * (1 + var_ingresos / 100)
            egresos_sim = egresos_actuales * (1 + var_egresos / 100)
            balance_sim = ingresos_sim - egresos_sim
            balance_actual = ingresos_actuales - egresos_actuales
            
            m1, m2, m3 = st.columns(3)
            m1.metric("Ingresos Proyectados", f"${ingresos_sim:,.2f}", f"{var_ingresos}%")
            m2.metric("Egresos Proyectados", f"${egresos_sim:,.2f}", f"{var_egresos}%", delta_color="inverse")
            m3.metric("Balance Proyectado", f"${balance_sim:,.2f}", f"${balance_sim - balance_actual:,.2f}")

        st.markdown("---")
        
        # Gráfico comparativo de totales
        fig_inmediato = go.Figure(data=[
            go.Bar(name='Escenario Actual', x=['Ingresos', 'Egresos'], y=[ingresos_actuales, egresos_actuales], marker_color='#b0c4de'),
            go.Bar(name='Escenario Simulado', x=['Ingresos', 'Egresos'], y=[ingresos_sim, egresos_sim], marker_color=['#02ab21', '#ef553b'])
        ])
        fig_inmediato.update_layout(barmode='group', title="Comparativa de Estructura de Costos Inmediata", margin=dict(t=40, b=0))
        st.plotly_chart(fig_inmediato, width='stretch')