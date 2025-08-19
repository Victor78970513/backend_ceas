from domain.accion import Accion
from sqlalchemy.orm import Session
from sqlalchemy import text
from config import SessionLocal
from typing import Optional

class AccionRepository:
    def list_acciones(self):
        db: Session = SessionLocal()
        try:
            result = db.execute(text("""
                SELECT a.id_accion, a.id_club, a.id_socio, a.modalidad_pago, a.estado_accion, 
                       a.certificado_pdf, a.certificado_cifrado, a.fecha_emision_certificado, 
                       a.tipo_accion, s.nombres, s.apellidos
                FROM accion a
                LEFT JOIN socio s ON a.id_socio = s.id_socio
                ORDER BY a.id_accion
            """)).fetchall()
            acciones = []
            for row in result:
                # Mapear campos en el orden correcto según la clase Accion
                accion = Accion(
                    id_accion=row[0],
                    id_club=row[1],
                    id_socio=row[2],
                    modalidad_pago=row[3],
                    estado_accion=row[4],
                    certificado_pdf=row[5],
                    certificado_cifrado=row[6],
                    fecha_emision_certificado=str(row[7]) if row[7] else None,
                    tipo_accion=row[8]
                )
                # Calcular nombre completo del socio
                nombres = row[9] if row[9] else ""
                apellidos = row[10] if row[10] else ""
                accion.socio_titular = f"{nombres} {apellidos}".strip() or "Socio no encontrado"
                acciones.append(accion)
            return acciones
        except Exception as e:
            import logging
            logging.error(f"Error en list_acciones: {str(e)}")
            raise Exception(f"Error al consultar acciones: {str(e)}")
        finally:
            db.close()

    def get_accion(self, accion_id: int) -> Optional[Accion]:
        db: Session = SessionLocal()
        try:
            result = db.execute(text("SELECT id_accion, id_club, id_socio, modalidad_pago, estado_accion, certificado_pdf, certificado_cifrado, fecha_emision_certificado, tipo_accion FROM accion WHERE id_accion = :id_accion"), {"id_accion": accion_id}).fetchone()
            if result:
                return Accion(
                    id_accion=result[0],
                    id_club=result[1],
                    id_socio=result[2],
                    modalidad_pago=result[3],
                    estado_accion=result[4],
                    certificado_pdf=result[5],
                    certificado_cifrado=result[6],
                    fecha_emision_certificado=str(result[7]) if result[7] else None,
                    tipo_accion=result[8]
                )
            return None
        except Exception as e:
            import logging
            logging.error(f"Error en get_accion: {str(e)}")
            raise Exception(f"Error al consultar acción: {str(e)}")
        finally:
            db.close()

    def create_accion(self, data):
        db: Session = SessionLocal()
        try:
            result = db.execute(text('''
                INSERT INTO accion (id_club, id_socio, modalidad_pago, estado_accion, certificado_pdf, certificado_cifrado, tipo_accion)
                VALUES (:id_club, :id_socio, :modalidad_pago, :estado_accion, :certificado_pdf, :certificado_cifrado, :tipo_accion)
                RETURNING id_accion, id_club, id_socio, modalidad_pago, estado_accion, certificado_pdf, certificado_cifrado, fecha_emision_certificado, tipo_accion
            '''), data.dict())
            db.commit()
            row = result.fetchone()
            return Accion(
                id_accion=row[0],
                id_club=row[1],
                id_socio=row[2],
                modalidad_pago=row[3],
                estado_accion=row[4],
                certificado_pdf=row[5],
                certificado_cifrado=row[6],
                fecha_emision_certificado=str(row[7]) if row[7] else None,
                tipo_accion=row[8]
            )
        except Exception as e:
            import logging
            logging.error(f"Error en create_accion: {str(e)}")
            db.rollback()
            raise Exception(f"Error al crear acción: {str(e)}")
        finally:
            db.close()

    def update_accion(self, accion_id: int, data):
        db: Session = SessionLocal()
        try:
            fields = []
            params = {"id_accion": accion_id}
            for field, value in data.dict(exclude_unset=True).items():
                fields.append(f"{field} = :{field}")
                params[field] = value
            if not fields:
                return self.get_accion(accion_id)
            db.execute(text(f"UPDATE accion SET {', '.join(fields)} WHERE id_accion = :id_accion"), params)
            db.commit()
            return self.get_accion(accion_id)
        finally:
            db.close()

    def delete_accion(self, accion_id: int):
        db: Session = SessionLocal()
        try:
            result = db.execute(text("DELETE FROM accion WHERE id_accion = :id_accion RETURNING id_accion"), {"id_accion": accion_id})
            db.commit()
            return result.rowcount > 0
        finally:
            db.close()

    def get_pagos(self, accion_id: int):
        """Obtiene todos los pagos realizados de una acción específica con información descriptiva"""
        db: Session = SessionLocal()
        try:
            result = db.execute(text("""
                SELECT 
                    pa.id_pago, 
                    pa.id_accion, 
                    pa.monto, 
                    pa.fecha_de_pago, 
                    pa.estado_pago,
                    pa.tipo_pago, 
                    pa.observaciones,
                    tp.descripcion as tipo_pago_desc,
                    ep.descripcion as estado_pago_desc
                FROM pagoaccion pa
                LEFT JOIN tipopago tp ON pa.tipo_pago = tp.id_tipo_pago
                LEFT JOIN estadopago ep ON pa.estado_pago = ep.id_estado_pago
                WHERE pa.id_accion = :accion_id
                ORDER BY pa.fecha_de_pago DESC
            """), {"accion_id": accion_id}).fetchall()
            
            pagos = []
            for row in result:
                pago = {
                    "id_pago": row[0],
                    "id_accion": row[1],
                    "monto": float(row[2]) if row[2] else 0.0,
                    "fecha_pago": str(row[3]) if row[3] else None,
                    "estado_pago_id": row[4],
                    "tipo_pago_id": row[5],
                    "observaciones": row[6],
                    "tipo_pago_desc": row[7],
                    "estado_pago_desc": row[8]
                }
                pagos.append(pago)
            
            return pagos
            
        except Exception as e:
            import logging
            logging.error(f"Error en get_pagos: {str(e)}")
            # Si hay error, retornar lista vacía en lugar de fallar
            return []
        finally:
            db.close()

    def get_estado_accion(self, estado_accion_id: int):
        """Obtiene el estado de acción por ID"""
        db: Session = SessionLocal()
        try:
            result = db.execute(text("""
                SELECT id_estado_accion, nombre_estado_accion
                FROM estadoaccion 
                WHERE id_estado_accion = :estado_accion_id
            """), {"estado_accion_id": estado_accion_id}).fetchone()
            
            if result:
                return {
                    "id_estado_accion": result[0],
                    "nombre_estado_accion": result[1]
                }
            return None
        except Exception as e:
            import logging
            logging.error(f"Error en get_estado_accion: {str(e)}")
            return None
        finally:
            db.close()

    def get_socio_by_id(self, socio_id: int):
        """Obtiene datos del socio por ID"""
        db: Session = SessionLocal()
        try:
            result = db.execute(text("""
                SELECT id_socio, nombres, apellidos, ci_nit, correo_electronico
                FROM socio 
                WHERE id_socio = :socio_id
            """), {"socio_id": socio_id}).fetchone()
            
            if result:
                return {
                    "id_socio": result[0],
                    "nombres": result[1],
                    "apellidos": result[2],
                    "ci_nit": result[3],
                    "correo_electronico": result[4]
                }
            return None
        except Exception as e:
            import logging
            logging.error(f"Error en get_socio_by_id: {str(e)}")
            return None
        finally:
            db.close()

    def get_modalidad_pago(self, modalidad_id: int):
        """Obtiene la modalidad de pago por ID"""
        db: Session = SessionLocal()
        try:
            result = db.execute(text("""
                SELECT id_modalidad_pago, descripcion, meses_de_gracia, 
                       porcentaje_renovacion_inicial, porcentaje_renovacion_mensual, 
                       costo_renovacion_estandar, cantidad_cuotas
                FROM modalidadpago 
                WHERE id_modalidad_pago = :modalidad_id
            """), {"modalidad_id": modalidad_id}).fetchone()
            
            if result:
                return {
                    "id_modalidad_pago": result[0],
                    "descripcion": result[1],
                    "meses_de_gracia": result[2],
                    "porcentaje_renovacion_inicial": float(result[3]) if result[3] else 0.0,
                    "porcentaje_renovacion_mensual": float(result[4]) if result[4] else 0.0,
                    "costo_renovacion_estandar": float(result[5]) if result[5] else 0.0,
                    "cantidad_cuotas": result[6] if result[6] else 1
                }
            return None
        except Exception as e:
            import logging
            logging.error(f"Error en get_modalidad_pago: {str(e)}")
            raise Exception(f"Error al consultar modalidad de pago: {str(e)}")
        finally:
            db.close()

    def calcular_estado_pagos(self, accion, modalidad, pagos_realizados):
        """Calcula el estado completo de pagos de una acción"""
        try:
            # Calcular total a pagar según modalidad
            # Usar el campo cantidad_cuotas para calcular el total real
            cantidad_cuotas = modalidad.get("cantidad_cuotas", 1)
            costo_por_cuota = modalidad["costo_renovacion_estandar"]
            precio_renovacion = cantidad_cuotas * costo_por_cuota
            
            print(f"DEBUG - Cantidad cuotas: {cantidad_cuotas}")
            print(f"DEBUG - Costo por cuota: {costo_por_cuota}")
            print(f"DEBUG - Precio renovación total: {precio_renovacion}")
            
            # Calcular total pagado (solo pagos aprobados/validados)
            # Asumiendo que estado_pago = 1 es "APROBADO" o similar
            total_pagado = sum(pago.get("monto", 0) for pago in pagos_realizados if pago.get("estado_pago_id") == 1)
            
            # Calcular saldo pendiente (no puede ser negativo)
            saldo_pendiente = max(0, precio_renovacion - total_pagado)
            
            # Calcular pagos restantes
            pagos_restantes = 0
            if saldo_pendiente > 0:
                # Calcular cuántos pagos mensuales faltan
                monto_pago_mensual = precio_renovacion * (modalidad["porcentaje_renovacion_mensual"] / 100)
                if monto_pago_mensual > 0:
                    pagos_restantes = int(saldo_pendiente / monto_pago_mensual) + (1 if saldo_pendiente % monto_pago_mensual > 0 else 0)
            
            # Determinar estado
            if saldo_pendiente <= 0:
                estado_pago = "COMPLETAMENTE_PAGADA"
            elif saldo_pendiente <= (precio_renovacion * 0.1):  # Menos del 10% pendiente
                estado_pago = "CASI_PAGADA"
            elif saldo_pendiente <= (precio_renovacion * 0.5):  # Menos del 50% pendiente
                estado_pago = "PARCIALMENTE_PAGADA"
            else:
                estado_pago = "PENDIENTE_DE_PAGO"
            
            # Contar pagos aprobados
            pagos_aprobados = len([p for p in pagos_realizados if p.get("estado_pago_id") == 1])
            
            # Calcular porcentaje pagado (máximo 100%)
            porcentaje_pagado = min(100.0, round((total_pagado / precio_renovacion) * 100, 2)) if precio_renovacion > 0 else 100.0
            
            return {
                "id_accion": accion.id_accion,
                "modalidad_pago": {
                    "id": modalidad["id_modalidad_pago"],
                    "descripcion": modalidad["descripcion"],
                    "meses_de_gracia": modalidad["meses_de_gracia"],
                    "porcentaje_renovacion_inicial": modalidad["porcentaje_renovacion_inicial"],
                    "porcentaje_renovacion_mensual": modalidad["porcentaje_renovacion_mensual"],
                    "costo_renovacion_estandar": modalidad["costo_renovacion_estandar"],
                    "cantidad_cuotas": modalidad["cantidad_cuotas"]
                },
                "precio_renovacion": precio_renovacion,
                "total_pagado": total_pagado,
                "saldo_pendiente": saldo_pendiente,
                "pagos_restantes": pagos_restantes,
                "estado_pago": estado_pago,
                "porcentaje_pagado": porcentaje_pagado,
                "pagos_realizados": pagos_aprobados,
                "total_pagos_registrados": len(pagos_realizados),
                "detalle_pagos": pagos_realizados
            }
            
        except Exception as e:
            import logging
            logging.error(f"Error en calcular_estado_pagos: {str(e)}")
            raise Exception(f"Error al calcular estado de pagos: {str(e)}") 