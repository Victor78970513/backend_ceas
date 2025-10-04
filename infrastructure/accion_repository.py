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
                       a.tipo_accion, s.nombres, s.apellidos, a.cantidad_acciones, a.precio_unitario,
                       a.total_pago, a.metodo_pago, a.qr_data, a.fecha_venta, a.comprobante_path, a.fecha_comprobante
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
                    tipo_accion=row[8],
                    cantidad_acciones=row[11] if row[11] else 1,
                    precio_unitario=float(row[12]) if row[12] else 0.00,
                    total_pago=float(row[13]) if row[13] else 0.00,
                    metodo_pago=row[14] if row[14] else "efectivo",
                    qr_data=row[15],
                    fecha_venta=str(row[16]) if row[16] else None,
                    comprobante_path=row[17],
                    fecha_comprobante=str(row[18]) if row[18] else None
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
            result = db.execute(text("SELECT id_accion, id_club, id_socio, modalidad_pago, estado_accion, certificado_pdf, certificado_cifrado, fecha_emision_certificado, tipo_accion, cantidad_acciones, precio_unitario, total_pago, metodo_pago, qr_data, fecha_venta, comprobante_path, fecha_comprobante FROM accion WHERE id_accion = :id_accion"), {"id_accion": accion_id}).fetchone()
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
                    tipo_accion=result[8],
                    cantidad_acciones=result[9] if result[9] else 1,
                    precio_unitario=float(result[10]) if result[10] else 0.00,
                    total_pago=float(result[11]) if result[11] else 0.00,
                    metodo_pago=result[12] if result[12] else "efectivo",
                    qr_data=result[13],
                    fecha_venta=str(result[14]) if result[14] else None,
                    comprobante_path=result[15],
                    fecha_comprobante=str(result[16]) if result[16] else None
                )
            return None
        except Exception as e:
            import logging
            logging.error(f"Error en get_accion: {str(e)}")
            raise Exception(f"Error al consultar acción: {str(e)}")
        finally:
            db.close()

    def get_acciones_by_socio(self, socio_id: int):
        """Obtiene todas las acciones de un socio específico"""
        db: Session = SessionLocal()
        try:
            result = db.execute(text("""
                SELECT id_accion, id_club, id_socio, modalidad_pago, estado_accion, 
                       certificado_pdf, certificado_cifrado, fecha_emision_certificado, 
                       tipo_accion, cantidad_acciones, precio_unitario, total_pago, 
                       metodo_pago, qr_data, fecha_venta, comprobante_path, fecha_comprobante
                FROM accion 
                WHERE id_socio = :socio_id
                ORDER BY id_accion DESC
            """), {"socio_id": socio_id}).fetchall()
            
            acciones = []
            for row in result:
                accion = Accion(
                    id_accion=row[0],
                    id_club=row[1],
                    id_socio=row[2],
                    modalidad_pago=row[3],
                    estado_accion=row[4],
                    certificado_pdf=row[5],
                    certificado_cifrado=row[6],
                    fecha_emision_certificado=str(row[7]) if row[7] else None,
                    tipo_accion=row[8],
                    cantidad_acciones=row[9] if row[9] else 1,
                    precio_unitario=float(row[10]) if row[10] else 0.00,
                    total_pago=float(row[11]) if row[11] else 0.00,
                    metodo_pago=row[12] if row[12] else "efectivo",
                    qr_data=row[13],
                    fecha_venta=str(row[14]) if row[14] else None,
                    comprobante_path=row[15],
                    fecha_comprobante=str(row[16]) if row[16] else None
                )
                acciones.append(accion)
            return acciones
        except Exception as e:
            import logging
            logging.error(f"Error en get_acciones_by_socio: {str(e)}")
            raise Exception(f"Error al consultar acciones del socio: {str(e)}")
        finally:
            db.close()

    def create_accion(self, data):
        db: Session = SessionLocal()
        try:
            result = db.execute(text('''
                INSERT INTO accion (id_club, id_socio, modalidad_pago, estado_accion, certificado_pdf, certificado_cifrado, tipo_accion, cantidad_acciones, precio_unitario, total_pago, metodo_pago)
                VALUES (:id_club, :id_socio, :modalidad_pago, :estado_accion, :certificado_pdf, :certificado_cifrado, :tipo_accion, :cantidad_acciones, :precio_unitario, :total_pago, :metodo_pago)
                RETURNING id_accion, id_club, id_socio, modalidad_pago, estado_accion, certificado_pdf, certificado_cifrado, fecha_emision_certificado, tipo_accion, cantidad_acciones, precio_unitario, total_pago, metodo_pago, qr_data, fecha_venta, comprobante_path, fecha_comprobante
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
                tipo_accion=row[8],
                cantidad_acciones=row[9] if row[9] else 1,
                precio_unitario=float(row[10]) if row[10] else 0.00,
                total_pago=float(row[11]) if row[11] else 0.00,
                metodo_pago=row[12] if row[12] else "efectivo",
                qr_data=row[13],
                fecha_venta=str(row[14]) if row[14] else None,
                comprobante_path=row[15],
                fecha_comprobante=str(row[16]) if row[16] else None
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
            
            # Si data es un diccionario, usarlo directamente
            if isinstance(data, dict):
                data_dict = data
            else:
                # Si es un schema Pydantic, convertir a diccionario
                data_dict = data.dict(exclude_unset=True)
            
            for field, value in data_dict.items():
                if value is not None:  # Solo actualizar campos que no sean None
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
                FROM pago_accion pa
                LEFT JOIN tipo_pago tp ON pa.tipo_pago = tp.id_tipo_pago
                LEFT JOIN estado_pago ep ON pa.estado_pago = ep.id_estado_pago
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
                FROM estado_accion 
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
                FROM modalidad_pago 
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
            from datetime import datetime, timedelta
            
            # Calcular el precio total basado en la modalidad de pago
            # Si la modalidad tiene cantidad_cuotas > 1, el precio total es: precio_unitario * cantidad_cuotas
            # Si no, usar el total_pago directamente
            cantidad_cuotas = modalidad.get("cantidad_cuotas", 1)
            precio_unitario = float(accion.precio_unitario) if hasattr(accion, 'precio_unitario') and accion.precio_unitario else 0.0
            total_pago_accion = float(accion.total_pago) if hasattr(accion, 'total_pago') and accion.total_pago else 0.0
            
            # Determinar el precio total correcto
            if cantidad_cuotas > 1 and precio_unitario > 0:
                # Modalidad con múltiples cuotas: precio_unitario * cantidad_cuotas
                precio_total = precio_unitario * cantidad_cuotas
            else:
                # Modalidad de pago único: usar total_pago
                precio_total = total_pago_accion
            
            # El costo de renovación mensual viene de la modalidad
            costo_renovacion_mensual = modalidad["costo_renovacion_estandar"]
            
            # Calcular total pagado (solo pagos aprobados/validados)
            # estado_pago_id = 2 es "Pagado" según la BD
            total_pagado = sum(pago.get("monto", 0) for pago in pagos_realizados if pago.get("estado_pago_id") == 2)
            
            # Calcular saldo pendiente del precio total
            saldo_pendiente = max(0, precio_total - total_pagado)
            
            # Calcular pagos restantes basado en cuotas de la modalidad
            pagos_realizados_count = len([p for p in pagos_realizados if p.get("estado_pago_id") == 2])
            pagos_restantes = max(0, cantidad_cuotas - pagos_realizados_count)
            
            # Determinar estado
            if saldo_pendiente <= 0:
                estado_pago = "COMPLETAMENTE_PAGADA"
            elif total_pagado > 0:
                estado_pago = "PARCIALMENTE_PAGADA"
            else:
                estado_pago = "PENDIENTE_DE_PAGO"
            
            # Calcular porcentaje pagado basado en el precio total
            porcentaje_pagado = round((total_pagado / precio_total) * 100, 2) if precio_total > 0 else 0.0
            
            # Calcular si puede renovar (después de meses de gracia)
            fecha_creacion = accion.fecha_creacion if hasattr(accion, 'fecha_creacion') else datetime.now()
            meses_de_gracia = modalidad.get("meses_de_gracia", 0)
            fecha_renovacion = fecha_creacion + timedelta(days=meses_de_gracia * 30)  # Aproximación
            puede_renovar = datetime.now() >= fecha_renovacion
            
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
                "precio_inicial": precio_total,
                "costo_renovacion_mensual": costo_renovacion_mensual,
                "total_pagado": total_pagado,
                "saldo_pendiente": saldo_pendiente,
                "pagos_restantes": pagos_restantes,
                "estado_pago": estado_pago,
                "porcentaje_pagado": porcentaje_pagado,
                "pagos_realizados": pagos_realizados_count,
                "renovar": puede_renovar,
                "total_pagos_registrados": len(pagos_realizados),
                "detalle_pagos": pagos_realizados
            }
            
        except Exception as e:
            import logging
            logging.error(f"Error en calcular_estado_pagos: {str(e)}")
            raise Exception(f"Error al calcular estado de pagos: {str(e)}") 