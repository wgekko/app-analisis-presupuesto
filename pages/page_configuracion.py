import streamlit as st
import pandas as pd
from config.settings import DEFAULT_CURRENCY, DEFAULT_LANGUAGE
from config.i18n import get_text
from services.backup_service import BackupService

def render_page():
    st.subheader(":material/settings: Configuración del Sistema")
    st.markdown("Administra las preferencias globales, categorías y proyectos.")

    # Inicialización de variables en memoria (Session State)
    # En la Fase 2 del ERP, esto se conectaría directamente a las tablas de SQLite.
    if 'categorias' not in st.session_state:
        st.session_state['categorias'] = ["Ventas", "Servicios", "Viáticos", "Insumos", "Otros"]
    if 'proyectos' not in st.session_state:
        st.session_state['proyectos'] = ["General", "Las Verbenas", "Lindos Pagos"]
    if 'moneda' not in st.session_state:
        st.session_state['moneda'] = DEFAULT_CURRENCY
    if 'idioma' not in st.session_state:
        st.session_state['idioma'] = DEFAULT_LANGUAGE

    tab1, tab2, tab3, tab4 = st.tabs(["Preferencias Generales", "Gestión de Categorías", "Gestión de Proyectos", "Gestión de Backup"])

    # --- TAB 1: PREFERENCIAS GLOBALES ---
    with tab1:
        st.subheader("Ajustes Regionales")
        col1, col2 = st.columns(2)
        with col1:
            nuevo_idioma = st.selectbox(
                "Idioma de la Interfaz", 
                ["es", "en"], 
                index=0 if st.session_state['idioma'] == "es" else 1
            )
        with col2:
            opciones_moneda = ["$", "€", "USD", "S/.", "COP"]
            idx_moneda = opciones_moneda.index(st.session_state['moneda']) if st.session_state['moneda'] in opciones_moneda else 0
            nueva_moneda = st.selectbox("Moneda Principal", opciones_moneda, index=idx_moneda)
        
        if st.button("Guardar Preferencias", type="primary"):
            st.session_state['idioma'] = nuevo_idioma
            st.session_state['moneda'] = nueva_moneda
            st.success(":material/check_box: Preferencias actualizadas. Los cambios se aplicarán en los módulos.")

    # --- TAB 2: CATEGORÍAS FINANCIERAS ---
    with tab2:
        st.subheader("Categorías de Movimientos")
        col_cat1, col_cat2 = st.columns([3, 1])
        with col_cat1:
            nueva_cat = st.text_input("Nueva Categoría", placeholder="Ej: Publicidad", key="input_cat")
        with col_cat2:
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("Agregar Categoría", width='stretch'):
                if nueva_cat and nueva_cat not in st.session_state['categorias']:
                    st.session_state['categorias'].append(nueva_cat)
                    st.success(f"Categoría '{nueva_cat}' agregada.")
                    st.rerun()
                elif nueva_cat in st.session_state['categorias']:
                    st.warning("La categoría ya existe.")
        
        st.markdown("**Categorías Actuales:**")
        for cat in st.session_state['categorias']:
            c1, c2 = st.columns([4, 1])
            c1.markdown(f"- {cat}")
            if c2.button("Eliminar", key=f"del_cat_{cat}"):
                st.session_state['categorias'].remove(cat)
                st.rerun()

    # --- TAB 3: PROYECTOS ---
    with tab3:
        st.subheader("Proyectos Activos")
        col_proy1, col_proy2 = st.columns([3, 1])
        with col_proy1:
            nuevo_proy = st.text_input("Nuevo Proyecto", placeholder="Ej: Campaña Invierno", key="input_proy")
        with col_proy2:
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("Agregar Proyecto", width='stretch'):
                if nuevo_proy and nuevo_proy not in st.session_state['proyectos']:
                    st.session_state['proyectos'].append(nuevo_proy)
                    st.success(f"Proyecto '{nuevo_proy}' agregado.")
                    st.rerun()
                elif nuevo_proy in st.session_state['proyectos']:
                    st.warning("El proyecto ya existe.")
        
        st.markdown("**Proyectos Actuales:**")
        for proy in st.session_state['proyectos']:
            p1, p2 = st.columns([4, 1])
            p1.markdown(f"- {proy}")
            if p2.button("Eliminar", key=f"del_proy_{proy}"):
                st.session_state['proyectos'].remove(proy)
                st.rerun()

     # --- TAB 4: BACKUP ---

    with tab4:            
        st.subheader(":material/settings: Configuración y Copias de Seguridad")
        st.markdown("Administra la integridad de tus datos mediante respaldos locales.")

        backup_service = BackupService()

        # --- SECCIÓN: CREAR BACKUP MANUAL ---
        st.markdown(":material/save: ### Copia de Seguridad Manual")
        col_info, col_btn = st.columns([2, 1])

        with col_info:
            st.write("Genera una copia instantánea del archivo de base de datos SQLite en la carpeta `backups/`.")

        with col_btn:
            if st.button("Crear Backup Ahora", width='stretch', type="primary"):
                exito, mensaje = backup_service.create_backup()
                if exito:
                    st.success(f"¡Backup creado con éxito! (`{mensaje}`)")
                    st.rerun()
                else:
                    st.error(f"Error al crear backup: {mensaje}")

        st.markdown("---")

        # --- SECCIÓN: HISTORIAL DE BACKUPS ---
        st.markdown("### 📋 Historial de Resguardos Disponibles")
        backups = backup_service.get_all_backups()

        if not backups:
            st.info("Aún no se han generado copias de seguridad.")
        else:
            df_backups = pd.DataFrame(backups)
            
            # Formatear la vista
            df_display = df_backups[['nombre', 'fecha', 'tamano_kb']].copy()
            df_display.columns = ['Nombre de Archivo', 'Fecha de Creación', 'Tamaño (KB)']
            
            st.dataframe(df_display, width='stretch', hide_index=True)

            # Permitir la descarga directa de la última copia de seguridad
            ultimo_backup = backups[0]
            with open(ultimo_backup['ruta'], "rb") as file:
                st.download_button(
                    label=f"📥 Descargar última copia ({ultimo_backup['nombre']})",
                    data=file,
                    file_name=ultimo_backup['nombre'],
                    mime="application/x-sqlite3"
                )