from sqlalchemy import Column, Integer, String, Boolean, DateTime
from datetime import datetime, timezone
from models.base import Base

class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    
    # Roles: Administrador, Operador, Solo lectura
    role = Column(String(50), nullable=False, default="Operador") 
    is_active = Column(Boolean, default=True)
    fecha_creacion = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    def __repr__(self):
        return f"<User(username='{self.username}', role='{self.role}')>"