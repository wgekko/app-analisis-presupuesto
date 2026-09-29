import streamlit as st
import pandas as pd
import unicodedata
from database.db_session import SessionLocal
from services.mov_service import MovimientoService
from services.export_service import ExportService

def render_page():
    st.subheader(":material/article: Reportes, Importación y Exportación")
    st.markdown("Filtra tu información financiera para exportarla, o importa masivamente nuevos registros.")
    
    db = SessionLocal()
    mov_service = MovimientoService(db)
    df = mov_service.get_all_df()
    db.close()
    
    # ==========================================
    # SECCIÓN 1: FILTROS Y EXPORTACIÓN
    # ==========================================
    st.markdown("### :material/move_group: Exportar Datos Financieros")
    
    if df.empty:
        st.info("No hay registros financieros en la base de datos para exportar.")
    else:
        # Filtros
        col1, col2 = st.columns(2)
        with col1:
            tipo_filtro = st.selectbox("Tipo de Movimiento", ["Todos", "Ingreso", "Egreso"])
        with col2:
            proyectos = ["Todos"] + list(df['proyecto'].unique())
            proy_filtro = st.selectbox("Proyecto", proyectos)

        # Aplicar filtros
        df_filtrado = df.copy()
        if tipo_filtro != "Todos":
            df_filtrado = df_filtrado[df_filtrado['tipo'] == tipo_filtro]
        if proy_filtro != "Todos":
            df_filtrado = df_filtrado[df_filtrado['proyecto'] == proy_filtro]

        # Previsualización
        st.dataframe(df_filtrado, width='stretch', hide_index=True)

        # Botones de descarga
        st.markdown("#### 📥 Descargar Reporte Filtrado")
        col_btn1, col_btn2, _ = st.columns([1, 1, 2])
        
        with col_btn1:
            csv_data = ExportService.to_csv(df_filtrado)
            st.download_button(
                label="Descargar CSV", 
                data=csv_data, 
                file_name="reporte_financiero.csv", 
                mime="text/csv", 
                width='stretch'
            )
            
        with col_btn2:
            excel_data = ExportService.to_excel(df_filtrado)
            st.download_button(
                label="Descargar Excel", 
                data=excel_data, 
                file_name="reporte_financiero.xlsx", 
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", 
                width='stretch'
            )

    st.markdown("---")
    
    # ==========================================
    # SECCIÓN 2: IMPORTACIÓN MASIVA
    # ==========================================
    st.markdown("### :material/breaking_news: Importación Masiva (Excel / CSV)")
    uploaded_file = st.file_uploader("Sube tu archivo con movimientos (Asegúrate de que coincida con las columnas de la app)", type=["csv", "xlsx"])
    
    if uploaded_file is not None:
        try:
            if uploaded_file.name.endswith('.csv'):
                df_import = pd.read_csv(uploaded_file)
            else:
                df_import = pd.read_excel(uploaded_file)
                
            # --- LIMPIEZA AUTOMÁTICA DE COLUMNAS ---
            nuevas_columnas = []
            for col in df_import.columns:
                # Pasar a minúsculas y quitar espacios en los bordes
                c = str(col).strip().lower() 
                # Quitar tildes (ej: Categoría -> categoria)
                c = ''.join(char for char in unicodedata.normalize('NFKD', c) if unicodedata.category(char) != 'Mn')
                # Forzar que variaciones de importe se reconozcan correctamente
                if 'importe' in c:
                    c = 'importe'
                nuevas_columnas.append(c)
            
            # Aplicar los nuevos nombres limpios al DataFrame
            df_import.columns = nuevas_columnas
            # --------------------------------------------
                
            st.success(f"Archivo cargado correctamente. Se leyeron {len(df_import)} registros.")
            st.dataframe(df_import.head(3), width='stretch')
            
            if st.button("Confirmar e Importar a la Base de Datos"):
                db_imp = SessionLocal()
                mov_imp_service = MovimientoService(db_imp)
                
                exitos = 0
                for _, row in df_import.iterrows():
                    # Intento de inserción segura extrayendo los datos ya normalizados
                    ok = mov_imp_service.create(
                        fecha=pd.to_datetime(row.get('fecha', pd.Timestamp.today())).date(),
                        tipo=str(row.get('tipo', 'Ingreso')).strip().capitalize(),
                        proyecto=str(row.get('proyecto', 'General')).strip(),
                        categoria=str(row.get('categoria', 'Otros')).strip(),
                        concepto=str(row.get('concepto', 'Importación masiva')).strip(),
                        importe=float(row.get('importe', 0.0)),
                        estado=str(row.get('estado', 'Pendiente')).strip().capitalize(),
                        observaciones=str(row.get('observaciones', ''))
                    )
                    if ok:
                        exitos += 1
                db_imp.close()
                st.success(f":material/check_box: Se importaron {exitos} de {len(df_import)} registros con éxito.")
                st.rerun()
                
        except Exception as e:
            st.error(f":material/error: Error al procesar el archivo: {e}")