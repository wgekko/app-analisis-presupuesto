import pandas as pd
from sqlalchemy.orm import Session
from sqlalchemy import exc
from models.movimiento import Movimiento
from datetime import date, datetime, timezone

class MovimientoService:
    def __init__(self, db_session: Session):
        self.db = db_session

    def create(self, fecha: date, tipo: str, proyecto: str, 
               categoria: str, concepto: str, importe: float, 
               estado: str = "Pendiente", observaciones: str = "") -> bool:
        """Crea un nuevo registro financiero en la base de datos."""
        try:
            nuevo_mov = Movimiento(
                fecha=fecha,
                tipo=tipo,
                proyecto=proyecto,
                categoria=categoria,
                concepto=concepto,
                importe=importe,
                estado=estado,
                observaciones=observaciones
            )
            self.db.add(nuevo_mov)
            self.db.commit()
            return True
        except exc.SQLAlchemyError as e:
            self.db.rollback()
            print(f"Error al crear movimiento: {e}")
            return False

    def get_all_df(self) -> pd.DataFrame:
        """Obtiene todos los movimientos y los devuelve como un DataFrame de Pandas."""
        query = self.db.query(Movimiento)
        df = pd.read_sql(query.statement, self.db.bind)
        if not df.empty:
            # Aseguramos que la fecha sea datetime para Plotly/AgGrid
            df['fecha'] = pd.to_datetime(df['fecha']).dt.date
        return df

    def update(self, mov_id: int, **kwargs) -> bool:
        """Actualiza campos específicos de un movimiento."""
        try:
            mov = self.db.query(Movimiento).filter(Movimiento.id == mov_id).first()
            if not mov:
                return False
            
            for key, value in kwargs.items():
                if hasattr(mov, key):
                    setattr(mov, key, value)
            
            mov.fecha_actualizacion = datetime.now(timezone.utc)
            self.db.commit()
            return True
        except exc.SQLAlchemyError as e:
            self.db.rollback()
            print(f"Error al actualizar: {e}")
            return False

    def delete(self, mov_id: int) -> bool:
        """Elimina un movimiento por su ID."""
        try:
            mov = self.db.query(Movimiento).filter(Movimiento.id == mov_id).first()
            if mov:
                self.db.delete(mov)
                self.db.commit()
                return True
            return False
        except exc.SQLAlchemyError as e:
            self.db.rollback()
            print(f"Error al eliminar: {e}")
            return False

    def duplicate(self, mov_id: int) -> bool:
        """Duplica un registro existente basándose en su ID."""
        try:
            mov_original = self.db.query(Movimiento).filter(Movimiento.id == mov_id).first()
            if not mov_original:
                return False
            
            nuevo_mov = Movimiento(
                fecha=mov_original.fecha,
                tipo=mov_original.tipo,
                proyecto=mov_original.proyecto,
                categoria=mov_original.categoria,
                concepto=f"{mov_original.concepto} (Copia)",
                importe=mov_original.importe,
                estado=mov_original.estado,
                observaciones=mov_original.observaciones
            )
            self.db.add(nuevo_mov)
            self.db.commit()
            return True
        except exc.SQLAlchemyError as e:
            self.db.rollback()
            return False