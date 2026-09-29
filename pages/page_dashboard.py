import streamlit as st
import pandas as pd
from database.db_session import SessionLocal
from services.mov_service import MovimientoService
from dashboard.executive import render_executive_summary
from dashboard.analytical import render_analytical_views
from ml_models.risk_scorer import calcular_score_riesgo

def render_page():
    st.subheader(":material/dashboard: Panel de Control (Dashboard)")
    st.markdown("Visión general del estado financiero de tu empresa y alertas proactivas.")
    
    db = SessionLocal()
    mov_service = MovimientoService(db)
    df = mov_service.get_all_df()
    db.close()
    
    if df.empty:
        st.info("No hay datos suficientes para mostrar en el Dashboard. Registra movimientos primero.")
        return

    # Asegurar formato de fecha para cálculos temporales
    df['fecha'] = pd.to_datetime(df['fecha'])

    # ==========================================
    # NUEVO: CENTRO DE ALERTAS PROACTIVO
    # ==========================================
    alertas = []

    # --- ALERTA 1: SCORE DE RIESGO CRÍTICO (< 50) ---
    score_data = calcular_score_riesgo(df)
    if score_data['score'] < 50:
        alertas.append({
            "tipo": "error",
            "mensaje": f":material/readiness_score: **Score de Riesgo Crítico ({score_data['score']}/100):** Nivel {score_data['nivel']}. Tu liquidez o relación de egresos requiere atención urgente."
        })

    # --- ALERTA 2: GASTOS MES ACTUAL > 20% DEL PROMEDIO HISTÓRICO ---
    df_egresos = df[df['tipo'] == 'Egreso'].copy()
    if not df_egresos.empty:
        df_egresos['mes_anio'] = df_egresos['fecha'].dt.to_period('M')
        
        # Agrupar egresos por mes y categoría
        cat_mensual = df_egresos.groupby(['mes_anio', 'categoria'])['importe'].sum().reset_index()
        
        # Promedio histórico mensual por categoría
        promedio_historico = cat_mensual.groupby('categoria')['importe'].mean()
        
        # Egresos del último mes registrado
        ultimo_mes = cat_mensual['mes_anio'].max()
        gastos_ultimo_mes = cat_mensual[cat_mensual['mes_anio'] == ultimo_mes]
        
        for _, row in gastos_ultimo_mes.iterrows():
            cat = row['categoria']
            monto_actual = row['importe']
            monto_prom = promedio_historico.get(cat, 0)
            
            # Si el gasto actual supera el promedio en más del 20%
            if monto_prom > 0 and monto_actual > (monto_prom * 1.20):
                exceso_pct = ((monto_actual - monto_prom) / monto_prom) * 100
                alertas.append({
                    "tipo": "warning",
                    "mensaje": f":material/graph_2: **Desviación de Presupuesto:** En la categoría **{cat}** has gastado **${monto_actual:,.2f}** este mes, un **{exceso_pct:.1f}% superior** a tu promedio histórico (${monto_prom:,.2f})."
                })

    # --- ALERTA 3: MOVIMIENTOS PENDIENTES CON MÁS DE 30 DÍAS ---
    hoy = pd.Timestamp.today()
    if 'estado' in df.columns:
        pendientes_vencidos = df[
            (df['estado'] == 'Pendiente') & 
            ((hoy - df['fecha']).dt.days > 30)
        ]
        
        if not pendientes_vencidos.empty:
            cant_vencidos = len(pendientes_vencidos)
            monto_vencido = pendientes_vencidos['importe'].sum()
            alertas.append({
                "tipo": "warning",
                "mensaje": f":material/account_box: **Cuentas Pendientes Vencidas:** Tienes **{cant_vencidos} registro(s) pendiente(s)** con más de 30 días de antigüedad por un total de **${monto_vencido:,.2f}**."
            })

    # Renderizar el bloque de alertas si existen
    if alertas:
        st.markdown(":material/warning: ### Centro de Alertas y Notificaciones")
        for alerta in alertas:
            if alerta['tipo'] == 'error':
                st.error(alerta['mensaje'])
            else:
                st.warning(alerta['mensaje'])
        st.markdown("---")
    else:
        st.success(":material/check_box: **Todo bajo control:** No se detectaron anomalías, desviaciones de presupuesto ni cuentas vencidas.")
        st.markdown("---")

    st.markdown("---")

    # 1. Tarjetas KPI Superiores (Módulo externo)
    render_executive_summary(df)
    
    st.markdown("---")
    
    # 2. Gráficos y Tendencias (Módulo externo)
    render_analytical_views(df)
