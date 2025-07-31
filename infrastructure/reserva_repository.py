from domain.reserva import Reserva
from sqlalchemy.orm import Session
from sqlalchemy import text
from config import SessionLocal
from typing import Optional, List

class ReservaRepository:
    def list_reservas(self, id_evento: Optional[int] = None, id_socio: Optional[int] = None) -> List[Reserva]:
        db: Session = SessionLocal()
        try:
            query = "SELECT id_reserva, id_socio, id_evento, fecha_de_reserva, estado FROM reservas"
            filters = []
            params = {}
            if id_evento is not None:
                filters.append("id_evento = :id_evento")
                params["id_evento"] = id_evento
            if id_socio is not None:
                filters.append("id_socio = :id_socio")
                params["id_socio"] = id_socio
            if filters:
                query += " WHERE " + " AND ".join(filters)
            result = db.execute(text(query), params).fetchall()
            return [Reserva(*row) for row in result]
        finally:
            db.close()

    def get_reserva(self, reserva_id: int) -> Optional[Reserva]:
        db: Session = SessionLocal()
        try:
            result = db.execute(text("SELECT id_reserva, id_socio, id_evento, fecha_de_reserva, estado FROM reservas WHERE id_reserva = :id_reserva"), {"id_reserva": reserva_id}).fetchone()
            if result:
                return Reserva(*result)
            return None
        finally:
            db.close()

    def create_reserva(self, data):
        db: Session = SessionLocal()
        try:
            result = db.execute(text('''
                INSERT INTO reservas (id_socio, id_evento, estado)
                VALUES (:id_socio, :id_evento, :estado)
                RETURNING id_reserva, id_socio, id_evento, fecha_de_reserva, estado
            '''), data.dict())
            db.commit()
            row = result.fetchone()
            return Reserva(*row)
        finally:
            db.close()

    def update_reserva(self, reserva_id: int, data):
        db: Session = SessionLocal()
        try:
            fields = []
            params = {"id_reserva": reserva_id}
            for field, value in data.dict(exclude_unset=True).items():
                fields.append(f"{field} = :{field}")
                params[field] = value
            if not fields:
                return self.get_reserva(reserva_id)
            db.execute(text(f"UPDATE reservas SET {', '.join(fields)} WHERE id_reserva = :id_reserva"), params)
            db.commit()
            return self.get_reserva(reserva_id)
        finally:
            db.close()

    def delete_reserva(self, reserva_id: int):
        db: Session = SessionLocal()
        try:
            result = db.execute(text("DELETE FROM reservas WHERE id_reserva = :id_reserva RETURNING id_reserva"), {"id_reserva": reserva_id})
            db.commit()
            return result.rowcount > 0
        finally:
            db.close() 