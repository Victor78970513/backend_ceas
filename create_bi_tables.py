#!/usr/bin/env python3
"""
Script para crear tablas consolidadas para Business Intelligence
Esto implementa un ETL simplificado para análisis de datos
"""

import psycopg2
from config import DATABASE_URL
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_bi_tables():
    """Crea tablas consolidadas para BI"""
    
    # Queries para crear tablas BI
    tables = {
        # Tabla consolidada de socios activos
        "socios_activos": """
            CREATE TABLE IF NOT EXISTS socios_activos AS
            SELECT 
                s.id_socio,
                s.nombres,
                s.apellidos,
                CONCAT(s.nombres, ' ', s.apellidos) as nombre_completo,
                s.estado,
                s.fecha_de_registro,
                c.nombre_club,
                COUNT(a.id_accion) as total_acciones,
                COALESCE(SUM(COALESCE(a.saldo_pendiente, 0)), 0) as total_invertido,
                CASE 
                    WHEN s.estado = 1 THEN true
                    ELSE false
                END as es_activo,
                EXTRACT(YEAR FROM AGE(CURRENT_DATE, s.fecha_de_registro)) as antiguedad_anios
            FROM socio s
            LEFT JOIN club c ON s.id_club = c.id_club
            LEFT JOIN accion a ON s.id_socio = a.id_socio
            GROUP BY s.id_socio, s.nombres, s.apellidos, s.estado, s.fecha_de_registro, c.nombre_club
            ORDER BY s.fecha_de_registro DESC;
        """,
        
        # Tabla consolidada de finanzas mensuales
        "finanzas_resumen": """
            CREATE TABLE IF NOT EXISTS finanzas_resumen AS
            SELECT 
                EXTRACT(YEAR FROM mf.fecha) as anio,
                EXTRACT(MONTH FROM mf.fecha) as mes,
                DATE_TRUNC('month', mf.fecha) as fecha_mes,
                c.nombre_club,
                mf.tipo_movimiento,
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
                COUNT(*) as cantidad_movimientos,
                AVG(mf.monto) as monto_promedio
            FROM movimientofinanciero mf
            LEFT JOIN club c ON mf.id_club = c.id_club
            GROUP BY 
                EXTRACT(YEAR FROM mf.fecha),
                EXTRACT(MONTH FROM mf.fecha),
                DATE_TRUNC('month', mf.fecha),
                c.nombre_club,
                mf.tipo_movimiento,
                CASE
                    WHEN mf.descripcion ILIKE '%cuota%' THEN 'Cuotas'
                    WHEN mf.descripcion ILIKE '%donación%' THEN 'Donaciones'
                    WHEN mf.descripcion ILIKE '%evento%' THEN 'Eventos'
                    WHEN mf.descripcion ILIKE '%servicio%' THEN 'Servicios'
                    WHEN mf.descripcion ILIKE '%compra%' THEN 'Compras'
                    WHEN mf.descripcion ILIKE '%material%' THEN 'Materiales'
                    ELSE 'Otros'
                END
            ORDER BY anio DESC, mes DESC;
        """,
        
        # Tabla consolidada de acciones y pagos
        "acciones_pagos_resumen": """
            CREATE TABLE IF NOT EXISTS acciones_pagos_resumen AS
            SELECT 
                a.id_accion,
                a.id_socio,
                CONCAT(s.nombres, ' ', s.apellidos) as nombre_socio,
                c.nombre_club,
                a.tipo_accion,
                COALESCE(a.saldo_pendiente, 0) as precio_renovacion,
                mp.descripcion as modalidad_pago,
                mp.cantidad_cuotas,
                COUNT(pa.id_pago) as pagos_realizados,
                COALESCE(SUM(pa.monto), 0) as total_pagado,
                (COALESCE(a.saldo_pendiente, 0) - COALESCE(SUM(pa.monto), 0)) as saldo_pendiente,
                CASE 
                    WHEN COUNT(pa.id_pago) = 0 THEN 'SIN_PAGOS'
                    WHEN COUNT(pa.id_pago) = mp.cantidad_cuotas THEN 'COMPLETAMENTE_PAGADO'
                    ELSE 'PAGO_PARCIAL'
                END as estado_pago,
                CASE 
                    WHEN COALESCE(a.saldo_pendiente, 0) > 0 THEN
                        (COALESCE(SUM(pa.monto), 0) / COALESCE(a.saldo_pendiente, 1) * 100)
                    ELSE 0
                END as porcentaje_pagado,
                (mp.cantidad_cuotas - COUNT(pa.id_pago)) as pagos_restantes,
                a.fecha_emision_certificado,
                MAX(pa.fecha_de_pago) as ultimo_pago
            FROM accion a
            LEFT JOIN socio s ON a.id_socio = s.id_socio
            LEFT JOIN club c ON a.id_club = c.id_club
            LEFT JOIN modalidadpago mp ON a.modalidad_pago = mp.id_modalidad_pago
            LEFT JOIN pagoaccion pa ON a.id_accion = pa.id_accion
            GROUP BY 
                a.id_accion, a.id_socio, s.nombres, s.apellidos, c.nombre_club,
                a.tipo_accion, a.saldo_pendiente, mp.descripcion, mp.cantidad_cuotas,
                a.fecha_emision_certificado
            ORDER BY a.fecha_emision_certificado DESC;
        """,
        
        # Tabla consolidada de personal y asistencia
        "personal_asistencia_resumen": """
            CREATE TABLE IF NOT EXISTS personal_asistencia_resumen AS
            SELECT 
                p.id_personal,
                CONCAT(p.nombres, ' ', p.apellidos) as nombre_completo,
                p.departamento,
                c.nombre_cargo,
                p.fecha_ingreso,
                EXTRACT(YEAR FROM AGE(CURRENT_DATE, p.fecha_ingreso)) as antiguedad_anios,
                p.salario,
                p.estado,
                COUNT(a.id_asistencia) as total_asistencias,
                COUNT(CASE WHEN a.estado = 'PRESENTE' THEN 1 END) as asistencias_completas,
                COUNT(CASE WHEN a.estado = 'TARDANZA' THEN 1 END) as tardanzas,
                COUNT(CASE WHEN a.estado = 'AUSENTE' THEN 1 END) as ausencias,
                CASE 
                    WHEN COUNT(a.id_asistencia) > 0 THEN
                        (COUNT(CASE WHEN a.estado = 'PRESENTE' THEN 1 END)::float / 
                         COUNT(a.id_asistencia) * 100)
                    ELSE 0
                END as porcentaje_asistencia
            FROM personal p
            LEFT JOIN cargos c ON p.cargo = c.id_cargo
            LEFT JOIN asistencia a ON p.id_personal = a.id_personal
            GROUP BY 
                p.id_personal, p.nombres, p.apellidos, p.departamento,
                c.nombre_cargo, p.fecha_ingreso, p.salario, p.estado
            ORDER BY p.nombres, p.apellidos;
        """,
        
        # Tabla consolidada de métricas por club
        "metricas_club_resumen": """
            CREATE TABLE IF NOT EXISTS metricas_club_resumen AS
            SELECT 
                c.id_club,
                c.nombre_club,
                'Sin ubicación' as ubicacion,
                COUNT(DISTINCT s.id_socio) as total_socios,
                COUNT(DISTINCT CASE WHEN s.estado = 1 THEN s.id_socio END) as socios_activos,
                COUNT(DISTINCT CASE WHEN s.estado != 1 THEN s.id_socio END) as socios_inactivos,
                COUNT(DISTINCT a.id_accion) as total_acciones,
                COALESCE(SUM(COALESCE(a.saldo_pendiente, 0)), 0) as valor_total_acciones,
                COALESCE(
                    SUM(CASE WHEN mf.tipo_movimiento = 'INGRESO' THEN mf.monto ELSE 0 END), 0
                ) as ingresos_totales,
                COALESCE(
                    SUM(CASE WHEN mf.tipo_movimiento = 'EGRESO' THEN mf.monto ELSE 0 END), 0
                ) as egresos_totales,
                COALESCE(
                    SUM(CASE WHEN mf.tipo_movimiento = 'INGRESO' THEN mf.monto ELSE 0 END), 0
                ) - COALESCE(
                    SUM(CASE WHEN mf.tipo_movimiento = 'EGRESO' THEN mf.monto ELSE 0 END), 0
                ) as balance_neto,
                CASE 
                    WHEN COUNT(DISTINCT s.id_socio) > 0 THEN
                        (COUNT(DISTINCT CASE WHEN s.estado = 1 THEN s.id_socio END)::float / 
                         COUNT(DISTINCT s.id_socio) * 100)
                    ELSE 0
                END as tasa_retencion
            FROM club c
            LEFT JOIN socio s ON c.id_club = s.id_club
            LEFT JOIN accion a ON c.id_club = a.id_club
            LEFT JOIN movimientofinanciero mf ON c.id_club = mf.id_club
            GROUP BY c.id_club, c.nombre_club
            ORDER BY balance_neto DESC;
        """
    }
    
    try:
        # Conectar a la base de datos
        conn = psycopg2.connect(DATABASE_URL)
        cursor = conn.cursor()
        
        logger.info("🔧 Creando tablas consolidadas para BI...")
        
        # Crear cada tabla
        for table_name, query in tables.items():
            try:
                logger.info(f"📊 Creando tabla: {table_name}")
                cursor.execute(query)
                conn.commit()
                logger.info(f"✅ Tabla {table_name} creada exitosamente")
                
            except Exception as e:
                logger.error(f"❌ Error creando tabla {table_name}: {str(e)}")
                conn.rollback()
        
        # Crear índices para optimizar consultas
        logger.info("🔍 Creando índices para optimización...")
        
        indexes = [
            "CREATE INDEX IF NOT EXISTS idx_socios_activos_estado ON socios_activos(estado);",
            "CREATE INDEX IF NOT EXISTS idx_socios_activos_fecha ON socios_activos(fecha_de_registro);",
            "CREATE INDEX IF NOT EXISTS idx_finanzas_resumen_fecha ON finanzas_resumen(fecha_mes);",
            "CREATE INDEX IF NOT EXISTS idx_finanzas_resumen_club ON finanzas_resumen(nombre_club);",
            "CREATE INDEX IF NOT EXISTS idx_acciones_pagos_socio ON acciones_pagos_resumen(id_socio);",
            "CREATE INDEX IF NOT EXISTS idx_acciones_pagos_estado ON acciones_pagos_resumen(estado_pago);",
            "CREATE INDEX IF NOT EXISTS idx_personal_asistencia_depto ON personal_asistencia_resumen(departamento);",
            "CREATE INDEX IF NOT EXISTS idx_metricas_club_balance ON metricas_club_resumen(balance_neto);"
        ]
        
        for index_query in indexes:
            try:
                cursor.execute(index_query)
                conn.commit()
            except Exception as e:
                logger.warning(f"⚠️  Error creando índice: {str(e)}")
        
        logger.info("✅ Todas las tablas consolidadas creadas exitosamente")
        
        # Mostrar resumen de las tablas creadas
        cursor.execute("""
            SELECT table_name, 
                   (SELECT COUNT(*) FROM information_schema.columns WHERE table_name = t.table_name) as columnas
            FROM information_schema.tables t
            WHERE table_name IN ('socios_activos', 'finanzas_resumen', 'acciones_pagos_resumen', 
                                'personal_asistencia_resumen', 'metricas_club_resumen')
            AND table_schema = 'public'
            ORDER BY table_name;
        """)
        
        tables_info = cursor.fetchall()
        logger.info("\n📋 RESUMEN DE TABLAS CREADAS:")
        logger.info("=" * 50)
        
        for table_info in tables_info:
            logger.info(f"📊 {table_info[0]}: {table_info[1]} columnas")
        
        logger.info("=" * 50)
        
    except Exception as e:
        logger.error(f"❌ Error general: {str(e)}")
        raise
    finally:
        if 'conn' in locals():
            conn.close()

