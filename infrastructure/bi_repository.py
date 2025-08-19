from sqlalchemy.orm import Session
from sqlalchemy import text, func
from config import SessionLocal
from typing import Dict, List, Optional
from decimal import Decimal
import logging
from datetime import datetime

class BIRepository:
    def get_dashboard_financiero(self, mes: Optional[int] = None, anio: Optional[int] = None) -> Dict:
        """Obtiene métricas del dashboard financiero para un período específico"""
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
            
            # Métricas generales
            metricas_generales = self._get_metricas_generales(db, fecha_inicio, fecha_fin)
            
            # Distribución por club
            distribucion_club = self._get_distribucion_por_club(db, fecha_inicio, fecha_fin)
            
            # Top categorías
            top_categorias = self._get_top_categorias(db, fecha_inicio, fecha_fin)
            
            return {
                "periodo": periodo,
                "metricas_generales": metricas_generales,
                "distribucion_por_club": distribucion_club,
                "top_categorias": top_categorias
            }
            
        except Exception as e:
            logging.error(f"Error en get_dashboard_financiero: {str(e)}")
            raise Exception(f"Error al obtener dashboard financiero: {str(e)}")
        finally:
            db.close()
    
    def _get_metricas_generales(self, db: Session, fecha_inicio: str, fecha_fin: str) -> Dict:
        """Obtiene métricas generales del período"""
        try:
            result = db.execute(text("""
                SELECT 
                    COUNT(*) as total_movimientos,
                    SUM(CASE WHEN tipo_movimiento = 'INGRESO' THEN monto ELSE 0 END) as total_ingresos,
                    SUM(CASE WHEN tipo_movimiento = 'EGRESO' THEN monto ELSE 0 END) as total_egresos
                FROM movimientofinanciero 
                WHERE fecha >= :fecha_inicio AND fecha < :fecha_fin
            """), {"fecha_inicio": fecha_inicio, "fecha_fin": fecha_fin}).fetchone()
            
            ingresos = float(result[1]) if result[1] else 0.0
            egresos = float(result[2]) if result[2] else 0.0
            balance = ingresos - egresos
            
            return {
                "ingresos": Decimal(str(ingresos)),
                "egresos": Decimal(str(egresos)),
                "balance": Decimal(str(balance)),
                "movimientos": result[0] if result[0] else 0
            }
        except Exception as e:
            logging.error(f"Error en _get_metricas_generales: {str(e)}")
            return {"ingresos": Decimal("0"), "egresos": Decimal("0"), "balance": Decimal("0"), "movimientos": 0}
    
    def _get_distribucion_por_club(self, db: Session, fecha_inicio: str, fecha_fin: str) -> Dict:
        """Obtiene distribución de movimientos por club"""
        try:
            result = db.execute(text("""
                SELECT 
                    c.nombre_club,
                    SUM(CASE WHEN mf.tipo_movimiento = 'INGRESO' THEN mf.monto ELSE 0 END) as ingresos,
                    SUM(CASE WHEN mf.tipo_movimiento = 'EGRESO' THEN mf.monto ELSE 0 END) as egresos
                FROM movimientofinanciero mf
                LEFT JOIN club c ON mf.id_club = c.id_club
                WHERE mf.fecha >= :fecha_inicio AND mf.fecha < :fecha_fin
                GROUP BY c.id_club, c.nombre_club
                ORDER BY c.nombre_club
            """), {"fecha_inicio": fecha_inicio, "fecha_fin": fecha_fin}).fetchall()
            
            distribucion = {}
            for row in result:
                nombre_club = row[0] or "Club Sin Nombre"
                ingresos = float(row[1]) if row[1] else 0.0
                egresos = float(row[2]) if row[2] else 0.0
                balance = ingresos - egresos
                
                distribucion[nombre_club] = {
                    "ingresos": Decimal(str(ingresos)),
                    "egresos": Decimal(str(egresos)),
                    "balance": Decimal(str(balance))
                }
            
            return distribucion
        except Exception as e:
            logging.error(f"Error en _get_distribucion_por_club: {str(e)}")
            return {}
    
    def _get_top_categorias(self, db: Session, fecha_inicio: str, fecha_fin: str) -> Dict:
        """Obtiene top categorías por ingresos y egresos"""
        try:
            # Top categorías de ingresos
            top_ingresos = db.execute(text("""
                SELECT 
                    CASE 
                        WHEN mf.tipo_movimiento = 'INGRESO' AND mf.descripcion ILIKE '%cuota%' THEN 'Cuotas'
                        WHEN mf.tipo_movimiento = 'INGRESO' AND mf.descripcion ILIKE '%donación%' THEN 'Donaciones'
                        WHEN mf.tipo_movimiento = 'INGRESO' AND mf.descripcion ILIKE '%evento%' THEN 'Eventos'
                        ELSE 'Otros Ingresos'
                    END as categoria,
                    SUM(mf.monto) as monto
                FROM movimientofinanciero mf
                WHERE mf.fecha >= :fecha_inicio AND mf.fecha < :fecha_fin
                AND mf.tipo_movimiento = 'INGRESO'
                GROUP BY categoria
                ORDER BY monto DESC
                LIMIT 5
            """), {"fecha_inicio": fecha_inicio, "fecha_fin": fecha_fin}).fetchall()
            
            # Top categorías de egresos
            top_egresos = db.execute(text("""
                SELECT 
                    CASE 
                        WHEN mf.tipo_movimiento = 'EGRESO' AND mf.descripcion ILIKE '%servicio%' THEN 'Servicios'
                        WHEN mf.tipo_movimiento = 'EGRESO' AND mf.descripcion ILIKE '%compra%' THEN 'Compras'
                        WHEN mf.tipo_movimiento = 'EGRESO' AND mf.descripcion ILIKE '%material%' THEN 'Materiales'
                        ELSE 'Otros Egresos'
                    END as categoria,
                    SUM(mf.monto) as monto
                FROM movimientofinanciero mf
                WHERE mf.fecha >= :fecha_inicio AND mf.fecha < :fecha_fin
                AND mf.tipo_movimiento = 'EGRESO'
                GROUP BY categoria
                ORDER BY monto DESC
                LIMIT 5
            """), {"fecha_inicio": fecha_inicio, "fecha_fin": fecha_fin}).fetchall()
            
            # Formatear resultados
            ingresos_formateados = []
            for row in top_ingresos:
                ingresos_formateados.append({
                    "categoria": row[0],
                    "monto": Decimal(str(float(row[1]) if row[1] else 0.0))
                })
            
            egresos_formateados = []
            for row in top_egresos:
                egresos_formateados.append({
                    "categoria": row[0],
                    "monto": Decimal(str(float(row[1]) if row[1] else 0.0))
                })
            
            return {
                "ingresos": ingresos_formateados,
                "egresos": egresos_formateados
            }
        except Exception as e:
            logging.error(f"Error en _get_top_categorias: {str(e)}")
            return {"ingresos": [], "egresos": []}
