from sqlalchemy.orm import declarative_base

# Clase base para todos los modelos ORM
# Permite a SQLAlchemy mapear las clases de Python a tablas de SQLite
Base = declarative_base()