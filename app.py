import streamlit as st
from streamlit_option_menu import option_menu
from database.db_session import init_db
from config.settings import APP_NAME
from config.i18n import get_text
from services.auth_service import AuthService
from services.backup_service import BackupService
from database.db_session import init_db, SessionLocal
from models.user import User

# 1. Configuración global (Única declaración)
st.set_page_config(
    page_title=APP_NAME,
    page_icon=":material/finance:",
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.markdown(
    """
    <style>
    [data-testid="stSidebarNav"] {
        display: none;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# 2. Inicializar BD
init_db()

def asegurar_usuarios_por_defecto():
    db = SessionLocal()
    try:
        # Verificar si la tabla de usuarios está vacía
        if db.query(User).count() == 0:
            auth_service = AuthService(db)
            # Crear Administrador por defecto
            auth_service.create_user(username="admin", password="admin123", role="Administrador")
            # Crear Operador por defecto
            auth_service.create_user(username="operador", password="op123", role="Operador")
    except Exception as e:
        print(f"Error al crear usuarios por defecto: {e}")
    finally:
        db.close()

# Ejecutar la creación automática
asegurar_usuarios_por_defecto()


# Extraemos el idioma configurado (por defecto 'es')
idioma = st.session_state.get('idioma', 'es')

# 3. Control de Sesión / Autenticación
if 'authenticated' not in st.session_state:
    st.session_state['authenticated'] = False
    st.session_state['user_data'] = None

# Si el usuario NO está autenticado, mostramos la pantalla de Login
if not st.session_state['authenticated']:
    st.markdown("<br><br>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 1.5, 1])
    
    with col2:
        st.subheader(f":material/passkey: Acceso a {APP_NAME}")
        st.markdown("Introduce tus credenciales para continuar.")
        
        # with st.form("login_form"):
        #     username = st.text_input("Usuario", placeholder="admin u operador")
        #     password = st.text_input("Contraseña", type="password", placeholder="admin123 u op123")
        #     submit = st.form_submit_button("Iniciar Sesión", width='stretch')
            
        #     if submit:
        #         user = AuthService.authenticate(username, password)
        #         if user:
        #             st.session_state['authenticated'] = True
        #             st.session_state['user_data'] = user
        #             st.success(f"¡Bienvenido, {user['name']}!")
        #             st.rerun()
        with st.form("login_form"):
            username = st.text_input("Usuario", placeholder="admin u operador")
            password = st.text_input("Contraseña", type="password", placeholder="admin123 u op123")
            submit = st.form_submit_button("Iniciar Sesión", width='stretch')
            
            if submit:
                # --- AQUÍ SE INTEGRA EL SERVICIO CONECTADO A LA BD ---
                db = SessionLocal()
                auth_service = AuthService(db)
                user_obj = auth_service.authenticate(username, password)
                db.close()

                if user_obj:
                    st.session_state['authenticated'] = True
                    # Guardamos un diccionario con los datos del modelo User de tu base de datos
                    st.session_state['user_data'] = {
                        'username': user_obj.username,
                        'role': user_obj.role,
                        'name': user_obj.username  # O el campo de nombre si lo agregas luego
                    }
                    st.success(f"¡Bienvenido, {user_obj.username}!")
                    st.rerun()
                else:
                    st.error(":material/error: Usuario o contraseña incorrectos.")
                    
        with st.expander(":material/id_card: Credenciales de prueba"):
            st.markdown("""
            - **Administrador:** `admin` / `admin123`
            - **Operador:** `operador` / `op123`
            """)
            
    st.stop() # Detiene la ejecución de la app hasta que el usuario inicie sesión

# 4. Recuperar datos del usuario logueado
user_data = st.session_state['user_data']

# 5. Diseño del Sidebar (Una vez autenticado)
with st.sidebar:
    st.markdown(f"### :material/account_balance: {get_text(idioma, 'app_title')}")
    st.markdown("---")
    
    selected_page = option_menu(
        menu_title="Menú Principal",
        options=["Dashboard", "Movimientos", "Inteligencia", "Simulador", "ImportarDatos/Reportes", "Configuración"],
        icons=["bar-chart-fill", "wallet2", "cpu", "sliders", "file-earmark-pdf", "gear"],
        menu_icon="cast",
        default_index=0,
        key="menu_principal",
        styles={
            "container": {"padding": "0!important", "background-color": "transparent"},
            "icon": {"color": "orange", "font-size": "18px"}, 
            "nav-link": {"font-size": "15px", "text-align": "left", "margin":"0px", "--hover-color": "#eee"},
            "nav-link-selected": {"background-color": "#02ab21"},
        }
    )
    
    st.markdown("---")
    st.info(f":material/account_box: {user_data['name']}\n\n Rol: {user_data['role']}")
    
    if st.button(":material/logout: Cerrar Sesión", width='stretch'):
        st.session_state['authenticated'] = False
        st.session_state['user_data'] = None
        st.rerun()
# Generar un backup automático una sola vez por sesión
if "backup_realizado" not in st.session_state:
    backup_service = BackupService()
    backup_service.create_backup()
    st.session_state["backup_realizado"] = True


# 6. Ruteador completo de páginas
if selected_page == "Dashboard":
    from pages import page_dashboard
    page_dashboard.render_page()
elif selected_page == "Movimientos":
    from pages import page_movimientos
    page_movimientos.render_page()
elif selected_page == "Inteligencia":
    from pages import page_inteligencia
    page_inteligencia.render_page()
elif selected_page == "Simulador":
    from pages import page_simulador
    page_simulador.render_page()
elif selected_page == "ImportarDatos/Reportes":
    from pages import page_reportes
    page_reportes.render_page()
elif selected_page == "Configuración":
    from pages import page_configuracion
    page_configuracion.render_page()
else:
    st.title(f"Módulo: {selected_page}")
    st.warning(get_text(idioma, 'in_construction'))