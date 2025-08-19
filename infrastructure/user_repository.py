from domain.user import User
from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy import text
from config import SessionLocal

class UserRepository:
    def get_by_username(self, nombre_usuario: str) -> Optional[User]:
        db: Session = SessionLocal()
        try:
            result = db.execute(
                text("""
                    SELECT id_usuario, nombre_usuario, contrasena_hash, rol, estado, id_club, correo_electronico, ultimo_acceso
                    FROM usuario
                    WHERE nombre_usuario = :nombre_usuario
                """),
                {"nombre_usuario": nombre_usuario}
            ).fetchone()
            if result:
                return User(
                    id_usuario=result[0],
                    nombre_usuario=result[1],
                    contrasena_hash=result[2],
                    rol=result[3],
                    estado=result[4],
                    id_club=result[5],
                    correo_electronico=result[6],
                    ultimo_acceso=str(result[7]) if result[7] else None
                )
            return None
        finally:
            db.close()

    def get_by_email(self, correo_electronico: str) -> Optional[User]:
        db: Session = SessionLocal()
        try:
            result = db.execute(
                text("""
                    SELECT id_usuario, nombre_usuario, contrasena_hash, rol, estado, id_club, correo_electronico, ultimo_acceso
                    FROM usuario
                    WHERE correo_electronico = :correo_electronico
                """),
                {"correo_electronico": correo_electronico}
            ).fetchone()
            if result:
                return User(
                    id_usuario=result[0],
                    nombre_usuario=result[1],
                    contrasena_hash=result[2],
                    rol=result[3],
                    estado=result[4],
                    id_club=result[5],
                    correo_electronico=result[6],
                    ultimo_acceso=str(result[7]) if result[7] else None
                )
            return None
        finally:
            db.close()

    def list_users(self):
        db: Session = SessionLocal()
        try:
            result = db.execute(text("SELECT id_usuario, nombre_usuario, contrasena_hash, rol, estado, id_club, correo_electronico, ultimo_acceso FROM usuario")).fetchall()
            from domain.user import User
            return [User(*row) for row in result]
        finally:
            db.close()

    def get_user(self, user_id: int) -> Optional[User]:
        db: Session = SessionLocal()
        try:
            result = db.execute(text("SELECT id_usuario, nombre_usuario, contrasena_hash, rol, estado, id_club, correo_electronico, ultimo_acceso FROM usuario WHERE id_usuario = :id_usuario"), {"id_usuario": user_id}).fetchone()
            if result:
                from domain.user import User
                return User(*result)
            return None
        finally:
            db.close()

    def create_user(self, nombre_usuario: str, contrasena_hash: str, rol: int, estado: str, id_club: int, correo_electronico: str) -> User:
        db: Session = SessionLocal()
        try:
            result = db.execute(
                text('''
                    INSERT INTO usuario (nombre_usuario, contrasena_hash, rol, estado, id_club, correo_electronico)
                    VALUES (:nombre_usuario, :contrasena_hash, :rol, :estado, :id_club, :correo_electronico)
                    RETURNING id_usuario, nombre_usuario, contrasena_hash, rol, estado, id_club, correo_electronico, ultimo_acceso
                '''),
                {
                    "nombre_usuario": nombre_usuario,
                    "contrasena_hash": contrasena_hash,
                    "rol": rol,
                    "estado": estado,
                    "id_club": id_club,
                    "correo_electronico": correo_electronico
                }
            )
            db.commit()
            user_row = result.fetchone()
            return User(
                id_usuario=user_row[0],
                nombre_usuario=user_row[1],
                contrasena_hash=user_row[2],
                rol=user_row[3],
                estado=user_row[4],
                id_club=user_row[5],
                correo_electronico=user_row[6],
                ultimo_acceso=str(user_row[7]) if user_row[7] else None
            )
        finally:
            db.close()

    def update_user(self, user_id: int, data):
        db: Session = SessionLocal()
        try:
            fields = []
            params = {"id_usuario": user_id}
            for field, value in data.dict(exclude_unset=True).items():
                if field == "contrasena":
                    from infrastructure.security import hash_password
                    fields.append("contrasena_hash = :contrasena_hash")
                    params["contrasena_hash"] = hash_password(value)
                else:
                    fields.append(f"{field} = :{field}")
                    params[field] = value
            if not fields:
                return self.get_user(user_id)
            db.execute(text(f"UPDATE usuario SET {', '.join(fields)} WHERE id_usuario = :id_usuario"), params)
            db.commit()
            return self.get_user(user_id)
        finally:
            db.close()

    def delete_user(self, user_id: int):
        db: Session = SessionLocal()
        try:
            result = db.execute(text("DELETE FROM usuario WHERE id_usuario = :id_usuario RETURNING id_usuario"), {"id_usuario": user_id})
            db.commit()
            return result.rowcount > 0
        finally:
            db.close() 