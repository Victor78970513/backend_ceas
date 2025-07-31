from domain.proveedor import Proveedor
from sqlalchemy.orm import Session
from sqlalchemy import text
from config import SessionLocal
from typing import Optional

class ProveedorRepository:
    def list_proveedores(self):
        db: Session = SessionLocal()
        try:
            result = db.execute(text("SELECT id_proveedor, nombre_proveedor, contacto, telefono, correo_electronico, direccion FROM proveedores")).fetchall()
            return [Proveedor(*row) for row in result]
        finally:
            db.close()

    def get_proveedor(self, proveedor_id: int) -> Optional[Proveedor]:
        db: Session = SessionLocal()
        try:
            result = db.execute(text("SELECT id_proveedor, nombre_proveedor, contacto, telefono, correo_electronico, direccion FROM proveedores WHERE id_proveedor = :id_proveedor"), {"id_proveedor": proveedor_id}).fetchone()
            if result:
                return Proveedor(*result)
            return None
        finally:
            db.close()

    def create_proveedor(self, data):
        db: Session = SessionLocal()
        try:
            result = db.execute(text('''
                INSERT INTO proveedores (nombre_proveedor, contacto, telefono, correo_electronico, direccion)
                VALUES (:nombre_proveedor, :contacto, :telefono, :correo_electronico, :direccion)
                RETURNING id_proveedor, nombre_proveedor, contacto, telefono, correo_electronico, direccion
            '''), data.dict())
            db.commit()
            row = result.fetchone()
            return Proveedor(*row)
        finally:
            db.close()

    def update_proveedor(self, proveedor_id: int, data):
        db: Session = SessionLocal()
        try:
            fields = []
            params = {"id_proveedor": proveedor_id}
            for field, value in data.dict(exclude_unset=True).items():
                fields.append(f"{field} = :{field}")
                params[field] = value
            if not fields:
                return self.get_proveedor(proveedor_id)
            db.execute(text(f"UPDATE proveedores SET {', '.join(fields)} WHERE id_proveedor = :id_proveedor"), params)
            db.commit()
            return self.get_proveedor(proveedor_id)
        finally:
            db.close()

    def delete_proveedor(self, proveedor_id: int):
        db: Session = SessionLocal()
        try:
            result = db.execute(text("DELETE FROM proveedores WHERE id_proveedor = :id_proveedor RETURNING id_proveedor"), {"id_proveedor": proveedor_id})
            db.commit()
            return result.rowcount > 0
        finally:
            db.close() 