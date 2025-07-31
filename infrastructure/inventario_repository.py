from domain.inventario import ProductoInventario
from sqlalchemy.orm import Session
from sqlalchemy import text
from config import SessionLocal
from typing import Optional

class InventarioRepository:
    def list_productos(self):
        db: Session = SessionLocal()
        try:
            result = db.execute(text("SELECT id_producto, nombre_producto, descripcion, cantidad_en_stock, precio_unitario, id_club FROM inventario")).fetchall()
            return [ProductoInventario(*row) for row in result]
        finally:
            db.close()

    def get_producto(self, producto_id: int) -> Optional[ProductoInventario]:
        db: Session = SessionLocal()
        try:
            result = db.execute(text("SELECT id_producto, nombre_producto, descripcion, cantidad_en_stock, precio_unitario, id_club FROM inventario WHERE id_producto = :id_producto"), {"id_producto": producto_id}).fetchone()
            if result:
                return ProductoInventario(*result)
            return None
        finally:
            db.close()

    def create_producto(self, data):
        db: Session = SessionLocal()
        try:
            result = db.execute(text('''
                INSERT INTO inventario (nombre_producto, descripcion, cantidad_en_stock, precio_unitario, id_club)
                VALUES (:nombre_producto, :descripcion, :cantidad_en_stock, :precio_unitario, :id_club)
                RETURNING id_producto, nombre_producto, descripcion, cantidad_en_stock, precio_unitario, id_club
            '''), data.dict())
            db.commit()
            row = result.fetchone()
            return ProductoInventario(*row)
        finally:
            db.close()

    def update_producto(self, producto_id: int, data):
        db: Session = SessionLocal()
        try:
            fields = []
            params = {"id_producto": producto_id}
            for field, value in data.dict(exclude_unset=True).items():
                fields.append(f"{field} = :{field}")
                params[field] = value
            if not fields:
                return self.get_producto(producto_id)
            db.execute(text(f"UPDATE inventario SET {', '.join(fields)} WHERE id_producto = :id_producto"), params)
            db.commit()
            return self.get_producto(producto_id)
        finally:
            db.close()

    def delete_producto(self, producto_id: int):
        db: Session = SessionLocal()
        try:
            result = db.execute(text("DELETE FROM inventario WHERE id_producto = :id_producto RETURNING id_producto"), {"id_producto": producto_id})
            db.commit()
            return result.rowcount > 0
        finally:
            db.close() 