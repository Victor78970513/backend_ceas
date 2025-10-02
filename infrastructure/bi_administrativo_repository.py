from sqlalchemy.orm import Session
from sqlalchemy import text, func
from config import SessionLocal
from typing import Dict, List, Optional
import logging
from datetime import datetime, date, timedelta
from decimal import Decimal

class BIAdministrativoRepository:
    def get_dashboard_completo(self, mes: Optional[int] = None, anio: Optional[int] = None, 
                              club: Optional[int] = None) -> Dict:
        """Obtiene dashboard completo administrativo y financiero"""
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

            # Métricas financieras
            metricas_financieras = self._get_metricas_financieras(db, fecha_inicio, fecha_fin, club)

            # Métricas administrativas
            metricas_administrativas = self._get_metricas_administrativas(db, fecha_inicio, fecha_fin, club)

            # Top clubes
            top_clubes = self._get_top_clubes(db, fecha_inicio, fecha_fin)

            # Top socios
            top_socios = self._get_top_socios(db, fecha_inicio, fecha_fin, club)

            # Distribución financiera
            distribucion_ingresos = self._get_distribucion_financiera(db, fecha_inicio, fecha_fin, "ingreso", club)
            distribucion_egresos = self._get_distribucion_financiera(db, fecha_inicio, fecha_fin, "egreso", club)

            # KPIs principales
            kpis_principales = self._get_kpis_principales(db, fecha_inicio, fecha_fin, club)

            # Tendencias mensuales
            tendencias = self._get_tendencias_mensuales(db, anio, club)

            # Alertas críticas
            alertas = self._get_alertas_criticas(db, fecha_inicio, fecha_fin, club)

            return {
                "periodo": periodo,
                "metricas_financieras": metricas_financieras,
                "metricas_administrativas": metricas_administrativas,
                "top_clubes": top_clubes,
                "top_socios": top_socios,
                "distribucion_ingresos": distribucion_ingresos,
                "distribucion_egresos": distribucion_egresos,
                "kpis_principales": kpis_principales,
                "tendencias_mensuales": tendencias,
                "alertas_criticas": alertas
            }

        except Exception as e:
            logging.error(f"Error en get_dashboard_completo: {str(e)}")
            raise Exception(f"Error al obtener dashboard administrativo-financiero: {str(e)}")
        finally:
            db.close()

    def _get_metricas_financieras(self, db: Session, fecha_inicio: str, fecha_fin: str, 
                                 club: Optional[int] = None) -> Dict:
        """Obtiene métricas financieras principales"""
        try:
            where_clause = "WHERE mf.fecha >= :fecha_inicio AND mf.fecha < :fecha_fin"
            params = {"fecha_inicio": fecha_inicio, "fecha_fin": fecha_fin}
            
            if club:
                where_clause += " AND mf.id_club = :club"
                params['club'] = club

            result = db.execute(text(f"""
                SELECT 
                    COALESCE(SUM(CASE WHEN mf.tipo_movimiento = 'INGRESO' THEN mf.monto ELSE 0 END), 0) as ingresos,
                    COALESCE(SUM(CASE WHEN mf.tipo_movimiento = 'EGRESO' THEN mf.monto ELSE 0 END), 0) as egresos,
                    COUNT(*) as total_movimientos
                FROM movimiento_financiero mf
                {where_clause}
            """), params).fetchone()

            ingresos = Decimal(str(result[0])) if result[0] else Decimal('0')
            egresos = Decimal(str(result[1])) if result[1] else Decimal('0')
            balance = ingresos - egresos
            margen = (balance / ingresos * 100) if ingresos > 0 else 0

            # Proyección basada en tendencia
            proyeccion = self._calcular_proyeccion_financiera(db, fecha_inicio, fecha_fin, club)

            return {
                "ingresos_totales": ingresos,
                "egresos_totales": egresos,
                "balance_neto": balance,
                "margen_rentabilidad": round(margen, 2),
                "flujo_caja": balance,
                "proyeccion_mensual": proyeccion
            }

        except Exception as e:
            logging.error(f"Error en _get_metricas_financieras: {str(e)}")
            return {
                "ingresos_totales": Decimal('0'),
                "egresos_totales": Decimal('0'),
                "balance_neto": Decimal('0'),
                "margen_rentabilidad": 0.0,
                "flujo_caja": Decimal('0'),
                "proyeccion_mensual": Decimal('0')
            }

    def _get_metricas_administrativas(self, db: Session, fecha_inicio: str, fecha_fin: str, 
                                     club: Optional[int] = None) -> Dict:
        """Obtiene métricas administrativas principales"""
        try:
            where_clause = "WHERE 1=1"
            params = {}
            
            if club:
                where_clause += " AND s.id_club = :club"
                params['club'] = club

            # Total socios
            result = db.execute(text(f"""
                SELECT 
                    COUNT(*) as total,
                    COUNT(CASE WHEN s.estado = 1 THEN 1 END) as activos,
                    COUNT(CASE WHEN s.estado != 1 THEN 1 END) as inactivos
                FROM socio s
                {where_clause}
            """), params).fetchone()

            total = result[0] or 0
            activos = result[1] or 0
            inactivos = result[2] or 0
            tasa_retencion = (activos / total * 100) if total > 0 else 0

            # Crecimiento mensual
            crecimiento = self._calcular_crecimiento_socios(db, fecha_inicio, fecha_fin, club)

            # Eficiencia operativa (acciones vendidas vs socios)
            eficiencia = self._calcular_eficiencia_operativa(db, fecha_inicio, fecha_fin, club)

            return {
                "total_socios": total,
                "socios_activos": activos,
                "socios_inactivos": inactivos,
                "tasa_retencion": round(tasa_retencion, 2),
                "crecimiento_mensual": round(crecimiento, 2),
                "eficiencia_operativa": round(eficiencia, 2)
            }

        except Exception as e:
            logging.error(f"Error en _get_metricas_administrativas: {str(e)}")
            return {
                "total_socios": 0,
                "socios_activos": 0,
                "socios_inactivos": 0,
                "tasa_retencion": 0.0,
                "crecimiento_mensual": 0.0,
                "eficiencia_operativa": 0.0
            }

    def _get_top_clubes(self, db: Session, fecha_inicio: str, fecha_fin: str) -> List[Dict]:
        """Obtiene top clubes por rendimiento"""
        try:
            result = db.execute(text("""
                SELECT 
                    c.id_club,
                    c.nombre_club,
                    COALESCE(SUM(CASE WHEN mf.tipo_movimiento = 'INGRESO' THEN mf.monto ELSE 0 END), 0) as ingresos,
                    COALESCE(SUM(CASE WHEN mf.tipo_movimiento = 'EGRESO' THEN mf.monto ELSE 0 END), 0) as egresos,
                    COUNT(DISTINCT s.id_socio) as socios_activos,
                    COUNT(DISTINCT a.id_accion) as acciones_vendidas
                FROM club c
                LEFT JOIN movimiento_financiero mf ON c.id_club = mf.id_club 
                    AND mf.fecha >= :fecha_inicio AND mf.fecha < :fecha_fin
                LEFT JOIN socio s ON c.id_club = s.id_club AND s.estado = 1
                LEFT JOIN accion a ON c.id_club = a.id_club
                GROUP BY c.id_club, c.nombre_club
                ORDER BY ingresos DESC
                LIMIT 10
            """), {"fecha_inicio": fecha_inicio, "fecha_fin": fecha_fin}).fetchall()

            clubes = []
            for row in result:
                ingresos = Decimal(str(row[2])) if row[2] else Decimal('0')
                egresos = Decimal(str(row[3])) if row[3] else Decimal('0')
                balance = ingresos - egresos
                rentabilidad = (balance / ingresos * 100) if ingresos > 0 else 0

                clubes.append({
                    "id_club": row[0],
                    "nombre_club": row[1],
                    "ingresos": ingresos,
                    "egresos": egresos,
                    "balance": balance,
                    "rentabilidad": round(rentabilidad, 2),
                    "socios_activos": row[4] or 0,
                    "acciones_vendidas": row[5] or 0
                })

            return clubes

        except Exception as e:
            logging.error(f"Error en _get_top_clubes: {str(e)}")
            return []

    def _get_top_socios(self, db: Session, fecha_inicio: str, fecha_fin: str, 
                        club: Optional[int] = None) -> List[Dict]:
        """Obtiene top socios por inversión"""
        try:
            where_clause = "WHERE a.id_accion IS NOT NULL"
            params = {"fecha_inicio": fecha_inicio, "fecha_fin": fecha_fin}
            
            if club:
                where_clause += " AND s.id_club = :club"
                params['club'] = club

            result = db.execute(text(f"""
                SELECT 
                    s.id_socio,
                    CONCAT(s.nombres, ' ', s.apellidos) as nombre_completo,
                    c.nombre_club,
                    COUNT(a.id_accion) as acciones_compradas,
                    COALESCE(SUM(COALESCE(a.saldo_pendiente, 0)), 0) as total_invertido,
                    CASE 
                        WHEN COUNT(a.id_accion) = 0 THEN 'SIN_ACCIONES'
                        WHEN COUNT(pa.id_pago) = 0 THEN 'SIN_PAGOS'
                        WHEN COUNT(pa.id_pago) = COUNT(a.id_accion) THEN 'COMPLETAMENTE_PAGADO'
                        ELSE 'PAGO_PARCIAL'
                    END as estado_pagos,
                    EXTRACT(MONTH FROM AGE(CURRENT_DATE, s.fecha_de_registro)) as antiguedad_meses
                FROM socio s
                LEFT JOIN club c ON s.id_club = c.id_club
                LEFT JOIN accion a ON s.id_socio = a.id_socio
                LEFT JOIN pago_accion pa ON a.id_accion = pa.id_accion
                {where_clause}
                GROUP BY s.id_socio, s.nombres, s.apellidos, c.nombre_club, s.fecha_de_registro
                ORDER BY total_invertido DESC
                LIMIT 10
            """), params).fetchall()

            socios = []
            for row in result:
                socios.append({
                    "id_socio": row[0],
                    "nombre_completo": row[1],
                    "club_principal": row[2] or "Sin club",
                    "acciones_compradas": row[3] or 0,
                    "total_invertido": Decimal(str(row[4])) if row[4] else Decimal('0'),
                    "estado_pagos": row[5],
                    "antiguedad_meses": int(row[6]) if row[6] else 0
                })

            return socios

        except Exception as e:
            logging.error(f"Error en _get_top_socios: {str(e)}")
            return []

    def _get_distribucion_financiera(self, db: Session, fecha_inicio: str, fecha_fin: str, 
                                    tipo_movimiento: str, club: Optional[int] = None) -> List[Dict]:
        """Obtiene distribución financiera por categorías"""
        try:
            where_clause = "WHERE mf.tipo_movimiento = :tipo AND mf.fecha >= :fecha_inicio AND mf.fecha < :fecha_fin"
            params = {"tipo": tipo_movimiento, "fecha_inicio": fecha_inicio, "fecha_fin": fecha_fin}
            
            if club:
                where_clause += " AND mf.id_club = :club"
                params['club'] = club

            result = db.execute(text(f"""
                SELECT 
                    CASE
                        WHEN mf.descripcion ILIKE '%cuota%' THEN 'Cuotas'
                        WHEN mf.descripcion ILIKE '%donación%' THEN 'Donaciones'
                        WHEN mf.descripcion ILIKE '%evento%' THEN 'Eventos'
                        WHEN mf.descripcion ILIKE '%servicio%' THEN 'Servicios'
                        WHEN mf.descripcion ILIKE '%compra%' THEN 'Compras'
                        WHEN mf.descripcion ILIKE '%material%' THEN 'Materiales'
                        ELSE 'Otros'
                    END as categoria,
                    SUM(mf.monto) as monto_total,
                    COUNT(*) as cantidad_movimientos
                FROM movimiento_financiero mf
                {where_clause}
                GROUP BY 
                    CASE
                        WHEN mf.descripcion ILIKE '%cuota%' THEN 'Cuotas'
                        WHEN mf.descripcion ILIKE '%donación%' THEN 'Donaciones'
                        WHEN mf.descripcion ILIKE '%evento%' THEN 'Eventos'
                        WHEN mf.descripcion ILIKE '%servicio%' THEN 'Servicios'
                        WHEN mf.descripcion ILIKE '%compra%' THEN 'Compras'
                        WHEN mf.descripcion ILIKE '%material%' THEN 'Materiales'
                        ELSE 'Otros'
                    END
                ORDER BY monto_total DESC
            """), params).fetchall()

            # Calcular total para porcentajes
            total = sum(Decimal(str(row[1])) for row in result if row[1])

            distribucion = []
            for row in result:
                monto = Decimal(str(row[1])) if row[1] else Decimal('0')
                porcentaje = (monto / total * 100) if total > 0 else 0
                tendencia = self._determinar_tendencia_categoria(db, row[0], fecha_inicio, fecha_fin, club)

                distribucion.append({
                    "categoria": row[0],
                    "monto": monto,
                    "porcentaje": round(porcentaje, 2),
                    "tendencia": tendencia
                })

            return distribucion

        except Exception as e:
            logging.error(f"Error en _get_distribucion_financiera: {str(e)}")
            return []

    def _get_kpis_principales(self, db: Session, fecha_inicio: str, fecha_fin: str, 
                              club: Optional[int] = None) -> List[Dict]:
        """Obtiene KPIs principales del negocio"""
        try:
            kpis = []
            
            # KPI 1: Tasa de conversión de socios
            tasa_conversion = self._calcular_tasa_conversion(db, fecha_inicio, fecha_fin, club)
            kpis.append({
                "nombre": "Tasa de Conversión de Socios",
                "valor_actual": tasa_conversion,
                "valor_anterior": tasa_conversion * 0.95,  # Simulado
                "cambio_porcentual": 5.0,
                "meta": 80.0,
                "estado": "excelente" if tasa_conversion >= 80 else "bueno" if tasa_conversion >= 60 else "regular"
            })

            # KPI 2: Rentabilidad por club
            rentabilidad_club = self._calcular_rentabilidad_club(db, fecha_inicio, fecha_fin, club)
            kpis.append({
                "nombre": "Rentabilidad por Club",
                "valor_actual": rentabilidad_club,
                "valor_anterior": rentabilidad_club * 0.98,
                "cambio_porcentual": 2.0,
                "meta": 25.0,
                "estado": "excelente" if rentabilidad_club >= 25 else "bueno" if rentabilidad_club >= 15 else "regular"
            })

            # KPI 3: Eficiencia operativa
            eficiencia = self._calcular_eficiencia_operativa(db, fecha_inicio, fecha_fin, club)
            kpis.append({
                "nombre": "Eficiencia Operativa",
                "valor_actual": eficiencia,
                "valor_anterior": eficiencia * 1.02,
                "cambio_porcentual": -2.0,
                "meta": 85.0,
                "estado": "excelente" if eficiencia >= 85 else "bueno" if eficiencia >= 70 else "regular"
            })

            return kpis

        except Exception as e:
            logging.error(f"Error en _get_kpis_principales: {str(e)}")
            return []

    def _get_tendencias_mensuales(self, db: Session, anio: int, club: Optional[int] = None) -> Dict:
        """Obtiene tendencias mensuales del año"""
        try:
            where_clause = "WHERE EXTRACT(YEAR FROM mf.fecha) = :anio"
            params = {"anio": anio}
            
            if club:
                where_clause += " AND mf.id_club = :club"
                params['club'] = club

            result = db.execute(text(f"""
                SELECT 
                    EXTRACT(MONTH FROM mf.fecha) as mes,
                    COALESCE(SUM(CASE WHEN mf.tipo_movimiento = 'INGRESO' THEN mf.monto ELSE 0 END), 0) as ingresos,
                    COALESCE(SUM(CASE WHEN mf.tipo_movimiento = 'EGRESO' THEN mf.monto ELSE 0 END), 0) as egresos,
                    COUNT(*) as movimientos
                FROM movimiento_financiero mf
                {where_clause}
                GROUP BY EXTRACT(MONTH FROM mf.fecha)
                ORDER BY mes
            """), params).fetchall()

            tendencias = {}
            for row in result:
                mes = int(row[0])
                ingresos = float(row[1]) if row[1] else 0
                egresos = float(row[2]) if row[2] else 0
                balance = ingresos - egresos

                tendencias[f"{mes:02d}"] = {
                    "periodo": f"{anio:04d}-{mes:02d}",
                    "valor": balance,
                    "cambio_anterior": balance * 0.95,  # Simulado
                    "proyeccion": balance * 1.05  # Simulado
                }

            return tendencias

        except Exception as e:
            logging.error(f"Error en _get_tendencias_mensuales: {str(e)}")
            return {}

    def _get_alertas_criticas(self, db: Session, fecha_inicio: str, fecha_fin: str, 
                              club: Optional[int] = None) -> List[str]:
        """Obtiene alertas críticas del sistema"""
        try:
            alertas = []
            
            # Alerta 1: Balance negativo
            balance = self._get_balance_periodo(db, fecha_inicio, fecha_fin, club)
            if balance < 0:
                alertas.append(f"⚠️ Balance negativo: ${abs(balance):,.2f} - Revisar gastos")

            # Alerta 2: Socios inactivos
            socios_inactivos = self._get_socios_inactivos(db, club)
            if socios_inactivos > 10:
                alertas.append(f"⚠️ {socios_inactivos} socios inactivos - Implementar estrategia de retención")

            # Alerta 3: Pagos pendientes
            pagos_pendientes = self._get_pagos_pendientes(db, fecha_inicio, fecha_fin, club)
            if pagos_pendientes > 5:
                alertas.append(f"⚠️ {pagos_pendientes} pagos pendientes - Seguimiento requerido")

            return alertas

        except Exception as e:
            logging.error(f"Error en _get_alertas_criticas: {str(e)}")
            return ["Error al obtener alertas"]

    # ===== MÉTODOS AUXILIARES =====
    def _calcular_proyeccion_financiera(self, db: Session, fecha_inicio: str, fecha_fin: str, 
                                       club: Optional[int] = None) -> Decimal:
        """Calcula proyección financiera basada en tendencias"""
        try:
            # Simulación simple basada en crecimiento histórico
            return Decimal('10000.00')  # Placeholder
        except Exception as e:
            logging.error(f"Error en _calcular_proyeccion_financiera: {str(e)}")
            return Decimal('0.00')

    def _calcular_crecimiento_socios(self, db: Session, fecha_inicio: str, fecha_fin: str, 
                                   club: Optional[int] = None) -> float:
        """Calcula crecimiento mensual de socios"""
        try:
            # Simulación simple
            return 5.2  # Placeholder
        except Exception as e:
            logging.error(f"Error en _calcular_crecimiento_socios: {str(e)}")
            return 0.0

    def _calcular_eficiencia_operativa(self, db: Session, fecha_inicio: str, fecha_fin: str, 
                                     club: Optional[int] = None) -> float:
        """Calcula eficiencia operativa"""
        try:
            # Simulación simple
            return 78.5  # Placeholder
        except Exception as e:
            logging.error(f"Error en _calcular_eficiencia_operativa: {str(e)}")
            return 0.0

    def _determinar_tendencia_categoria(self, db: Session, categoria: str, fecha_inicio: str, 
                                      fecha_fin: str, club: Optional[int] = None) -> str:
        """Determina tendencia de una categoría financiera"""
        try:
            # Simulación simple
            return "creciente"  # Placeholder
        except Exception as e:
            logging.error(f"Error en _determinar_tendencia_categoria: {str(e)}")
            return "estable"

    def _calcular_tasa_conversion(self, db: Session, fecha_inicio: str, fecha_fin: str, 
                                club: Optional[int] = None) -> float:
        """Calcula tasa de conversión de socios"""
        try:
            # Simulación simple
            return 82.3  # Placeholder
        except Exception as e:
            logging.error(f"Error en _calcular_tasa_conversion: {str(e)}")
            return 0.0

    def _calcular_rentabilidad_club(self, db: Session, fecha_inicio: str, fecha_fin: str, 
                                  club: Optional[int] = None) -> float:
        """Calcula rentabilidad por club"""
        try:
            # Simulación simple
            return 28.7  # Placeholder
        except Exception as e:
            logging.error(f"Error en _calcular_rentabilidad_club: {str(e)}")
            return 0.0

    def _get_balance_periodo(self, db: Session, fecha_inicio: str, fecha_fin: str, 
                            club: Optional[int] = None) -> Decimal:
        """Obtiene balance del período"""
        try:
            # Simulación simple
            return Decimal('5000.00')  # Placeholder
        except Exception as e:
            logging.error(f"Error en _get_balance_periodo: {str(e)}")
            return Decimal('0.00')

    def _get_socios_inactivos(self, db: Session, club: Optional[int] = None) -> int:
        """Obtiene número de socios inactivos"""
        try:
            # Simulación simple
            return 15  # Placeholder
        except Exception as e:
            logging.error(f"Error en _get_socios_inactivos: {str(e)}")
            return 0

    def _get_pagos_pendientes(self, db: Session, fecha_inicio: str, fecha_fin: str, 
                             club: Optional[int] = None) -> int:
        """Obtiene número de pagos pendientes"""
        try:
            # Simulación simple
            return 8  # Placeholder
        except Exception as e:
            logging.error(f"Error en _get_pagos_pendientes: {str(e)}")
            return 0

    def get_movimientos_financieros_detallados(self, dias: int = 90, club: Optional[int] = None) -> Dict:
        """Obtiene movimientos financieros detallados día a día para gráficas de alta resolución"""
        try:
            # Por ahora, retornar datos de ejemplo para probar
            # TODO: Implementar consulta real a la base de datos
            
            from datetime import datetime, timedelta
            import random
            
            # Generar fechas de ejemplo
            fecha_fin = datetime.now()
            fecha_inicio = fecha_fin - timedelta(days=dias)
            
            # Crear datos de ejemplo para los últimos días
            movimientos_diarios = []
            balance_acumulado = 0.0
            
            # Configurar semilla para reproducibilidad
            random.seed(42)
            
            for i in range(dias):
                fecha = fecha_inicio + timedelta(days=i)
                fecha_str = fecha.strftime('%Y-%m-%d')
                
                # Simular patrones financieros realistas
                dia_semana = fecha.weekday()  # 0=Lunes, 6=Domingo
                dia_mes = fecha.day
                es_fin_semana = dia_semana >= 5
                es_inicio_mes = dia_mes <= 5
                es_mitad_mes = 10 <= dia_mes <= 20
                es_fin_mes = dia_mes >= 25
                
                # BASE INGRESOS - Con variaciones realistas
                base_ingresos = 1200.0
                
                # Picos de ingresos (pagos de cuotas)
                if es_inicio_mes:
                    pico_cuotas = random.uniform(800, 1200)  # Pago de cuotas mensuales
                elif es_mitad_mes:
                    pico_cuotas = random.uniform(200, 400)   # Pagos parciales
                else:
                    pico_cuotas = random.uniform(50, 150)    # Pagos menores
                
                # Variación por día de semana
                if es_fin_semana:
                    variacion_semana = random.uniform(-200, 100)  # Menos actividad
                else:
                    variacion_semana = random.uniform(100, 300)   # Más actividad
                
                # Variación aleatoria natural
                variacion_aleatoria = random.uniform(-150, 150)
                
                # Calcular ingresos del día
                ingresos = base_ingresos + pico_cuotas + variacion_semana + variacion_aleatoria
                ingresos = max(ingresos, 100)  # Mínimo 100
                
                # BASE EGRESOS - Con variaciones realistas
                base_egresos = 900.0
                
                # Picos de gastos (compras, servicios)
                if es_fin_mes:
                    pico_gastos = random.uniform(600, 1000)  # Gastos mensuales
                elif es_mitad_mes:
                    pico_gastos = random.uniform(300, 600)   # Gastos parciales
                else:
                    pico_gastos = random.uniform(100, 300)   # Gastos menores
                
                # Variación por día de semana
                if es_fin_semana:
                    variacion_gastos = random.uniform(-100, 200)  # Gastos de ocio
                else:
                    variacion_gastos = random.uniform(200, 400)   # Gastos operativos
                
                # Variación aleatoria natural
                variacion_gastos_aleatoria = random.uniform(-100, 100)
                
                # Calcular egresos del día
                egresos = base_egresos + pico_gastos + variacion_gastos + variacion_gastos_aleatoria
                egresos = max(egresos, 200)  # Mínimo 200
                
                # Días sin movimientos (ocasionalmente)
                if random.random() < 0.05:  # 5% de probabilidad
                    ingresos = random.uniform(50, 150)
                    egresos = random.uniform(100, 200)
                
                # Calcular balance del día
                balance_dia = ingresos - egresos
                balance_acumulado += balance_dia
                
                # Número de movimientos realista
                if ingresos > 1500 or egresos > 1200:
                    total_movimientos = random.randint(5, 8)  # Día ocupado
                elif ingresos < 300 and egresos < 400:
                    total_movimientos = random.randint(1, 3)  # Día tranquilo
                else:
                    total_movimientos = random.randint(3, 6)  # Día normal
                
                movimientos_diarios.append({
                    "fecha": fecha_str,
                    "ingresos": round(ingresos, 2),
                    "egresos": round(egresos, 2),
                    "balance_dia": round(balance_dia, 2),
                    "balance_acumulado": round(balance_acumulado, 2),
                    "total_movimientos": total_movimientos
                })
            
            # Calcular estadísticas
            total_ingresos = sum(item["ingresos"] for item in movimientos_diarios)
            total_egresos = sum(item["egresos"] for item in movimientos_diarios)
            total_balance = total_ingresos - total_egresos
            
            # Calcular días con movimientos significativos
            dias_con_movimientos = len([item for item in movimientos_diarios if item["total_movimientos"] > 2])
            
            return {
                "periodo": {
                    "fecha_inicio": fecha_inicio.strftime('%Y-%m-%d'),
                    "fecha_fin": fecha_fin.strftime('%Y-%m-%d'),
                    "dias_analizados": dias,
                    "dias_con_movimientos": dias_con_movimientos
                },
                "resumen": {
                    "total_ingresos": round(total_ingresos, 2),
                    "total_egresos": round(total_egresos, 2),
                    "balance_total": round(total_balance, 2),
                    "promedio_ingresos_diario": round(total_ingresos / dias, 2),
                    "promedio_egresos_diario": round(total_egresos / dias, 2)
                },
                "movimientos_diarios": movimientos_diarios,
                "tendencias": {
                    "tendencia_ingresos": "variable",
                    "tendencia_egresos": "variable",
                    "volatilidad": round(random.uniform(20, 35), 1)
                }
            }
            
        except Exception as e:
            logging.error(f"Error en get_movimientos_financieros_detallados: {str(e)}")
            return {
                "error": f"Error al obtener movimientos financieros detallados: {str(e)}",
                "movimientos_diarios": []
            }

    def _calcular_volatilidad(self, movimientos: List[Dict]) -> float:
        """Calcula la volatilidad de los movimientos financieros"""
        try:
            if len(movimientos) < 2:
                return 0.0
            
            # Calcular desviación estándar de los balances diarios
            balances = [item["balance_dia"] for item in movimientos]
            media = sum(balances) / len(balances)
            varianza = sum((x - media) ** 2 for x in balances) / len(balances)
            desviacion = varianza ** 0.5
            
            # Normalizar por el rango de valores
            rango = max(balances) - min(balances) if max(balances) != min(balances) else 1
            return (desviacion / rango) * 100
            
        except Exception as e:
            logging.error(f"Error en _calcular_volatilidad: {str(e)}")
            return 0.0
