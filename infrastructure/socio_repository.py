from domain.socio import Socio
from sqlalchemy.orm import Session
from sqlalchemy import text
from config import SessionLocal
from typing import Optional

class SocioRepository:
    def list_socios(self):
        db: Session = SessionLocal()
        try:
            result = db.execute(text("SELECT id_socio, id_club, nombres, apellidos, ci_nit, telefono, correo_electronico, direccion, estado, fecha_de_registro, fecha_nacimiento, tipo_membresia FROM socio")).fetchall()
            return [Socio(*row) for row in result]
        finally:
            db.close()

    def get_socio(self, socio_id: int) -> Optional[Socio]:
        db: Session = SessionLocal()
        try:
            result = db.execute(text("SELECT id_socio, id_club, nombres, apellidos, ci_nit, telefono, correo_electronico, direccion, estado, fecha_de_registro, fecha_nacimiento, tipo_membresia FROM socio WHERE id_socio = :id_socio"), {"id_socio": socio_id}).fetchone()
            if result:
                return Socio(*result)
            return None
        finally:
            db.close()

    def create_socio(self, data):
        db: Session = SessionLocal()
        try:
            result = db.execute(text('''
                INSERT INTO socio (id_club, nombres, apellidos, ci_nit, telefono, correo_electronico, direccion, estado, fecha_nacimiento, tipo_membresia)
                VALUES (:id_club, :nombres, :apellidos, :ci_nit, :telefono, :correo_electronico, :direccion, :estado, :fecha_nacimiento, :tipo_membresia)
                RETURNING id_socio, id_club, nombres, apellidos, ci_nit, telefono, correo_electronico, direccion, estado, fecha_de_registro, fecha_nacimiento, tipo_membresia
            '''), data.dict())
            db.commit()
            row = result.fetchone()
            return Socio(*row)
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
        finally:
            db.close()

    def delete_socio(self, socio_id: int):
        db: Session = SessionLocal()
        try:
            result = db.execute(text("DELETE FROM socio WHERE id_socio = :id_socio RETURNING id_socio"), {"id_socio": socio_id})
            db.commit()
            return result.rowcount > 0
        finally:
            db.close()

    def get_acciones(self, socio_id: int):
        # Placeholder
        return []

    def get_historial_pagos(self, socio_id: int):
        # Placeholder
        return [] 