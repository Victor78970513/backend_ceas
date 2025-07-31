from domain.compra import Compra
from sqlalchemy.orm import Session
from sqlalchemy import text
from config import SessionLocal
from typing import Optional

class CompraRepository:
    def list_compras(self):
        db: Session = SessionLocal()
        try:
            result = db.execute(text("SELECT id_compra, id_proveedor, fecha_de_compra, monto_total, estado FROM compras")).fetchall()
            return [Compra(*row) for row in result]
        finally:
            db.close()

    def get_compra(self, compra_id: int) -> Optional[Compra]:
        db: Session = SessionLocal()
        try:
            result = db.execute(text("SELECT id_compra, id_proveedor, fecha_de_compra, monto_total, estado FROM compras WHERE id_compra = :id_compra"), {"id_compra": compra_id}).fetchone()
            if result:
                return Compra(*result)
            return None
        finally:
            db.close()

    def create_compra(self, data):
        db: Session = SessionLocal()
        try:
            result = db.execute(text('''
                INSERT INTO compras (id_proveedor, monto_total, estado)
                VALUES (:id_proveedor, :monto_total, :estado)
                RETURNING id_compra, id_proveedor, fecha_de_compra, monto_total, estado
            '''), data.dict())
            db.commit()
            row = result.fetchone()
            return Compra(*row)
        finally:
            db.close()

    def update_compra(self, compra_id: int, data):
        db: Session = SessionLocal()
        try:
            fields = []
            params = {"id_compra": compra_id}
            for field, value in data.dict(exclude_unset=True).items():
                fields.append(f"{field} = :{field}")
                params[field] = value
            if not fields:
                return self.get_compra(compra_id)
            db.execute(text(f"UPDATE compras SET {', '.join(fields)} WHERE id_compra = :id_compra"), params)
            db.commit()
            return self.get_compra(compra_id)
        finally:
            db.close()

    def delete_compra(self, compra_id: int):
        db: Session = SessionLocal()
        try:
            result = db.execute(text("DELETE FROM compras WHERE id_compra = :id_compra RETURNING id_compra"), {"id_compra": compra_id})
            db.commit()
            return result.rowcount > 0
        finally:
            db.close() 