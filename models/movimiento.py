from sqlalchemy import Column, Integer, String, Float, DateTime, Text, Date
from datetime import datetime, timezone
from models.base import Base

class Movimiento(Base):
    __tablename__ = 'movimientos'

    # Campos principales
    id = Column(Integer, primary_key=True, autoincrement=True)
    fecha = Column(Date, nullable=False, index=True)
    tipo = Column(String(50), nullable=False) # 'Ingreso' o 'Egreso'
    proyecto = Column(String(100), nullable=False, index=True)
    categoria = Column(String(100), nullable=False)
    concepto = Column(String(255), nullable=False)
    importe = Column(Float, nullable=False)
    
    # Estados de flujo: Pendiente, Pagado, Cobrado, Cancelado
    estado = Column(String(50), nullable=False, default="Pendiente") 
    
    # Auditoría
    fecha_creacion = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    fecha_actualizacion = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    usuario = Column(String(100), nullable=False, default="Admin")
    observaciones = Column(Text, nullable=True)

    def __repr__(self):
        return f"<Movimiento(id={self.id}, tipo='{self.tipo}', importe={self.importe}, estado='{self.estado}')>"