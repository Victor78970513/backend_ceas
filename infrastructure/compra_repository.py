from domain.compra import Compra
from sqlalchemy.orm import Session
from sqlalchemy import text
from config import SessionLocal
from typing import Optional
import logging

class CompraRepository:
    def list_compras(self):
        db: Session = SessionLocal()
        try:
            # Query con JOIN para obtener nombre y categoría del proveedor
            result = db.execute(text("""
                SELECT 
                    c.id_compra, 
                    c.id_proveedor, 
                    c.fecha_de_compra, 
                    c.monto_total, 
                    c.estado, 
                    c.numero_factura,
                    c.observaciones,
                    p.nombre_proveedor,
                    p.categoria
                FROM compras c
                LEFT JOIN proveedores p ON c.id_proveedor = p.id_proveedor
                ORDER BY c.fecha_de_compra DESC
            """)).fetchall()
            
            compras = []
            for row in result:
                # Convertir fechas de datetime a string
                fecha_compra = str(row[2]) if row[2] else None
                
                compra = Compra(
                    id_compra=row[0],
                    id_proveedor=row[1],
                    fecha_de_compra=fecha_compra,
                    monto_total=float(row[3]) if row[3] else 0.0,
                    estado=row[4],
                    numero_factura=row[5] if row[5] else None,
                    observaciones=row[6] if row[6] else None,
                    proveedor=row[7] if row[7] else None,    # Nombre del proveedor
                    categoria_proveedor=row[8] if row[8] else None    # Categoría del proveedor
                )
                compras.append(compra)
            return compras
        except Exception as e:
            logging.error(f"Error en list_compras: {str(e)}")
            raise Exception(f"Error al consultar compras: {str(e)}")
        finally:
            db.close()

    def get_compra(self, compra_id: int) -> Optional[Compra]:
        db: Session = SessionLocal()
        try:
            # Query con JOIN para obtener nombre y categoría del proveedor
            result = db.execute(text("""
                SELECT 
                    c.id_compra, 
                    c.id_proveedor, 
                    c.fecha_de_compra, 
                    c.monto_total, 
                    c.estado, 
                    c.numero_factura,
                    c.observaciones,
                    p.nombre_proveedor,
                    p.categoria
                FROM compras c
                LEFT JOIN proveedores p ON c.id_proveedor = p.id_proveedor
                WHERE c.id_compra = :id_compra
            """), {"id_compra": compra_id}).fetchone()
            
            if result:
                # Convertir fechas de datetime a string
                fecha_compra = str(result[2]) if result[2] else None
                
                return Compra(
                    id_compra=result[0],
                    id_proveedor=result[1],
                    fecha_de_compra=fecha_compra,
                    monto_total=float(result[3]) if result[3] else 0.0,
                    estado=result[4],
                    numero_factura=result[5] if result[5] else None,
                    observaciones=result[6] if result[6] else None,
                    proveedor=result[7] if result[7] else None,    # Nombre del proveedor
                    categoria_proveedor=result[8] if result[8] else None    # Categoría del proveedor
                )
            return None
        except Exception as e:
            logging.error(f"Error en get_compra: {str(e)}")
            raise Exception(f"Error al consultar compra: {str(e)}")
        finally:
            db.close()

    def create_compra(self, data):
        db: Session = SessionLocal()
        try:
            result = db.execute(text('''
                INSERT INTO compras (id_proveedor, monto_total, estado, numero_factura, observaciones)
                VALUES (:id_proveedor, :monto_total, :estado, :numero_factura, :observaciones)
                RETURNING id_compra, id_proveedor, fecha_de_compra, monto_total, estado, numero_factura, observaciones
            '''), data.dict())
            db.commit()
            row = result.fetchone()
            
            # Convertir fechas de datetime a string
            fecha_compra = str(row[2]) if row[2] else None
            
            # Obtener nombre del proveedor
            proveedor_info = self._get_proveedor_info(db, row[1])
            
            return Compra(
                id_compra=row[0],
                id_proveedor=row[1],
                fecha_de_compra=fecha_compra,
                monto_total=float(row[3]) if row[3] else 0.0,
                estado=row[4],
                numero_factura=row[5] if row[5] else None,
                observaciones=row[6] if row[6] else None,
                proveedor=proveedor_info['nombre_proveedor'],
                categoria_proveedor=proveedor_info.get('categoria')
            )
        except Exception as e:
            logging.error(f"Error en create_compra: {str(e)}")
            raise Exception(f"Error al crear compra: {str(e)}")
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
    
    def _get_proveedor_info(self, db: Session, id_proveedor: int) -> dict:
        """Obtiene información del proveedor (nombre y categoría)"""
        try:
            result = db.execute(text("""
                SELECT nombre_proveedor, categoria FROM proveedores WHERE id_proveedor = :id_proveedor
            """), {"id_proveedor": id_proveedor}).fetchone()
            
            if result:
                return {
                    'nombre_proveedor': result[0] if result[0] else None,
                    'categoria': result[1] if result[1] else None
                }
            return {'nombre_proveedor': None, 'categoria': None}
        except Exception as e:
            logging.error(f"Error al obtener información del proveedor: {str(e)}")
            return {'nombre_proveedor': None, 'categoria': None} 