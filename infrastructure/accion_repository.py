from domain.accion import Accion
from sqlalchemy.orm import Session
from sqlalchemy import text
from config import SessionLocal
from typing import Optional

class AccionRepository:
    def list_acciones(self):
        db: Session = SessionLocal()
        try:
            result = db.execute(text("SELECT id_accion, id_club, id_socio, modalidad_pago, estado_accion, certificado_pdf, certificado_cifrado, fecha_emision_certificado, saldo_pendiente, tipo_accion FROM accion")).fetchall()
            return [Accion(*row) for row in result]
        finally:
            db.close()

    def get_accion(self, accion_id: int) -> Optional[Accion]:
        db: Session = SessionLocal()
        try:
            result = db.execute(text("SELECT id_accion, id_club, id_socio, modalidad_pago, estado_accion, certificado_pdf, certificado_cifrado, fecha_emision_certificado, saldo_pendiente, tipo_accion FROM accion WHERE id_accion = :id_accion"), {"id_accion": accion_id}).fetchone()
            if result:
                return Accion(*result)
            return None
        finally:
            db.close()

    def create_accion(self, data):
        db: Session = SessionLocal()
        try:
            result = db.execute(text('''
                INSERT INTO accion (id_club, id_socio, modalidad_pago, estado_accion, certificado_pdf, certificado_cifrado, saldo_pendiente, tipo_accion)
                VALUES (:id_club, :id_socio, :modalidad_pago, :estado_accion, :certificado_pdf, :certificado_cifrado, :saldo_pendiente, :tipo_accion)
                RETURNING id_accion, id_club, id_socio, modalidad_pago, estado_accion, certificado_pdf, certificado_cifrado, fecha_emision_certificado, saldo_pendiente, tipo_accion
            '''), data.dict())
            db.commit()
            row = result.fetchone()
            return Accion(*row)
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
        # Placeholder
        return [] 