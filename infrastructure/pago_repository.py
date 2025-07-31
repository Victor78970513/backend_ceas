from domain.pago import Pago
from sqlalchemy.orm import Session
from sqlalchemy import text
from config import SessionLocal
from typing import Optional

class PagoRepository:
    def list_pagos(self):
        db: Session = SessionLocal()
        try:
            result = db.execute(text("SELECT id_pago, id_accion, fecha_de_pago, monto, tipo_pago, estado_pago, observaciones FROM pago_accion")).fetchall()
            return [Pago(*row) for row in result]
        finally:
            db.close()

    def get_pago(self, pago_id: int) -> Optional[Pago]:
        db: Session = SessionLocal()
        try:
            result = db.execute(text("SELECT id_pago, id_accion, fecha_de_pago, monto, tipo_pago, estado_pago, observaciones FROM pago_accion WHERE id_pago = :id_pago"), {"id_pago": pago_id}).fetchone()
            if result:
                return Pago(*result)
            return None
        finally:
            db.close()

    def create_pago(self, data):
        db: Session = SessionLocal()
        try:
            result = db.execute(text('''
                INSERT INTO pago_accion (id_accion, monto, tipo_pago, estado_pago, observaciones)
                VALUES (:id_accion, :monto, :tipo_pago, :estado_pago, :observaciones)
                RETURNING id_pago, id_accion, fecha_de_pago, monto, tipo_pago, estado_pago, observaciones
            '''), data.dict())
            db.commit()
            row = result.fetchone()
            return Pago(*row)
        finally:
            db.close()

    def update_pago(self, pago_id: int, data):
        db: Session = SessionLocal()
        try:
            fields = []
            params = {"id_pago": pago_id}
            for field, value in data.dict(exclude_unset=True).items():
                fields.append(f"{field} = :{field}")
                params[field] = value
            if not fields:
                return self.get_pago(pago_id)
            db.execute(text(f"UPDATE pago_accion SET {', '.join(fields)} WHERE id_pago = :id_pago"), params)
            db.commit()
            return self.get_pago(pago_id)
        finally:
            db.close()

    def cambiar_estado(self, pago_id: int, data):
        db: Session = SessionLocal()
        try:
            db.execute(text("UPDATE pago_accion SET estado_pago = :estado_pago WHERE id_pago = :id_pago"), {"estado_pago": data.estado_pago, "id_pago": pago_id})
            db.commit()
            return self.get_pago(pago_id)
        finally:
            db.close()

    def delete_pago(self, pago_id: int):
        db: Session = SessionLocal()
        try:
            result = db.execute(text("DELETE FROM pago_accion WHERE id_pago = :id_pago RETURNING id_pago"), {"id_pago": pago_id})
            db.commit()
            return result.rowcount > 0
        finally:
            db.close() 