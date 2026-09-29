# import hashlib

# class AuthService:
#     """
#     Servicio encargado de la autenticación de usuarios, 
#     verificación de credenciales y gestión de roles.
#     """
    
#     # Base de datos simulada de usuarios (En un ERP avanzado, esto se mapea con una tabla 'users' en SQLite)
#     _USERS_DB = {
#         "admin": {
#             "password_hash": hashlib.sha256("admin123".encode()).hexdigest(),
#             "role": "Administrador",
#             "name": "Administrador General"
#         },
#         "operador": {
#             "password_hash": hashlib.sha256("op123".encode()).hexdigest(),
#             "role": "Operador Financiero",
#             "name": "Juan Pérez"
#         }
#     }

#     @classmethod
#     def authenticate(cls, username: str, password: str) -> dict | None:
#         """
#         Verifica si el usuario existe y si la contraseña coincide.
#         Devuelve un diccionario con los datos del usuario o None si falla.
#         """
#         username = username.strip().lower()
#         if username not in cls._USERS_DB:
#             return None
            
#         user_info = cls._USERS_DB[username]
#         input_hash = hashlib.sha256(password.encode()).hexdigest()
        
#         if user_info["password_hash"] == input_hash:
#             return {
#                 "username": username,
#                 "role": user_info["role"],
#                 "name": user_info["name"]
#             }
#         return None

#     @staticmethod
#     def verify_permission(user_role: str, required_role: str) -> bool:
#         """
#         Verifica si un rol tiene permisos para acceder a ciertas acciones.
#         """
#         hierarchy = {"Operador Financiero": 1, "Administrador": 2}
#         return hierarchy.get(user_role, 0) >= hierarchy.get(required_role, 1)

import bcrypt
from sqlalchemy.orm import Session
from models.user import User  # Importamos tu modelo User exacto

class AuthService:
    """Servicio para la gestión de usuarios, hashing de contraseñas y autenticación."""

    def __init__(self, db: Session):
        self.db = db

    def hash_password(self, password: str) -> str:
        """Genera un hash seguro utilizando bcrypt."""
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
        return hashed.decode('utf-8')

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verifica si una contraseña en texto plano coincide con su hash."""
        return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))

    def authenticate(self, username: str, password: str):
        """Valida las credenciales de un usuario y comprueba si su cuenta está activa."""
        user = self.db.query(User).filter(User.username == username).first()
        
        # Validar si el usuario existe y si está activo según tu modelo[cite: 9]
        if not user or not user.is_active:
            return None
            
        if self.verify_password(password, user.password_hash):
            return user
        return None

    def create_user(self, username: str, password: str, role: str = "Operador") -> tuple[bool, str]:
        """Registra un nuevo usuario en la base de datos con contraseña cifrada y rol asignado."""
        existing_user = self.db.query(User).filter(User.username == username).first()
        if existing_user:
            return False, "El nombre de usuario ya se encuentra registrado."
        
        try:
            pwd_hash = self.hash_password(password)
            new_user = User(
                username=username, 
                password_hash=pwd_hash, 
                role=role,
                is_active=True
            )
            self.db.add(new_user)
            self.db.commit()
            self.db.refresh(new_user)
            return True, "Usuario creado exitosamente."
        except Exception as e:
            self.db.rollback()
            return False, str(e)