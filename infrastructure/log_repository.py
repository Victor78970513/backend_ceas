from domain.log import LogSistema
from sqlalchemy.orm import Session
from sqlalchemy import text
from config import SessionLocal
from typing import Optional

class LogRepository:
    def list_logs(self):
        db: Session = SessionLocal()
        try:
            result = db.execute(text("SELECT id_log, id_usuario, accion_realizada, fecha_y_hora, modulo_o_tabla_afectada, id_afectado, descripcion_detallada, ip_address, user_agent FROM logs_sistema ORDER BY fecha_y_hora DESC")).fetchall()
            logs = []
            for row in result:
                # Convertir datetime a string
                fecha_str = str(row[3]) if row[3] else None
                log_data = (row[0], row[1], row[2], fecha_str, row[4], row[5], row[6], row[7], row[8])
                logs.append(LogSistema(*log_data))
            return logs
        finally:
            db.close()

    def get_log(self, log_id: int) -> Optional[LogSistema]:
        db: Session = SessionLocal()
        try:
            result = db.execute(text("SELECT id_log, id_usuario, accion_realizada, fecha_y_hora, modulo_o_tabla_afectada, id_afectado, descripcion_detallada, ip_address, user_agent FROM logs_sistema WHERE id_log = :id_log"), {"id_log": log_id}).fetchone()
            if result:
                # Convertir datetime a string
                fecha_str = str(result[3]) if result[3] else None
                log_data = (result[0], result[1], result[2], fecha_str, result[4], result[5], result[6], result[7], result[8])
                return LogSistema(*log_data)
            return None
        finally:
            db.close()

    def create_log(self, data):
        db: Session = SessionLocal()
        try:
            result = db.execute(text('''
                INSERT INTO logs_sistema (id_usuario, accion_realizada, modulo_o_tabla_afectada, id_afectado, descripcion_detallada, ip_address, user_agent)
                VALUES (:id_usuario, :accion_realizada, :modulo_o_tabla_afectada, :id_afectado, :descripcion_detallada, :ip_address, :user_agent)
                RETURNING id_log, id_usuario, accion_realizada, fecha_y_hora, modulo_o_tabla_afectada, id_afectado, descripcion_detallada, ip_address, user_agent
            '''), data.dict())
            db.commit()
            row = result.fetchone()
            # Convertir datetime a string
            fecha_str = str(row[3]) if row[3] else None
            log_data = (row[0], row[1], row[2], fecha_str, row[4], row[5], row[6], row[7], row[8])
            return LogSistema(*log_data)
        except Exception as e:
            db.rollback()
            raise Exception(f"Error al crear log: {str(e)}")
        finally:
            db.close() 