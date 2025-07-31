from domain.asistencia import Asistencia
from sqlalchemy.orm import Session
from sqlalchemy import text
from config import SessionLocal
from typing import Optional

class AsistenciaRepository:
    def list_asistencias(self):
        db: Session = SessionLocal()
        try:
            result = db.execute(text("SELECT id_asistencia, id_personal, fecha, hora_ingreso, hora_salida, observaciones FROM asistencia")).fetchall()
            return [Asistencia(*row) for row in result]
        finally:
            db.close()

    def get_asistencia_personal(self, id_personal: int):
        db: Session = SessionLocal()
        try:
            result = db.execute(text("SELECT id_asistencia, id_personal, fecha, hora_ingreso, hora_salida, observaciones FROM asistencia WHERE id_personal = :id_personal"), {"id_personal": id_personal}).fetchall()
            return [Asistencia(*row) for row in result]
        finally:
            db.close()

    def create_asistencia(self, data):
        db: Session = SessionLocal()
        try:
            result = db.execute(text('''
                INSERT INTO asistencia (id_personal, fecha, hora_ingreso, hora_salida, observaciones)
                VALUES (:id_personal, :fecha, :hora_ingreso, :hora_salida, :observaciones)
                RETURNING id_asistencia, id_personal, fecha, hora_ingreso, hora_salida, observaciones
            '''), data.dict())
            db.commit()
            row = result.fetchone()
            return Asistencia(*row)
        finally:
            db.close()

    def update_asistencia(self, asistencia_id: int, data):
        db: Session = SessionLocal()
        try:
            fields = []
            params = {"id_asistencia": asistencia_id}
            for field, value in data.dict(exclude_unset=True).items():
                fields.append(f"{field} = :{field}")
                params[field] = value
            if not fields:
                return None
            db.execute(text(f"UPDATE asistencia SET {', '.join(fields)} WHERE id_asistencia = :id_asistencia"), params)
            db.commit()
            result = db.execute(text("SELECT id_asistencia, id_personal, fecha, hora_ingreso, hora_salida, observaciones FROM asistencia WHERE id_asistencia = :id_asistencia"), {"id_asistencia": asistencia_id}).fetchone()
            if result:
                return Asistencia(*result)
            return None
        finally:
            db.close() 