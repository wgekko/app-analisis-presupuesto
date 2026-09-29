import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from database.db_session import SessionLocal
from services.mov_service import MovimientoService
from ml_models.insights_gen import generar_insights_texto
from ml_models.anomalies import detectar_anomalias
from ml_models.forecasting import proyectar_tendencia
from ml_models.clustering import agrupar_comportamiento_gastos

def render_page():
    st.subheader(":material/psychology: Inteligencia Artificial y Análisis Avanzado")
    st.markdown("Modelos predictivos, segmentación K-Means, proyecciones granulares y detección de anomalías aplicados a tus finanzas.")
    
    # 1. Carga de datos base
    db = SessionLocal()
    mov_service = MovimientoService(db)
    df = mov_service.get_all_df()
    db.close()
    
    if df.empty:
        st.info("No hay datos suficientes para ejecutar los modelos de Inteligencia Artificial.")
        return

    # 2. Navegación por Pestañas
    tab_clustering, tab_insights, tab_proyeccion, tab_anomalias = st.tabs([
        ":material/bubble_chart: Segmentación (Clustering)", 
        ":material/lightbulb: Insights Automáticos", 
        ":material/area_chart: Proyecciones Granulares", 
        ":material/warning: Detección de Anomalías"
    ])
    
    # ==========================================
    # PESTAÑA 1: SEGMENTACIÓN DE GASTOS (K-MEANS)
    # ==========================================
    with tab_clustering:
        st.markdown("### Segmentación Inteligente de Gastos")
        st.markdown("El algoritmo evalúa la relación entre la frecuencia de uso y el impacto financiero de cada categoría.")

        if len(df[df['tipo'] == 'Egreso']) < 3:
            st.warning("No hay suficientes datos de egresos para ejecutar el modelo de clustering (se requieren al menos 3 registros).")
        else:
            df_clusters = agrupar_comportamiento_gastos(df)

            if df_clusters.empty:
                st.info("No se pudieron generar clústeres con la información actual.")
            else:
                col_chart, col_data = st.columns([2, 1])

                with col_chart:
                    # Mapa de colores semántico para los perfiles
                    color_map = {
                        'Gasto Bajo/Controlado': '#02ab21',  # Verde
                        'Gasto Medio/Frecuente': '#ffb703',  # Amarillo
                        'Gasto Alto/Crítico': '#ef553b'      # Rojo
                    }

                    fig_scatter = px.scatter(
                        df_clusters,
                        x='frecuencia',
                        y='monto_total',
                        color='perfil_gasto',
                        size='monto_total',
                        hover_name='categoria',
                        color_discrete_map=color_map,
                        labels={
                            'frecuencia': 'Frecuencia de Transacciones',
                            'monto_total': 'Monto Total Consumido ($)',
                            'perfil_gasto': 'Perfil Asignado'
                        }
                    )
                    fig_scatter.add_hline(y=df_clusters['monto_total'].mean(), line_dash="dot", line_color="gray", annotation_text="Monto Promedio")
                    fig_scatter.add_vline(x=df_clusters['frecuencia'].mean(), line_dash="dot", line_color="gray", annotation_text="Frecuencia Promedio")
                    
                    fig_scatter.update_layout(margin=dict(t=20, b=0), legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1))
                    st.plotly_chart(fig_scatter, width='stretch')

                with col_data:
                    st.markdown("#### Detalle por Categoría")
                    df_display = df_clusters[['categoria', 'frecuencia', 'monto_total', 'perfil_gasto']].copy()
                    df_display['monto_total'] = df_display['monto_total'].apply(lambda x: f"${x:,.2f}")
                    st.dataframe(df_display, hide_index=True, width='stretch')

                st.markdown("---")
                st.markdown("#### Conclusiones del Algoritmo")
                
                criticos = df_clusters[df_clusters['perfil_gasto'] == 'Gasto Alto/Crítico']['categoria'].tolist()
                frecuentes = df_clusters[df_clusters['perfil_gasto'] == 'Gasto Medio/Frecuente']['categoria'].tolist()

                if criticos:
                    st.error(f"**Atención inmediata:** Las categorías **{', '.join(criticos)}** representan tu zona crítica. Concentran el mayor drenaje de capital.")
                if frecuentes:
                    st.warning(f"**Efecto de Gasto Hormiga/Recurrente:** Tienes alta transaccionalidad en **{', '.join(frecuentes)}**. El volumen acumulado por su repetición impacta tu liquidez.")
                if not criticos and not frecuentes:
                    st.success("Tus patrones de gasto actuales se mantienen en niveles bajos y controlados. ¡Excelente trabajo financiero!")

    # ==========================================
    # PESTAÑA 2: INSIGHTS AUTOMÁTICOS
    # ==========================================
    with tab_insights:
        st.markdown("### Análisis del Comportamiento Financiero")
        insights = generar_insights_texto(df)
        if not insights:
            st.info("No se generaron observaciones adicionales para los datos registrados.")
        else:
            for insight in insights:
                st.success(insight)
            
    # ==========================================
    # PESTAÑA 3: PROYECCIONES CON FILTRADO GRANULAR
    # ==========================================
    with tab_proyeccion:
        st.markdown("### Proyección de Tendencia por Segmento")
        st.markdown("Selecciona los parámetros para simular el comportamiento futuro de tus cuentas.")
        
        col_f1, col_f2, col_f3 = st.columns(3)
        with col_f1:
            filtro_tipo = st.selectbox("Tipo de Movimiento", ["Egreso", "Ingreso"])
        with col_f2:
            proyectos_disponibles = ["Todos"] + list(df['proyecto'].unique())
            filtro_proyecto = st.selectbox("Proyecto Específico", proyectos_disponibles)
        with col_f3:
            meses_proyeccion = st.slider("Meses a Proyectar", min_value=1, max_value=12, value=3)
            
        # Filtrar DataFrame antes de calcular proyección
        df_filtrado = df[df['tipo'] == filtro_tipo].copy()
        if filtro_proyecto != "Todos":
            df_filtrado = df_filtrado[df_filtrado['proyecto'] == filtro_proyecto]
            
        if df_filtrado.empty:
            st.warning(f"No hay registros suficientes para el filtro seleccionado ({filtro_tipo} - Proyecto: {filtro_proyecto}).")
        else:
            df_filtrado['fecha'] = pd.to_datetime(df_filtrado['fecha'])
            df_hist_mensual = df_filtrado.groupby(df_filtrado['fecha'].dt.to_period('M'))['importe'].sum().reset_index()
            df_hist_mensual['fecha'] = df_hist_mensual['fecha'].dt.to_timestamp()
            
            # Ejecutar modelo de proyección
            df_pred = proyectar_tendencia(df_filtrado, meses_futuros=meses_proyeccion)
            
            if df_pred.empty:
                st.warning("Se necesitan al menos 3 meses de registros históricos en este segmento para calcular la proyección.")
            else:
                fig_proy = go.Figure()
                
                # Histórico
                fig_proy.add_trace(go.Scatter(
                    x=df_hist_mensual['fecha'], 
                    y=df_hist_mensual['importe'],
                    mode='lines+markers',
                    name=f'Histórico de {filtro_tipo}s',
                    line=dict(color='#02ab21', width=3)
                ))
                
                # Proyección IA
                fig_proy.add_trace(go.Scatter(
                    x=df_pred['fecha'], 
                    y=df_pred['prediccion'],
                    mode='lines+markers',
                    name=f'Proyección IA ({meses_proyeccion} meses)',
                    line=dict(color='orange', width=3, dash='dash')
                ))
                
                titulo_grafico = f"Proyección de {filtro_tipo}s" + (f" - Proyecto: {filtro_proyecto}" if filtro_proyecto != "Todos" else " (Global)")
                fig_proy.update_layout(
                    title=titulo_grafico,
                    xaxis_title="Mes",
                    yaxis_title="Monto ($)",
                    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
                )
                st.plotly_chart(fig_proy, width='stretch')
                
                total_proyectado = df_pred['prediccion'].sum()
                st.info(f":material/info: **Resumen de la Simulación:** Se proyecta un {filtro_tipo.lower()} acumulado de **${total_proyectado:,.2f}** para los próximos {meses_proyeccion} meses en el segmento seleccionado.")

    # ==========================================
    # PESTAÑA 4: DETECCIÓN DE ANOMALÍAS
    # ==========================================
    with tab_anomalias:
        st.markdown("### Detección de Gastos Atípicos (Outliers)")
        df_anomalias = detectar_anomalias(df)
        if df_anomalias.empty:
            st.info(":material/beenhere: No se detectaron anomalías o egresos fuera del patrón normal.")
        else:
            st.warning(f":material/sd_card_alert: Se detectaron {len(df_anomalias)} movimientos con comportamientos inusuales:")
            st.dataframe(df_anomalias[['fecha', 'proyecto', 'categoria', 'concepto', 'importe']], width='stretch')