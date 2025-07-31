from domain.finanza import MovimientoFinanciero
from sqlalchemy.orm import Session
from sqlalchemy import text
from config import SessionLocal
from typing import Optional

class FinanzaRepository:
    def list_movimientos(self):
        db: Session = SessionLocal()
        try:
            result = db.execute(text("SELECT id_movimiento, id_club, tipo_movimiento, descripcion, monto, fecha, estado, referencia_relacionada, metodo_pago FROM movimiento_financiero")).fetchall()
            return [MovimientoFinanciero(*row) for row in result]
        finally:
            db.close()

    def get_movimiento(self, movimiento_id: int) -> Optional[MovimientoFinanciero]:
        db: Session = SessionLocal()
        try:
            result = db.execute(text("SELECT id_movimiento, id_club, tipo_movimiento, descripcion, monto, fecha, estado, referencia_relacionada, metodo_pago FROM movimiento_financiero WHERE id_movimiento = :id_movimiento"), {"id_movimiento": movimiento_id}).fetchone()
            if result:
                return MovimientoFinanciero(*result)
            return None
        finally:
            db.close()

    def create_movimiento(self, data):
        db: Session = SessionLocal()
        try:
            result = db.execute(text('''
                INSERT INTO movimiento_financiero (id_club, tipo_movimiento, descripcion, monto, estado, referencia_relacionada, metodo_pago)
                VALUES (:id_club, :tipo_movimiento, :descripcion, :monto, :estado, :referencia_relacionada, :metodo_pago)
                RETURNING id_movimiento, id_club, tipo_movimiento, descripcion, monto, fecha, estado, referencia_relacionada, metodo_pago
            '''), data.dict())
            db.commit()
            row = result.fetchone()
            return MovimientoFinanciero(*row)
        finally:
            db.close()

    def update_movimiento(self, movimiento_id: int, data):
        db: Session = SessionLocal()
        try:
            fields = []
            params = {"id_movimiento": movimiento_id}
            for field, value in data.dict(exclude_unset=True).items():
                fields.append(f"{field} = :{field}")
                params[field] = value
            if not fields:
                return self.get_movimiento(movimiento_id)
            db.execute(text(f"UPDATE movimiento_financiero SET {', '.join(fields)} WHERE id_movimiento = :id_movimiento"), params)
            db.commit()
            return self.get_movimiento(movimiento_id)
        finally:
            db.close()

    def delete_movimiento(self, movimiento_id: int):
        db: Session = SessionLocal()
        try:
            result = db.execute(text("DELETE FROM movimiento_financiero WHERE id_movimiento = :id_movimiento RETURNING id_movimiento"), {"id_movimiento": movimiento_id})
            db.commit()
            return result.rowcount > 0
        finally:
            db.close() 