from domain.asistencia import Asistencia
from sqlalchemy.orm import Session
from sqlalchemy import text
from config import SessionLocal
from typing import Optional

class AsistenciaRepository:
    def list_asistencias(self):
        db: Session = SessionLocal()
        try:
            # Query con JOIN para obtener el nombre del empleado
            result = db.execute(text("""
                SELECT 
                    a.id_asistencia, 
                    a.id_personal, 
                    a.fecha, 
                    a.hora_ingreso, 
                    a.hora_salida, 
                    a.observaciones, 
                    a.estado,
                    CONCAT(p.nombres, ' ', p.apellidos) as nombre_empleado
                FROM asistencia a
                LEFT JOIN personal p ON a.id_personal = p.id_personal
                ORDER BY a.fecha DESC, a.hora_ingreso DESC
            """)).fetchall()
            
            asistencias = []
            for row in result:
                # Convertir tipos de datos de datetime a string, manejando None correctamente
                fecha = str(row[2]) if row[2] else "1900-01-01"
                hora_ingreso = str(row[3]) if row[3] else None
                hora_salida = str(row[4]) if row[4] else None
                
                asistencia = Asistencia(
                    id_asistencia=row[0],
                    id_personal=row[1],
                    fecha=fecha,
                    hora_ingreso=hora_ingreso,
                    hora_salida=hora_salida,
                    observaciones=row[5] if row[5] else None,
                    estado=row[6] if row[6] else None,
                    nombre_empleado=row[7] if row[7] else None
                )
                asistencias.append(asistencia)
            return asistencias
        finally:
            db.close()

    def get_asistencia_personal(self, id_personal: int):
        db: Session = SessionLocal()
        try:
            # Query con JOIN para obtener el nombre del empleado
            result = db.execute(text("""
                SELECT 
                    a.id_asistencia, 
                    a.id_personal, 
                    a.fecha, 
                    a.hora_ingreso, 
                    a.hora_salida, 
                    a.observaciones, 
                    a.estado,
                    CONCAT(p.nombres, ' ', p.apellidos) as nombre_empleado
                FROM asistencia a
                LEFT JOIN personal p ON a.id_personal = p.id_personal
                WHERE a.id_personal = :id_personal
                ORDER BY a.fecha DESC, a.hora_ingreso DESC
            """), {"id_personal": id_personal}).fetchall()
            
            asistencias = []
            for row in result:
                # Convertir tipos de datos de datetime a string, manejando None correctamente
                fecha = str(row[2]) if row[2] else "1900-01-01"
                hora_ingreso = str(row[3]) if row[3] else None
                hora_salida = str(row[4]) if row[4] else None
                
                asistencia = Asistencia(
                    id_asistencia=row[0],
                    id_personal=row[1],
                    fecha=fecha,
                    hora_ingreso=hora_ingreso,
                    hora_salida=hora_salida,
                    observaciones=row[5] if row[5] else None,
                    estado=row[6] if row[6] else None,
                    nombre_empleado=row[7] if row[7] else None
                )
                asistencias.append(asistencia)
            return asistencias
        finally:
            db.close()

    def create_asistencia(self, data):
        db: Session = SessionLocal()
        try:
            result = db.execute(text('''
                INSERT INTO asistencia (id_personal, fecha, hora_ingreso, hora_salida, observaciones, estado)
                VALUES (:id_personal, :fecha, :hora_ingreso, :hora_salida, :observaciones, :estado)
                RETURNING id_asistencia, id_personal, fecha, hora_ingreso, hora_salida, observaciones, estado
            '''), data.dict())
            db.commit()
            row = result.fetchone()
            
            # Obtener el nombre del empleado
            nombre_empleado = self._get_nombre_empleado(db, row[1])
            
            # Convertir tipos de datos de datetime a string, manejando None correctamente
            fecha = str(row[2]) if row[2] else "1900-01-01"
            hora_ingreso = str(row[3]) if row[3] else None
            hora_salida = str(row[4]) if row[4] else None
            
            return Asistencia(
                id_asistencia=row[0],
                id_personal=row[1],
                fecha=fecha,
                hora_ingreso=hora_ingreso,
                hora_salida=hora_salida,
                observaciones=row[5] if row[5] else None,
                estado=row[6] if row[6] else None,
                nombre_empleado=nombre_empleado
            )
        finally:
            db.close()

    def update_asistencia(self, asistencia_id: int, data):
        db: Session = SessionLocal()
        try:
            fields = []
            params = {"id_asistencia": asistencia_id}
            for field, value in data.dict(exclude_unset=True).items():
                fields.append(f"{field} = :{field}")
                params[field] = value
            if not fields:
                return None
            db.execute(text(f"UPDATE asistencia SET {', '.join(fields)} WHERE id_asistencia = :id_asistencia"), params)
            db.commit()
            result = db.execute(text("SELECT id_asistencia, id_personal, fecha, hora_ingreso, hora_salida, observaciones, estado FROM asistencia WHERE id_asistencia = :id_asistencia"), {"id_asistencia": asistencia_id}).fetchone()
            if result:
                # Obtener el nombre del empleado
                nombre_empleado = self._get_nombre_empleado(db, result[1])
                
                # Convertir tipos de datos de datetime a string, manejando None correctamente
                fecha = str(result[2]) if result[2] else "1900-01-01"
                hora_ingreso = str(result[3]) if result[3] else None
                hora_salida = str(result[4]) if result[4] else None
                
                return Asistencia(
                    id_asistencia=result[0],
                    id_personal=result[1],
                    fecha=fecha,
                    hora_ingreso=hora_ingreso,
                    hora_salida=hora_salida,
                    observaciones=result[5] if result[5] else None,
                    estado=result[6] if result[6] else None,
                    nombre_empleado=nombre_empleado
                )
            return None
        finally:
            db.close()
    
    def _get_nombre_empleado(self, db: Session, id_personal: int) -> Optional[str]:
        """Obtiene el nombre completo del empleado basado en el ID"""
        try:
            result = db.execute(text("""
                SELECT CONCAT(nombres, ' ', apellidos) as nombre_completo
                FROM personal WHERE id_personal = :id_personal
            """), {"id_personal": id_personal}).fetchone()
            
            if result:
                return result[0]
            return None
        except Exception as e:
            logging.error(f"Error al obtener nombre del empleado: {str(e)}")
            return None 