import streamlit as st
from utils.validators import validate_amount, validate_required_field

def render_movimiento_form():
    """Formulario reutilizable para registrar un movimiento."""
    with st.form("form_nuevo_movimiento", clear_on_submit=True):
        st.subheader("Registrar Nuevo Movimiento")
        
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
            
        submitted = st.form_submit_button("Guardar Movimiento", width='stretch')
        
        if submitted:
            # Validaciones usando nuestro módulo validators.py
            if not validate_required_field(concepto):
                st.error("El campo 'Concepto' es obligatorio.")
                return None
                
            is_valid_amt, importe_val = validate_amount(importe_input)
            if not is_valid_amt:
                st.error("El importe debe ser un número válido mayor a 0.")
                return None
                
            # Si pasa las validaciones, devolvemos el diccionario listo para el servicio
            return {
                "fecha": fecha,
                "tipo": tipo,
                "proyecto": proyecto,
                "categoria": categoria,
                "concepto": concepto.strip(),
                "importe": importe_val,
                "estado": estado,
                "observaciones": observaciones.strip()
            }
    return None