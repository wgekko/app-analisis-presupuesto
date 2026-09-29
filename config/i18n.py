# Diccionario maestro de traducciones
TRANSLATIONS = {
    "es": {
        # Menú
        "menu_dashboard": "Dashboard",
        "menu_movimientos": "Movimientos",
        "menu_inteligencia": "Inteligencia",
        "menu_simulador": "Simulador",
        "menu_reportes": "ImportarDatos/Reportes",
        "menu_configuracion": "Configuración",
        
        # Generales
        "app_title": "Presupuesto",
        "welcome": "Bienvenido",
        "role_admin": "Administrador",
        "in_construction": "Este módulo está en construcción.",
        
        # Botones y Acciones
        "btn_save": "Guardar",
        "btn_cancel": "Cancelar",
        "btn_export": "Exportar Datos",
        "btn_import": "Importar Masivamente"
    },
    "en": {
        # Menu
        "menu_dashboard": "Dashboard",
        "menu_movimientos": "Transactions",
        "menu_inteligencia": "AI Analytics",
        "menu_simulador": "Simulator",
        "menu_reportes": "Reports",
        "menu_configuracion": "Settings",
        
        # General
        "app_title": "Presupuesto",
        "welcome": "Welcome",
        "role_admin": "Administrator",
        "in_construction": "This module is under construction.",
        
        # Buttons and Actions
        "btn_save": "Save",
        "btn_cancel": "Cancel",
        "btn_export": "Export Data",
        "btn_import": "Mass Import"
    }
}

def get_text(lang: str, key: str) -> str:
    """
    Busca el texto según el idioma. 
    Si la clave no existe en el idioma solicitado, intenta en español.
    Si tampoco existe, devuelve la clave original como medida de seguridad.
    """
    return TRANSLATIONS.get(lang, TRANSLATIONS["es"]).get(key, key)