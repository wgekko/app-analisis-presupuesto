import streamlit as st
import pandas as pd
from st_aggrid import AgGrid, GridOptionsBuilder, ColumnsAutoSizeMode
from database.db_session import SessionLocal
from services.mov_service import MovimientoService
from utils.validators import validate_amount, validate_required_field

def render_page():
    st.subheader(":material/wallet: Gestión de Movimientos Financieros")
    st.markdown("Registra, consulta y administra los ingresos y egresos de tu presupuesto.")
    
    db = SessionLocal()
    mov_service = MovimientoService(db)
    
    # --- SECCIÓN 1: FORMULARIO DE REGISTRO CON VALIDACIÓN ---
    with st.expander("Registrar Nuevo Movimiento", expanded=False):
        with st.form("form_nuevo_movimiento", clear_on_submit=True):
            col1, col2 = st.columns(2)
            with col1:
                fecha = st.date_input("Fecha")
                tipo = st.selectbox("Tipo", ["Ingreso", "Egreso"])
                proyecto = st.selectbox("Proyecto", ["General", "Las Verbenas", "Lindos Pagos"])
                categoria = st.selectbox("Categoría", ["Ventas", "Servicios", "Viáticos", "Insumos", "Otros"])
                
            with col2:
                concepto = st.text_input("Concepto / Descripción")
                importe_input = st.text_input("Importe ($)", placeholder="0.00")
                estado = st.selectbox("Estado", ["Completado", "Pendiente"])
                observaciones = st.text_area("Observaciones (Opcional)")
                
            submitted = st.form_submit_button("Guardar en Base de Datos", width='stretch')
            
            if submitted:
                # 1. Validar campo obligatorio
                if not validate_required_field(concepto):
                    st.error(":material/warning: El campo 'Concepto' es obligatorio.")
                else:
                    # 2. Validar importe numérico y positivo
                    is_valid_amt, importe_val = validate_amount(importe_input)
                    if not is_valid_amt:
                        st.error(":material/warning: El importe debe ser un número válido mayor a 0.")
                    else:
                        # 3. Inserción segura mediante el servicio
                        ok = mov_service.create(
                            fecha=fecha,
                            tipo=tipo,
                            proyecto=proyecto,
                            categoria=categoria,
                            concepto=concepto.strip(),
                            importe=importe_val,
                            estado=estado,
                            observaciones=observaciones.strip()
                        )
                        if ok:
                            st.success(":material/check_box: ¡Movimiento registrado con éxito!")
                            st.rerun()
                        else:
                            st.error(":material/error: Error al guardar el movimiento en la base de datos.")

    st.markdown("---")
    
    # --- SECCIÓN 2: HISTORIAL Y TABLA INTERACTIVA ---
    st.markdown(":material/history_edu: ### Historial Financiero")
    df_movimientos = mov_service.get_all_df()
    db.close()

    if df_movimientos.empty:
        st.info("No hay movimientos registrados actualmente. Usa el botón de arriba para agregar el primero.")
    else:
        # Conversión de fechas a texto para evitar conflictos visuales en AgGrid ([object Object])
        df_mostrar = df_movimientos.copy()
        if 'fecha' in df_mostrar.columns:
            df_mostrar['fecha'] = df_mostrar['fecha'].astype(str)
        if 'fecha_creacion' in df_mostrar.columns:
            df_mostrar['fecha_creacion'] = df_mostrar['fecha_creacion'].astype(str)
        if 'fecha_actualizacion' in df_mostrar.columns:
            df_mostrar['fecha_actualizacion'] = df_mostrar['fecha_actualizacion'].astype(str)
            
        gb = GridOptionsBuilder.from_dataframe(df_mostrar)
        gb.configure_pagination(paginationAutoPageSize=False, paginationPageSize=15)
        gb.configure_side_bar()
        gb.configure_selection('single', use_checkbox=True)
        
        AgGrid(
            df_mostrar,
            gridOptions=gb.build(),
            enable_enterprise_modules=False,
            columns_auto_size_mode=ColumnsAutoSizeMode.FIT_CONTENTS,
            theme='balham',
            height=500
        )