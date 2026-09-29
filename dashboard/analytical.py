import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from components.charts import render_bar_chart, render_donut_chart
from analytics.metrics import (
    get_monthly_cashflow, 
    get_ratio_cobertura, 
    get_top_concepts,
    get_pareto_data,
    get_heatmap_matrix,
    get_multiproject_margin
)

def render_analytical_views(df: pd.DataFrame):
    """Dibuja el panel avanzado de BI con jerarquías, calor, Pareto y proyectos, analizando por Concepto y Proyecto."""
    
    tab_flujo, tab_jerarquia, tab_granular, tab_eficiencia = st.tabs([
        "Flujo & General", 
        "Visualizaciones Jerárquicas", 
        "Análisis Granular (80/20 & Calor)", 
        "Eficiencia Operativa"
    ])
    
    # ==========================================
    # PESTAÑA 1: FLUJO GENERAL
    # ==========================================
    with tab_flujo:
        col1, col2 = st.columns([2, 1])
        with col1:
            df_cashflow = get_monthly_cashflow(df)
            render_bar_chart(df=df_cashflow, x_col='mes', y_cols=['Ingreso', 'Egreso'], title="Flujo de Caja Mensual")
        with col2:
            # Agrupación por proyecto en lugar de categoría
            df_gastos = df[df['tipo'] == 'Egreso'].groupby('proyecto', as_index=False)['importe'].sum()
            if not df_gastos.empty:
                render_donut_chart(df=df_gastos, names_col='proyecto', values_col='importe', title="Distribución de Egresos por Proyecto")
            else:
                st.info("No hay egresos registrados.")

    # ==========================================
    # PESTAÑA 2: VISUALIZACIONES JERÁRQUICAS
    # ==========================================
    with tab_jerarquia:
        st.markdown(":material/tune: ### Estructura Jerárquica del Capital")
        st.caption("Haz clic en cualquier segmento para expandir y explorar los niveles internos.")
        
        col_j1, col_j2 = st.columns(2)
        
        with col_j1:
            st.markdown(":material/sunny: #### Sol Naciente (Tipo ➔ Proyecto ➔ Concepto)")
            fig_sunburst = px.sunburst(
                df,
                path=['tipo', 'proyecto', 'concepto'],
                values='importe',
                color='tipo',
                color_discrete_map={'Ingreso': '#02ab21', 'Egreso': '#ef553b'},
                title="Desglose Global de Fondos"
            )
            fig_sunburst.update_layout(margin=dict(t=30, l=0, r=0, b=0))
            st.plotly_chart(fig_sunburst, width='stretch')
            
        with col_j2:
            st.markdown(":material/map_search: #### Mapa de Árbol de Egresos (Proyecto ➔ Concepto)")
            df_egresos = df[df['tipo'] == 'Egreso']
            if not df_egresos.empty:
                fig_treemap = px.treemap(
                    df_egresos,
                    path=['proyecto', 'concepto'], 
                    values='importe',
                    color='importe',
                    color_continuous_scale='Reds',
                    title="Concentración del Presupuesto de Gastos"
                )
                fig_treemap.update_layout(margin=dict(t=30, l=0, r=0, b=0))
                st.plotly_chart(fig_treemap, width='stretch')
            else:
                st.info("No hay egresos registrados para generar el Treemap.")

    # ==========================================
    # PESTAÑA 3: ANÁLISIS GRANULAR Y PROYECTOS
    # ==========================================
    with tab_granular:
        # 1. Matriz de Calor Temporal
        st.markdown("### Matriz de Calor Temporal (Picos de Gasto)")
        dim_heatmap = st.radio("Eje Vertical de Análisis:", ["concepto", "proyecto"], horizontal=True, format_func=lambda x: x.capitalize())
        
        pivot_heatmap = get_heatmap_matrix(df, tipo="Egreso", dimension=dim_heatmap)
        if not pivot_heatmap.empty:
            fig_heatmap = px.imshow(
                pivot_heatmap,
                labels=dict(x="Mes", y=dim_heatmap.capitalize(), color="Monto ($)"),
                text_auto=",f",
                color_continuous_scale="YlOrRd",
                aspect="auto"
            )
            fig_heatmap.update_layout(title=f"Intensidad de Egresos por {dim_heatmap.capitalize()} y Mes")
            st.plotly_chart(fig_heatmap, width='stretch')
        else:
            st.info("Datos insuficientes para la matriz de calor.")

        st.markdown("---")
        
        col_g1, col_g2 = st.columns(2)
        
        # 2. Análisis de Pareto (80/20)
        with col_g1:
            st.markdown(":material/quick_reference_all: ### Diagrama de Pareto (Regla 80/20)")
            df_pareto = get_pareto_data(df, tipo="Egreso")
            
            if not df_pareto.empty:
                fig_pareto = make_subplots(specs=[[{"secondary_y": True}]])
                
                # Barras de monto
                fig_pareto.add_trace(
                    go.Bar(x=df_pareto['concepto'], y=df_pareto['importe'], name="Monto ($)", marker_color='#ef553b'),
                    secondary_y=False
                )
                # Línea de % acumulado
                fig_pareto.add_trace(
                    go.Scatter(x=df_pareto['concepto'], y=df_pareto['pct_acumulado'], name="% Acumulado", mode="lines+markers", line=dict(color="#4E80E4", width=3)),
                    secondary_y=True
                )
                # Línea límite del 80%
                fig_pareto.add_hline(y=80, line_dash="dash", line_color="orange", annotation_text="80% Crítico", secondary_y=True)
                
                fig_pareto.update_layout(
                    title="Conceptos que Concentran el Gasto",
                    xaxis_title="Concepto",
                    showlegend=False
                )
                fig_pareto.update_yaxes(title_text="Monto Total ($)", secondary_y=False)
                fig_pareto.update_yaxes(title_text="% Acumulado", range=[0, 105], secondary_y=True)
                
                st.plotly_chart(fig_pareto, width='stretch')
            else:
                st.info("Sin registros de egresos para el Pareto.")
                
        # 3. Comparativa Multi-Proyecto
        with col_g2:
            st.markdown(":material/dashboard_2: ### Margen Neto Multi-Proyecto")
            df_mp = get_multiproject_margin(df)
            
            if not df_mp.empty:
                fig_mp = px.bar(
                    df_mp,
                    x='mes',
                    y='margen_neto',
                    color='proyecto',
                    barmode='group',
                    title="Rentabilidad Mensual Comparada (Ingresos - Egresos)",
                    labels={'margen_neto': 'Margen Neto ($)', 'mes': 'Mes', 'proyecto': 'Proyecto'}
                )
                st.plotly_chart(fig_mp, width='stretch')
            else:
                st.info("Sin datos multi-proyecto para comparar.")

    # ==========================================
    # PESTAÑA 4: EFICIENCIA OPERATIVA
    # ==========================================
    # with tab_eficiencia:
    #     cobertura = get_ratio_cobertura(df)
    #     ratio_val = cobertura["ratio"]
        
    #     col_m1, col_m2 = st.columns([1, 2])
    #     with col_m1:
    #         color = "normal" if ratio_val >= 100 else "inverse"
    #         st.metric(label="Ratio de Cobertura de Egresos", value=f"{ratio_val:.1f}%", delta="Ingresos vs Egresos", delta_color=color)
            
    #         if ratio_val >= 100:
    #             st.success(":material/check_box: **Sostenible:** Los ingresos cubren el 100% de los egresos operativos.")
    #         else:
    #             st.error(":material/warning: **Riesgo:** Los ingresos actuales no alcanzan a cubrir la totalidad de egresos.")
                
    #     with col_m2:
    #         st.markdown(":material/top_panel_close: #### Top Conceptos Financieros")
    #         tipo_filtro = st.radio("Filtrar Top Conceptos por:", ["Egreso", "Ingreso"], horizontal=True)
    #         df_top = get_top_concepts(df, tipo=tipo_filtro, top_n=10)
            
    #         if not df_top.empty:
    #             df_mostrar = df_top.copy()
    #             # Eliminamos la columna de categoría (índice 1) generada por get_top_concepts
    #             if len(df_mostrar.columns) >= 4:
    #                 df_mostrar = df_mostrar.drop(df_mostrar.columns[1], axis=1)
                
    #             df_mostrar.columns = ["Concepto", "N° Transacciones", "Monto Total ($)"]
                
    #             fig_top = px.bar(
    #                 df_mostrar, x="Monto Total ($)", y="Concepto", orientation="h",
    #                 title=f"Top 10 Conceptos con Mayor Impacto ({tipo_filtro}s)"
    #             )
    #             fig_top.update_layout(yaxis={'categoryorder': 'total ascending'})
    #             st.plotly_chart(fig_top, width='stretch')
    #             st.dataframe(df_mostrar, width='stretch', hide_index=True)
    #         else:
    #             st.info(f"No hay registros de tipo {tipo_filtro}.")
    # ==========================================
    # PESTAÑA 4: EFICIENCIA OPERATIVA
    # ==========================================
    with tab_eficiencia:
        cobertura = get_ratio_cobertura(df)
        ratio_val = cobertura["ratio"]
        
        col_m1, col_m2 = st.columns([1, 2])
        with col_m1:
            color = "normal" if ratio_val >= 100 else "inverse"
            st.metric(label="Ratio de Cobertura de Egresos", value=f"{ratio_val:.1f}%", delta="Ingresos vs Egresos", delta_color=color)
            
            if ratio_val >= 100:
                st.success(":material/check_box: **Sostenible:** Los ingresos cubren el 100% de los egresos operativos.")
            else:
                st.error(":material/warning: **Riesgo:** Los ingresos actuales no alcanzan a cubrir la totalidad de egresos.")
                
        with col_m2:
            st.markdown(":material/top_panel_close: #### Top Conceptos Financieros")
            tipo_filtro = st.radio("Filtrar Top Conceptos por:", ["Egreso", "Ingreso"], horizontal=True)
            
            # 1. Normalizar la columna para evitar errores por espacios (ej: "Ingreso " -> "Ingreso")
            df_temp = df.copy()
            df_temp['tipo_limpio'] = df_temp['tipo'].astype(str).str.strip().str.capitalize()
            
            df_filtrado = df_temp[df_temp['tipo_limpio'] == tipo_filtro]
            
            if not df_filtrado.empty:
                # 2. Agrupación directa SOLO por 'concepto' (evita que Pandas borre filas con categorías vacías)
                df_agrupado = df_filtrado.groupby('concepto', as_index=False).agg(
                    transacciones=('importe', 'count'),
                    monto_total=('importe', 'sum')
                )
                
                # 3. Ordenar, sacar el top 10 y renombrar columnas
                df_mostrar = df_agrupado.sort_values(by='monto_total', ascending=False).head(10)
                df_mostrar.columns = ["Concepto", "N° Transacciones", "Monto Total ($)"]
                
                fig_top = px.bar(
                    df_mostrar, 
                    x="Monto Total ($)", 
                    y="Concepto", 
                    color="Concepto", 
                    orientation="h",
                    text_auto=".2s",
                    title=f"Top 10 Conceptos con Mayor Impacto ({tipo_filtro}s)"
                )
                
                # Diseño de bordes para identificar barras
                fig_top.update_traces(
                    marker_line_color="#0D1B2A",  
                    marker_line_width=2,          
                    textfont_color="#FFFFFF"      
                )
                
                fig_top.update_layout(
                    yaxis={'categoryorder': 'total ascending'},
                    showlegend=False
                )
                
                st.plotly_chart(fig_top, width='stretch')
                st.dataframe(df_mostrar, width='stretch', hide_index=True)
            else:
                st.info(f"No hay registros válidos de tipo {tipo_filtro}.")