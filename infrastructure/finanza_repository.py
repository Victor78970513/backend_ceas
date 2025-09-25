from domain.finanza import MovimientoFinanciero
from sqlalchemy.orm import Session
from sqlalchemy import text
from config import SessionLocal
from typing import Optional
from decimal import Decimal
import logging

class FinanzaRepository:
    def list_movimientos(self):
        db: Session = SessionLocal()
        try:
            # Query con JOINs para obtener todos los datos necesarios
            result = db.execute(text("""
                SELECT 
                    mf.id_movimiento,
                    mf.id_club,
                    mf.tipo_movimiento,
                    mf.descripcion,
                    mf.monto,
                    mf.fecha,
                    mf.estado,
                    mf.referencia_relacionada,
                    mf.metodo_pago,
                    c.nombre_club,
                    -- Determinar categoría basada en tipo_movimiento y descripción
                    CASE 
                        WHEN mf.tipo_movimiento = 'INGRESO' AND mf.descripcion ILIKE '%cuota%' THEN 'Cuotas'
                        WHEN mf.tipo_movimiento = 'INGRESO' AND mf.descripcion ILIKE '%donación%' THEN 'Donaciones'
                        WHEN mf.tipo_movimiento = 'INGRESO' AND mf.descripcion ILIKE '%evento%' THEN 'Eventos'
                        WHEN mf.tipo_movimiento = 'EGRESO' AND mf.descripcion ILIKE '%servicio%' THEN 'Servicios'
                        WHEN mf.tipo_movimiento = 'EGRESO' AND mf.descripcion ILIKE '%compra%' THEN 'Compras'
                        WHEN mf.tipo_movimiento = 'EGRESO' AND mf.descripcion ILIKE '%material%' THEN 'Materiales'
                        ELSE 'Otros'
                    END as categoria,
                    -- Generar número de comprobante basado en ID y fecha
                    CONCAT('MF-', mf.id_movimiento, '-', TO_CHAR(mf.fecha, 'YYYYMMDD')) as numero_comprobante
                FROM movimiento_financiero mf
                LEFT JOIN club c ON mf.id_club = c.id_club
                ORDER BY mf.fecha DESC, mf.id_movimiento DESC
            """)).fetchall()
            
            movimientos = []
            for row in result:
                # Convertir tipos de datos
                monto = float(row[4]) if row[4] else 0.0
                fecha = str(row[5]) if row[5] else None
                
                movimiento = MovimientoFinanciero(
                    id_movimiento=row[0],
                    id_club=row[1],
                    tipo_movimiento=row[2],
                    descripcion=row[3],
                    monto=Decimal(str(monto)),
                    fecha=fecha,
                    estado=row[6],
                    referencia_relacionada=row[7],
                    metodo_pago=row[8]
                )
                
                # Agregar campos adicionales como atributos
                movimiento.nombre_club = row[9]
                movimiento.categoria = row[10]
                movimiento.numero_comprobante = row[11]
                
                movimientos.append(movimiento)
            return movimientos
        except Exception as e:
            logging.error(f"Error en list_movimientos: {str(e)}")
            raise Exception(f"Error al consultar movimientos financieros: {str(e)}")
        finally:
            db.close()

    def get_movimiento(self, movimiento_id: int) -> Optional[MovimientoFinanciero]:
        db: Session = SessionLocal()
        try:
            # Query con JOINs para obtener todos los datos necesarios
            result = db.execute(text("""
                SELECT 
                    mf.id_movimiento,
                    mf.id_club,
                    mf.tipo_movimiento,
                    mf.descripcion,
                    mf.monto,
                    mf.fecha,
                    mf.estado,
                    mf.referencia_relacionada,
                    mf.metodo_pago,
                    c.nombre_club,
                    -- Determinar categoría basada en tipo_movimiento y descripción
                    CASE 
                        WHEN mf.tipo_movimiento = 'INGRESO' AND mf.descripcion ILIKE '%cuota%' THEN 'Cuotas'
                        WHEN mf.tipo_movimiento = 'INGRESO' AND mf.descripcion ILIKE '%donación%' THEN 'Donaciones'
                        WHEN mf.tipo_movimiento = 'INGRESO' AND mf.descripcion ILIKE '%evento%' THEN 'Eventos'
                        WHEN mf.tipo_movimiento = 'EGRESO' AND mf.descripcion ILIKE '%servicio%' THEN 'Servicios'
                        WHEN mf.tipo_movimiento = 'EGRESO' AND mf.descripcion ILIKE '%compra%' THEN 'Compras'
                        WHEN mf.tipo_movimiento = 'EGRESO' AND mf.descripcion ILIKE '%material%' THEN 'Materiales'
                        ELSE 'Otros'
                    END as categoria,
                    -- Obtener nombre del socio si la referencia contiene "Socio ID:"
                    CASE 
                        WHEN mf.referencia_relacionada ILIKE 'Socio ID:%' THEN 
                            (SELECT CONCAT(s.nombres, ' ', s.apellidos) 
                             FROM socio s 
                             WHERE s.id_socio = CAST(REPLACE(mf.referencia_relacionada, 'Socio ID: ', '') AS INTEGER))
                        ELSE NULL
                    END as nombre_socio,
                    -- Obtener nombre del proveedor si la referencia contiene "Proveedor:"
                    CASE 
                        WHEN mf.referencia_relacionada ILIKE 'Proveedor:%' THEN 
                            (SELECT nombre_proveedor 
                             FROM proveedores 
                             WHERE id_proveedor = CAST(REPLACE(mf.referencia_relacionada, 'Proveedor: ', '') AS INTEGER))
                        ELSE NULL
                    END as nombre_proveedor,
                    -- Generar número de comprobante basado en ID y fecha
                    CONCAT('MF-', mf.id_movimiento, '-', TO_CHAR(mf.fecha, 'YYYYMMDD')) as numero_comprobante
                FROM movimiento_financiero mf
                LEFT JOIN club c ON mf.id_club = c.id_club
                WHERE mf.id_movimiento = :id_movimiento
            """), {"id_movimiento": movimiento_id}).fetchone()
            
            if result:
                # Convertir tipos de datos
                monto = float(result[4]) if result[4] else 0.0
                fecha = str(result[5]) if result[5] else None
                
                movimiento = MovimientoFinanciero(
                    id_movimiento=result[0],
                    id_club=result[1],
                    tipo_movimiento=result[2],
                    descripcion=result[3],
                    monto=Decimal(str(monto)),
                    fecha=fecha,
                    estado=result[6],
                    referencia_relacionada=result[7],
                    metodo_pago=result[8]
                )
                
                # Agregar campos adicionales como atributos
                movimiento.nombre_club = result[9]
                movimiento.categoria = result[10]
                movimiento.nombre_socio = result[11]
                movimiento.nombre_proveedor = result[12]
                movimiento.numero_comprobante = result[13]
                
                return movimiento
            return None
        except Exception as e:
            logging.error(f"Error en get_movimiento: {str(e)}")
            raise Exception(f"Error al consultar movimiento financiero: {str(e)}")
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
            
            # Convertir tipos de datos
            monto = float(row[4]) if row[4] else 0.0
            fecha = str(row[5]) if row[5] else None
            
            return MovimientoFinanciero(
                id_movimiento=row[0],
                id_club=row[1],
                tipo_movimiento=row[2],
                descripcion=row[3],
                monto=Decimal(str(monto)),
                fecha=fecha,
                estado=row[6],
                referencia_relacionada=row[7],
                metodo_pago=row[8]
            )
        except Exception as e:
            logging.error(f"Error en create_movimiento: {str(e)}")
            raise Exception(f"Error al crear movimiento financiero: {str(e)}")
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