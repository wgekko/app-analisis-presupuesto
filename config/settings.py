import os
from pathlib import Path

# --- RUTAS Y DIRECTORIOS ---
# Detecta automáticamente la ruta raíz del proyecto
BASE_DIR = Path(__file__).resolve().parent.parent
DB_NAME = "prompt_maestro.db"
DATABASE_URL = f"sqlite:///{os.path.join(BASE_DIR, DB_NAME)}"

# --- CONFIGURACIÓN GENERAL DE LA APP ---
APP_NAME = "Presupuesto"
APP_VERSION = "1.0.0"
DEFAULT_LANGUAGE = "es"
DEFAULT_CURRENCY = "$"
TIMEZONE = "America/Argentina/Mendoza"

# --- INTERFAZ DE USUARIO (UI) ---
THEME_MAIN_COLOR = "#02ab21"
ROWS_PER_PAGE = 15  # Límite de filas en las tablas de movimientos

# --- PARÁMETROS DE INTELIGENCIA ARTIFICIAL Y SIMULADOR ---
MIN_RECORDS_FOR_ML = 5       # Mínimo de registros para que la IA prediga
DEFAULT_PROJECTION_DAYS = 30 # Días por defecto en el slider del simulador
ANOMALY_CONTAMINATION = 0.05 # 5% de tolerancia para Isolation Forest