from domain.evento import Evento
from sqlalchemy.orm import Session
from sqlalchemy import text
from config import SessionLocal
from typing import Optional

class EventoRepository:
    def list_eventos(self):
        db: Session = SessionLocal()
        try:
            result = db.execute(text("SELECT id_evento, nombre_evento, descripcion, fecha, hora, id_club, estado FROM eventos")).fetchall()
            return [Evento(*row) for row in result]
        finally:
            db.close()

    def get_evento(self, evento_id: int) -> Optional[Evento]:
        db: Session = SessionLocal()
        try:
            result = db.execute(text("SELECT id_evento, nombre_evento, descripcion, fecha, hora, id_club, estado FROM eventos WHERE id_evento = :id_evento"), {"id_evento": evento_id}).fetchone()
            if result:
                return Evento(*result)
            return None
        finally:
            db.close()

    def create_evento(self, data):
        db: Session = SessionLocal()
        try:
            result = db.execute(text('''
                INSERT INTO eventos (nombre_evento, descripcion, fecha, hora, id_club, estado)
                VALUES (:nombre_evento, :descripcion, :fecha, :hora, :id_club, :estado)
                RETURNING id_evento, nombre_evento, descripcion, fecha, hora, id_club, estado
            '''), data.dict())
            db.commit()
            row = result.fetchone()
            return Evento(*row)
        finally:
            db.close()

    def update_evento(self, evento_id: int, data):
        db: Session = SessionLocal()
        try:
            fields = []
            params = {"id_evento": evento_id}
            for field, value in data.dict(exclude_unset=True).items():
                fields.append(f"{field} = :{field}")
                params[field] = value
            if not fields:
                return self.get_evento(evento_id)
            db.execute(text(f"UPDATE eventos SET {', '.join(fields)} WHERE id_evento = :id_evento"), params)
            db.commit()
            return self.get_evento(evento_id)
        finally:
            db.close()

    def delete_evento(self, evento_id: int):
        db: Session = SessionLocal()
        try:
            result = db.execute(text("DELETE FROM eventos WHERE id_evento = :id_evento RETURNING id_evento"), {"id_evento": evento_id})
            db.commit()
            return result.rowcount > 0
        finally:
            db.close() 