from domain.factura import Factura
from sqlalchemy.orm import Session
from sqlalchemy import text
from config import SessionLocal
from typing import Optional

class FacturaRepository:
    def list_facturas(self):
        db: Session = SessionLocal()
        try:
            result = db.execute(text("SELECT id_factura, id_socio, fecha_de_emision, monto_total, estado FROM facturacion")).fetchall()
            return [Factura(*row) for row in result]
        finally:
            db.close()

    def get_factura(self, factura_id: int) -> Optional[Factura]:
        db: Session = SessionLocal()
        try:
            result = db.execute(text("SELECT id_factura, id_socio, fecha_de_emision, monto_total, estado FROM facturacion WHERE id_factura = :id_factura"), {"id_factura": factura_id}).fetchone()
            if result:
                return Factura(*result)
            return None
        finally:
            db.close()

    def create_factura(self, data):
        db: Session = SessionLocal()
        try:
            result = db.execute(text('''
                INSERT INTO facturacion (id_socio, monto_total, estado)
                VALUES (:id_socio, :monto_total, :estado)
                RETURNING id_factura, id_socio, fecha_de_emision, monto_total, estado
            '''), data.dict())
            db.commit()
            row = result.fetchone()
            return Factura(*row)
        finally:
            db.close()

    def update_factura(self, factura_id: int, data):
        db: Session = SessionLocal()
        try:
            fields = []
            params = {"id_factura": factura_id}
            for field, value in data.dict(exclude_unset=True).items():
                fields.append(f"{field} = :{field}")
                params[field] = value
            if not fields:
                return self.get_factura(factura_id)
            db.execute(text(f"UPDATE facturacion SET {', '.join(fields)} WHERE id_factura = :id_factura"), params)
            db.commit()
            return self.get_factura(factura_id)
        finally:
            db.close()

    def delete_factura(self, factura_id: int):
        db: Session = SessionLocal()
        try:
            result = db.execute(text("DELETE FROM facturacion WHERE id_factura = :id_factura RETURNING id_factura"), {"id_factura": factura_id})
            db.commit()
            return result.rowcount > 0
        finally:
            db.close() 