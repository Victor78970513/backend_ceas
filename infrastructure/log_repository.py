from domain.log import LogSistema
from sqlalchemy.orm import Session
from sqlalchemy import text
from config import SessionLocal
from typing import Optional

class LogRepository:
    def list_logs(self):
        db: Session = SessionLocal()
        try:
            result = db.execute(text("SELECT id_log, id_usuario, accion_realizada, fecha_y_hora, modulo_o_tabla_afectada, id_afectado, descripcion_detallada FROM logs_sistema")).fetchall()
            return [LogSistema(*row) for row in result]
        finally:
            db.close()

    def get_log(self, log_id: int) -> Optional[LogSistema]:
        db: Session = SessionLocal()
        try:
            result = db.execute(text("SELECT id_log, id_usuario, accion_realizada, fecha_y_hora, modulo_o_tabla_afectada, id_afectado, descripcion_detallada FROM logs_sistema WHERE id_log = :id_log"), {"id_log": log_id}).fetchone()
            if result:
                return LogSistema(*result)
            return None
        finally:
            db.close() 