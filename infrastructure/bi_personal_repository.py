from sqlalchemy.orm import Session
from sqlalchemy import text, func
from config import SessionLocal
from typing import Dict, List, Optional
import logging
from datetime import datetime

class BIPersonalRepository:
    def get_dashboard_personal(self, mes: Optional[int] = None, anio: Optional[int] = None, 
                              departamento: Optional[str] = None, cargo: Optional[int] = None) -> Dict:
        """Obtiene métricas del dashboard de personal para un período específico"""
        db: Session = SessionLocal()
        try:
            # Determinar período
            if mes and anio:
                periodo = f"{anio:04d}-{mes:02d}"
                fecha_inicio = f"{anio:04d}-{mes:02d}-01"
                if mes == 12:
                    fecha_fin = f"{anio+1:04d}-01-01"
                else:
                    fecha_fin = f"{anio:04d}-{mes+1:02d}-01"
            else:
                # Período actual
                now = datetime.now()
                mes = now.month
                anio = now.year
                periodo = f"{anio:04d}-{mes:02d}"
                fecha_inicio = f"{anio:04d}-{mes:02d}-01"
                if mes == 12:
                    fecha_fin = f"{anio+1:04d}-01-01"
                else:
                    fecha_fin = f"{anio:04d}-{mes+1:02d}-01"

            # Métricas generales del personal
            metricas_generales = self._get_metricas_generales(db, departamento, cargo)

            # Métricas de asistencia
            metricas_asistencia = self._get_metricas_asistencia(db, fecha_inicio, fecha_fin, departamento, cargo)

            # Top empleados por asistencia
            top_empleados = self._get_top_empleados_asistencia(db, fecha_inicio, fecha_fin, departamento, cargo)

            # Asistencia por departamento
            asistencia_departamento = self._get_asistencia_por_departamento(db, fecha_inicio, fecha_fin)

            # Tendencias mensuales
            tendencias = self._get_tendencias_mensuales(db, anio, departamento, cargo)

            return {
                "periodo": periodo,
                "metricas_generales": metricas_generales,
                "metricas_asistencia": metricas_asistencia,
                "top_empleados_asistencia": top_empleados,
                "asistencia_por_departamento": asistencia_departamento,
                "tendencias_mensuales": tendencias
            }

        except Exception as e:
            logging.error(f"Error en get_dashboard_personal: {str(e)}")
            raise Exception(f"Error al obtener dashboard de personal: {str(e)}")
        finally:
            db.close()

    def _get_metricas_generales(self, db: Session, departamento: Optional[str] = None, 
                                cargo: Optional[int] = None) -> Dict:
        """Obtiene métricas generales del personal"""
        try:
            where_clause = "WHERE 1=1"
            params = {}
            
            if departamento:
                where_clause += " AND departamento = :departamento"
                params['departamento'] = departamento
            
            if cargo:
                where_clause += " AND cargo = :cargo"
                params['cargo'] = cargo

            # Total personal
            result = db.execute(text(f"""
                SELECT 
                    COUNT(*) as total,
                    COUNT(CASE WHEN estado = true THEN 1 END) as activos,
                    COUNT(CASE WHEN estado = false THEN 1 END) as inactivos
                FROM personal 
                {where_clause}
            """), params).fetchone()

            # Personal por departamento
            dept_result = db.execute(text(f"""
                SELECT 
                    COALESCE(departamento, 'Sin departamento') as dept,
                    COUNT(*) as total
                FROM personal 
                {where_clause}
                GROUP BY departamento
                ORDER BY total DESC
            """), params).fetchall()

            personal_por_departamento = {row[0]: row[1] for row in dept_result}

            # Personal por cargo
            cargo_result = db.execute(text(f"""
                SELECT 
                    c.nombre_cargo,
                    COUNT(p.id_personal) as total
                FROM personal p
                LEFT JOIN cargos c ON p.cargo = c.id_cargo
                {where_clause.replace('personal', 'p')}
                GROUP BY c.nombre_cargo
                ORDER BY total DESC
            """), params).fetchall()

            personal_por_cargo = {row[0] if row[0] else 'Sin cargo': row[1] for row in cargo_result}

            return {
                "total_personal": result[0],
                "personal_activo": result[1],
                "personal_inactivo": result[2],
                "personal_por_departamento": personal_por_departamento,
                "personal_por_cargo": personal_por_cargo
            }

        except Exception as e:
            logging.error(f"Error en _get_metricas_generales: {str(e)}")
            return {
                "total_personal": 0,
                "personal_activo": 0,
                "personal_inactivo": 0,
                "personal_por_departamento": {},
                "personal_por_cargo": {}
            }

    def _get_metricas_asistencia(self, db: Session, fecha_inicio: str, fecha_fin: str,
                                 departamento: Optional[str] = None, cargo: Optional[int] = None) -> Dict:
        """Obtiene métricas de asistencia"""
        try:
            where_clause = "WHERE a.fecha >= :fecha_inicio AND a.fecha < :fecha_fin"
            params = {"fecha_inicio": fecha_inicio, "fecha_fin": fecha_fin}
            
            if departamento:
                where_clause += " AND p.departamento = :departamento"
                params['departamento'] = departamento
            
            if cargo:
                where_clause += " AND p.cargo = :cargo"
                params['cargo'] = cargo

            result = db.execute(text(f"""
                SELECT 
                    COUNT(*) as total_registros,
                    COUNT(CASE WHEN a.estado = 'Presente' THEN 1 END) as asistencias_completas,
                    COUNT(CASE WHEN a.estado = 'Tardanza' THEN 1 END) as tardanzas,
                    COUNT(CASE WHEN a.estado = 'Ausente' THEN 1 END) as ausencias,
                    AVG(CASE 
                        WHEN a.hora_ingreso IS NOT NULL AND a.hora_salida IS NOT NULL 
                        THEN EXTRACT(EPOCH FROM (a.hora_salida::time - a.hora_ingreso::time))/3600
                        ELSE NULL 
                    END) as promedio_horas
                FROM asistencia a
                LEFT JOIN personal p ON a.id_personal = p.id_personal
                {where_clause}
            """), params).fetchone()

            total = result[0] or 0
            asistencias = result[1] or 0
            porcentaje = (asistencias / total * 100) if total > 0 else 0

            return {
                "total_registros": total,
                "asistencias_completas": asistencias,
                "tardanzas": result[2] or 0,
                "ausencias": result[3] or 0,
                "porcentaje_asistencia": round(porcentaje, 2),
                "promedio_horas_trabajadas": round(result[4], 2) if result[4] else None
            }

        except Exception as e:
            logging.error(f"Error en _get_metricas_asistencia: {str(e)}")
            return {
                "total_registros": 0,
                "asistencias_completas": 0,
                "tardanzas": 0,
                "ausencias": 0,
                "porcentaje_asistencia": 0.0,
                "promedio_horas_trabajadas": None
            }

    def _get_top_empleados_asistencia(self, db: Session, fecha_inicio: str, fecha_fin: str,
                                     departamento: Optional[str] = None, cargo: Optional[int] = None) -> List[Dict]:
        """Obtiene top empleados por asistencia"""
        try:
            where_clause = "WHERE a.fecha >= :fecha_inicio AND a.fecha < :fecha_fin"
            params = {"fecha_inicio": fecha_inicio, "fecha_fin": fecha_fin}
            
            if departamento:
                where_clause += " AND p.departamento = :departamento"
                params['departamento'] = departamento
            
            if cargo:
                where_clause += " AND p.cargo = :cargo"
                params['cargo'] = cargo

            result = db.execute(text(f"""
                SELECT 
                    p.id_personal,
                    CONCAT(p.nombres, ' ', p.apellidos) as nombre_empleado,
                    COUNT(*) as total_asistencias,
                    COUNT(CASE WHEN a.estado = 'Tardanza' THEN 1 END) as tardanzas,
                    COUNT(CASE WHEN a.estado = 'Ausente' THEN 1 END) as ausencias,
                    AVG(CASE 
                        WHEN a.hora_ingreso IS NOT NULL AND a.hora_salida IS NOT NULL 
                        THEN EXTRACT(EPOCH FROM (a.hora_salida::time - a.hora_ingreso::time))/3600
                        ELSE NULL 
                    END) as promedio_horas
                FROM asistencia a
                LEFT JOIN personal p ON a.id_personal = p.id_personal
                {where_clause}
                GROUP BY p.id_personal, p.nombres, p.apellidos
                ORDER BY total_asistencias DESC, tardanzas ASC
                LIMIT 10
            """), params).fetchall()

            empleados = []
            for row in result:
                total = row[2] or 0
                asistencias = total - (row[3] or 0) - (row[4] or 0)
                porcentaje = (asistencias / total * 100) if total > 0 else 0

                empleados.append({
                    "id_personal": row[0],
                    "nombre_empleado": row[1],
                    "total_asistencias": total,
                    "tardanzas": row[3] or 0,
                    "ausencias": row[4] or 0,
                    "porcentaje_asistencia": round(porcentaje, 2),
                    "promedio_horas_trabajadas": round(row[5], 2) if row[5] else None
                })

            return empleados

        except Exception as e:
            logging.error(f"Error en _get_top_empleados_asistencia: {str(e)}")
            return []

    def _get_asistencia_por_departamento(self, db: Session, fecha_inicio: str, fecha_fin: str) -> List[Dict]:
        """Obtiene asistencia agrupada por departamento"""
        try:
            result = db.execute(text("""
                SELECT 
                    COALESCE(p.departamento, 'Sin departamento') as departamento,
                    COUNT(DISTINCT p.id_personal) as total_empleados,
                    COUNT(*) as total_asistencias,
                    COUNT(CASE WHEN UPPER(a.estado) IN ('PRESENTE', 'HORAS_EXTRAS') THEN 1 END) as asistencias,
                    COUNT(CASE WHEN UPPER(a.estado) IN ('TARDANZA', 'RETRASO') THEN 1 END) as tardanzas,
                    COUNT(CASE WHEN UPPER(a.estado) IN ('FALTANDO', 'AUSENTE') THEN 1 END) as ausencias
                FROM asistencia a
                LEFT JOIN personal p ON a.id_personal = p.id_personal
                WHERE a.fecha >= :fecha_inicio AND a.fecha < :fecha_fin
                GROUP BY p.departamento
                ORDER BY total_empleados DESC
            """), {"fecha_inicio": fecha_inicio, "fecha_fin": fecha_fin}).fetchall()

            departamentos = []
            for row in result:
                total = row[2] or 0
                asistencias = row[3] or 0
                promedio = (asistencias / total * 100) if total > 0 else 0

                departamentos.append({
                    "departamento": row[0],
                    "total_empleados": row[1],
                    "promedio_asistencia": round(promedio, 2),
                    "total_tardanzas": row[4] or 0,
                    "total_ausencias": row[5] or 0
                })

            return departamentos

        except Exception as e:
            logging.error(f"Error en _get_asistencia_por_departamento: {str(e)}")
            return []

    def _get_tendencias_mensuales(self, db: Session, anio: int, departamento: Optional[str] = None, 
                                  cargo: Optional[int] = None) -> Dict:
        """Obtiene tendencias mensuales de asistencia"""
        try:
            where_clause = "WHERE EXTRACT(YEAR FROM a.fecha) = :anio"
            params = {"anio": anio}
            
            if departamento:
                where_clause += " AND p.departamento = :departamento"
                params['departamento'] = departamento
            
            if cargo:
                where_clause += " AND p.cargo = :cargo"
                params['cargo'] = cargo

            result = db.execute(text(f"""
                SELECT 
                    EXTRACT(MONTH FROM a.fecha) as mes,
                    COUNT(*) as total_registros,
                    COUNT(CASE WHEN UPPER(a.estado) IN ('PRESENTE', 'HORAS_EXTRAS') THEN 1 END) as asistencias,
                    COUNT(CASE WHEN UPPER(a.estado) IN ('TARDANZA', 'RETRASO') THEN 1 END) as tardanzas,
                    COUNT(CASE WHEN UPPER(a.estado) IN ('FALTANDO', 'AUSENTE') THEN 1 END) as ausencias
                FROM asistencia a
                LEFT JOIN personal p ON a.id_personal = p.id_personal
                {where_clause}
                GROUP BY EXTRACT(MONTH FROM a.fecha)
                ORDER BY mes
            """), params).fetchall()

            tendencias = {}
            for row in result:
                mes = int(row[0])
                total = row[1] or 0
                asistencias = row[2] or 0
                porcentaje = (asistencias / total * 100) if total > 0 else 0

                tendencias[f"{mes:02d}"] = {
                    "total_registros": total,
                    "asistencias": asistencias,
                    "tardanzas": row[3] or 0,
                    "ausencias": row[4] or 0,
                    "porcentaje_asistencia": round(porcentaje, 2)
                }

            return tendencias

        except Exception as e:
            logging.error(f"Error en _get_tendencias_mensuales: {str(e)}")
            return {}

