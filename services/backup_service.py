import os
import shutil
from datetime import datetime
from pathlib import Path

class BackupService:
    """Servicio para la gestión y creación de copias de seguridad de la base de datos SQLite."""

    def __init__(self, db_path: str = "database/presupuesto.db", backup_dir: str = "backups"):
        self.db_path = Path(db_path)
        self.backup_dir = Path(backup_dir)
        # Asegurar que la carpeta backups exista
        self.backup_dir.mkdir(parents=True, exist_ok=True)

    def create_backup(self) -> tuple[bool, str]:
        """Crea una copia de seguridad con marca de tiempo del archivo de base de datos."""
        if not self.db_path.exists():
            return False, f"No se encontró el archivo de base de datos en: {self.db_path}"

        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_filename = f"backup_presupuesto_{timestamp}.db"
            target_path = self.backup_dir / backup_filename

            # Realizar la copia manteniendo los metadatos del archivo original
            shutil.copy2(self.db_path, target_path)
            return True, backup_filename
        except Exception as e:
            return False, str(e)

    def get_all_backups(self) -> list[dict]:
        """Retorna una lista detallada de todas las copias de seguridad disponibles."""
        if not self.backup_dir.exists():
            return []

        backups = []
        for file in sorted(self.backup_dir.glob("*.db"), reverse=True):
            stat = file.stat()
            backups.append({
                "nombre": file.name,
                "ruta": str(file),
                "tamano_kb": round(stat.st_size / 1024, 2),
                "fecha": datetime.fromtimestamp(stat.st_mtime).strftime("%d/%m/%Y %H:%M:%S")
            })
        return backups