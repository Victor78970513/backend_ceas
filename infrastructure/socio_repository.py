from domain.socio import Socio
from sqlalchemy.orm import Session
from sqlalchemy import text
from config import SessionLocal
from typing import Optional
import logging
from datetime import datetime

class SocioRepository:
    def list_socios(self):
        db: Session = SessionLocal()
        try:
            # Verificar si la tabla existe
            result = db.execute(text("SELECT id_socio, id_club, nombres, apellidos, ci_nit, telefono, correo_electronico, direccion, estado, fecha_de_registro, fecha_nacimiento, tipo_membresia, id_usuario FROM socio")).fetchall()
            socios = []
            for row in result:
                # Convertir datetime a string si es necesario
                fecha_registro = str(row[9]) if row[9] else None
                fecha_nacimiento = str(row[10]) if row[10] else None
                
                socio = Socio(
                    id_socio=row[0],
                    id_club=row[1],
                    nombres=row[2],
                    apellidos=row[3],
                    ci_nit=row[4],
                    telefono=row[5],
                    correo_electronico=row[6],
                    direccion=row[7],
                    estado=row[8],
                    fecha_de_registro=fecha_registro,
                    fecha_nacimiento=fecha_nacimiento,
                    tipo_membresia=row[11],
                    id_usuario=row[12]
                )
                socios.append(socio)
            return socios
        except Exception as e:
            logging.error(f"Error en list_socios: {str(e)}")
            raise Exception(f"Error al consultar socios: {str(e)}")
        finally:
            db.close()

    def get_socio(self, socio_id: int) -> Optional[Socio]:
        db: Session = SessionLocal()
        try:
            result = db.execute(text("SELECT id_socio, id_club, nombres, apellidos, ci_nit, telefono, correo_electronico, direccion, estado, fecha_de_registro, fecha_nacimiento, tipo_membresia, id_usuario FROM socio WHERE id_socio = :id_socio"), {"id_socio": socio_id}).fetchone()
            if result:
                # Convertir datetime a string si es necesario
                fecha_registro = str(result[9]) if result[9] else None
                fecha_nacimiento = str(result[10]) if result[10] else None
                
                return Socio(
                    id_socio=result[0],
                    id_club=result[1],
                    nombres=result[2],
                    apellidos=result[3],
                    ci_nit=result[4],
                    telefono=result[5],
                    correo_electronico=result[6],
                    direccion=result[7],
                    estado=result[8],
                    fecha_de_registro=fecha_registro,
                    fecha_nacimiento=fecha_nacimiento,
                    tipo_membresia=result[11],
                    id_usuario=result[12]
                )
            return None
        except Exception as e:
            logging.error(f"Error en get_socio: {str(e)}")
            raise Exception(f"Error al consultar socio: {str(e)}")
        finally:
            db.close()

    def create_socio(self, data):
        db: Session = SessionLocal()
        try:
            result = db.execute(text('''
                INSERT INTO socio (id_club, nombres, apellidos, ci_nit, telefono, correo_electronico, direccion, estado, fecha_nacimiento, tipo_membresia, id_usuario)
                VALUES (:id_club, :nombres, :apellidos, :ci_nit, :telefono, :correo_electronico, :direccion, :estado, :fecha_nacimiento, :tipo_membresia, :id_usuario)
                RETURNING id_socio, id_club, nombres, apellidos, ci_nit, telefono, correo_electronico, direccion, estado, fecha_de_registro, fecha_nacimiento, tipo_membresia, id_usuario
            '''), data.dict())
            db.commit()
            row = result.fetchone()
            
            # Convertir datetime a string si es necesario
            fecha_registro = str(row[9]) if row[9] else None
            fecha_nacimiento = str(row[10]) if row[10] else None
            
            return Socio(
                id_socio=row[0],
                id_club=row[1],
                nombres=row[2],
                apellidos=row[3],
                ci_nit=row[4],
                telefono=row[5],
                correo_electronico=row[6],
                direccion=row[7],
                estado=row[8],
                fecha_de_registro=fecha_registro,
                fecha_nacimiento=fecha_nacimiento,
                tipo_membresia=row[11],
                id_usuario=row[12]
            )
        except Exception as e:
            logging.error(f"Error en create_socio: {str(e)}")
            db.rollback()
            raise Exception(f"Error al crear socio: {str(e)}")
        finally:
            db.close()

    def update_socio(self, socio_id: int, data):
        db: Session = SessionLocal()
        try:
            fields = []
            params = {"id_socio": socio_id}
            for field, value in data.dict(exclude_unset=True).items():
                fields.append(f"{field} = :{field}")
                params[field] = value
            if not fields:
                return self.get_socio(socio_id)
            db.execute(text(f"UPDATE socio SET {', '.join(fields)} WHERE id_socio = :id_socio"), params)
            db.commit()
            return self.get_socio(socio_id)
        except Exception as e:
            logging.error(f"Error en update_socio: {str(e)}")
            db.rollback()
            raise Exception(f"Error al actualizar socio: {str(e)}")
        finally:
            db.close()

    def delete_socio(self, socio_id: int):
        db: Session = SessionLocal()
        try:
            result = db.execute(text("DELETE FROM socio WHERE id_socio = :id_socio RETURNING id_socio"), {"id_socio": socio_id})
            db.commit()
            return result.rowcount > 0
        except Exception as e:
            logging.error(f"Error en delete_socio: {str(e)}")
            db.rollback()
            raise Exception(f"Error al eliminar socio: {str(e)}")
        finally:
            db.close()

    def get_acciones(self, socio_id: int):
        # Placeholder
        return []

    def get_historial_pagos(self, socio_id: int):
        # Placeholder
        return []

    def get_socio_by_usuario_id(self, usuario_id: int) -> Optional[Socio]:
        """Obtiene un socio por su ID de usuario"""
        db: Session = SessionLocal()
        try:
            result = db.execute(text("""
                SELECT id_socio, id_club, nombres, apellidos, ci_nit, telefono, correo_electronico, direccion, estado, fecha_de_registro, fecha_nacimiento, tipo_membresia, id_usuario 
                FROM socio 
                WHERE id_usuario = :usuario_id
            """), {"usuario_id": usuario_id}).fetchone()
            
            if result:
                fecha_registro = str(result[9]) if result[9] else None
                fecha_nacimiento = str(result[10]) if result[10] else None
                
                return Socio(
                    id_socio=result[0],
                    id_club=result[1],
                    nombres=result[2],
                    apellidos=result[3],
                    ci_nit=result[4],
                    telefono=result[5],
                    correo_electronico=result[6],
                    direccion=result[7],
                    estado=result[8],
                    fecha_de_registro=fecha_registro,
                    fecha_nacimiento=fecha_nacimiento,
                    tipo_membresia=result[11],
                    id_usuario=result[12]
                )
            return None
        except Exception as e:
            logging.error(f"Error en get_socio_by_usuario_id: {str(e)}")
            raise Exception(f"Error al consultar socio por usuario: {str(e)}")
        finally:
            db.close() 