def refresh_bi_tables():
    """Actualiza las tablas consolidadas con datos frescos"""
    
    refresh_queries = {
        "socios_activos": "DROP TABLE IF EXISTS socios_activos;",
        "finanzas_resumen": "DROP TABLE IF EXISTS finanzas_resumen;",
        "acciones_pagos_resumen": "DROP TABLE IF EXISTS acciones_pagos_resumen;",
        "personal_asistencia_resumen": "DROP TABLE IF EXISTS personal_asistencia_resumen;",
        "metricas_club_resumen": "DROP TABLE IF EXISTS metricas_club_resumen;"
    }
    
    try:
        conn = psycopg2.connect(DATABASE_URL)
        cursor = conn.cursor()
        
        logger.info("🔄 Actualizando tablas consolidadas...")
        
        # Eliminar tablas existentes
        for table_name, drop_query in refresh_queries.items():
            cursor.execute(drop_query)
            logger.info(f"🗑️  Tabla {table_name} eliminada")
        
        conn.commit()
        
        # Recrear tablas
        create_bi_tables()
        
        logger.info("✅ Tablas consolidadas actualizadas exitosamente")
        
    except Exception as e:
        logger.error(f"❌ Error actualizando tablas: {str(e)}")
        raise
    finally:
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    print("🚀 CREANDO TABLAS CONSOLIDADAS PARA BUSINESS INTELLIGENCE")
    print("=" * 60)
    
    # Crear tablas iniciales
    create_bi_tables()
    
    print("\n💡 Para actualizar las tablas con datos frescos, ejecuta:")
    print("   python create_bi_tables.py --refresh")
    
    print("\n📚 Las siguientes tablas han sido creadas:")
    print("   • socios_activos - Resumen de socios y sus inversiones")
    print("   • finanzas_resumen - Resumen financiero mensual por club")
    print("   • acciones_pagos_resumen - Estado de pagos de acciones")
    print("   • personal_asistencia_resumen - Métricas de personal y asistencia")
    print("   • metricas_club_resumen - KPIs consolidados por club")
