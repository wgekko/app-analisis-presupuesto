import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models.base import Base
from config.settings import DATABASE_URL

# Importamos los modelos explícitamente para que Base.metadata los registre
from models.movimiento import Movimiento
from models.user import User

# Archivo SQLite en la raíz del proyecto
#DB_URL = "sqlite:///prompt_maestro.db"
SQLALCHEMY_DATABASE_URL = DATABASE_URL

# Engine de conexión
engine = create_engine(
    #DB_URL,
    SQLALCHEMY_DATABASE_URL, 
    connect_args={"check_same_thread": False},
    echo=False # Cambiar a True si se desea auditar las queries SQL en la consola
)

# Generador de sesiones
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db():
    """
    Crea todas las tablas en la base de datos si no existen.
    Esta función se llamará al arrancar la aplicación.
    """
    Base.metadata.create_all(bind=engine)
    
def get_db():
    """
    Función utilitaria para manejar la sesión de base de datos
    de forma segura y garantizar su cierre.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()