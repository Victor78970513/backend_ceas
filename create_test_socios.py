#!/usr/bin/env python3
"""
Script para crear 50 socios de prueba con datos realistas
Este script genera socios con información variada para testing del frontend
"""

import psycopg2
from config import DATABASE_URL
import random
from datetime import datetime, timedelta
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Datos para generar socios realistas
NOMBRES = [
    "Carlos", "María", "José", "Ana", "Luis", "Carmen", "Antonio", "Isabel", "Manuel", "Pilar",
    "Francisco", "Dolores", "Juan", "Teresa", "Pedro", "Rosa", "Miguel", "Francisca", "Ángel", "Concepción",
    "Rafael", "Antonia", "Jesús", "Mercedes", "Alejandro", "Rosario", "Fernando", "Encarnación", "Joaquín", "Carmen",
    "Diego", "Josefa", "Sergio", "María", "Rubén", "Ana", "Víctor", "Isabel", "Iván", "Pilar",
    "Óscar", "Dolores", "Raúl", "Teresa", "Rubén", "Rosa", "Adrián", "Francisca", "Mario", "Concepción"
]

APELLIDOS = [
    "García", "Rodríguez", "González", "Fernández", "López", "Martínez", "Sánchez", "Pérez", "Gómez", "Martín",
    "Jiménez", "Ruiz", "Hernández", "Díaz", "Moreno", "Muñoz", "Álvarez", "Romero", "Alonso", "Gutiérrez",
    "Navarro", "Torres", "Domínguez", "Vázquez", "Ramos", "Gil", "Ramírez", "Serrano", "Blanco", "Suárez",
    "Molina", "Morales", "Ortega", "Delgado", "Castro", "Ortiz", "Rubio", "Marín", "Sanz", "Iglesias",
    "Medina", "Cortés", "Castillo", "Garrido", "Santos", "Guerrero", "Lozano", "Cantero", "Prieto", "Méndez"
]

TIPOS_MEMBRESIA = ["Básica", "Premium", "VIP", "Gold", "Platinum", "Elite"]
ESTADOS_SOCIO = [1, 2]  # 1 = activo, 2 = inactivo (con más probabilidad de activos)
CIUDADES = [
    "La Paz", "Santa Cruz", "Cochabamba", "Sucre", "Oruro", "Potosí", "Tarija", "Trinidad", "Cobija", "Riberalta"
]

DIRECCIONES = [
    "Av. 16 de Julio", "Calle Comercio", "Av. 6 de Agosto", "Calle Potosí", "Av. Mariscal Santa Cruz",
    "Calle Linares", "Av. Ballivián", "Calle Sagárnaga", "Av. Montes", "Calle Jaén",
    "Av. Arce", "Calle Murillo", "Av. Camacho", "Calle Ayacucho", "Av. Villazón",
    "Calle Sucre", "Av. Perú", "Calle Yanacocha", "Av. Pando", "Calle Tarapacá"
]

def generar_telefono():
    """Genera un número de teléfono boliviano realista"""
    prefijos = ["2", "3", "4", "7"]
    prefijo = random.choice(prefijos)
    numero = ''.join([str(random.randint(0, 9)) for _ in range(7)])
    return f"{prefijo}{numero}"

def generar_ci_nit():
    """Genera un CI/NIT boliviano realista"""
    ci = ''.join([str(random.randint(0, 9)) for _ in range(7)])
    return ci

def generar_fecha_nacimiento():
    """Genera una fecha de nacimiento entre 18 y 65 años"""
    edad = random.randint(18, 65)
    fecha_base = datetime.now() - timedelta(days=edad * 365)
    # Agregar variación de días
    variacion = random.randint(-30, 30)
    fecha = fecha_base + timedelta(days=variacion)
    return fecha.strftime("%Y-%m-%d")

def generar_direccion():
    """Genera una dirección realista"""
    direccion = random.choice(DIRECCIONES)
    numero = random.randint(1, 9999)
    zona = random.choice(["Zona Centro", "Zona Norte", "Zona Sur", "Zona Este", "Zona Oeste", "Zona Sur", "Zona Central"])
    return f"{direccion} {numero}, {zona}"

def crear_socios_prueba():
    """Crea 50 socios de prueba con datos realistas"""
    
    try:
        # Conectar a la base de datos
        conn = psycopg2.connect(DATABASE_URL)
        cursor = conn.cursor()
        
        logger.info("👥 Creando 50 socios de prueba...")
        
        socios_creados = 0
        errores = 0
        
        for i in range(50):
            try:
                # Generar datos únicos para cada socio
                nombre = random.choice(NOMBRES)
                apellido = random.choice(APELLIDOS)
                segundo_apellido = random.choice(APELLIDOS)
                
                # Evitar apellidos duplicados
                while segundo_apellido == apellido:
                    segundo_apellido = random.choice(APELLIDOS)
                
                nombres_completos = f"{nombre} {apellido} {segundo_apellido}"
                apellidos_completos = f"{apellido} {segundo_apellido}"
                
                ci_nit = generar_ci_nit()
                telefono = generar_telefono()
                correo = f"{nombre.lower()}.{apellido.lower()}{i+1}@gmail.com"
                direccion = generar_direccion()
                estado = random.choices(ESTADOS_SOCIO, weights=[80, 20])[0]  # 80% activos, 20% inactivos
                tipo_membresia = random.choice(TIPOS_MEMBRESIA)
                fecha_nacimiento = generar_fecha_nacimiento()
                
                # Insertar socio
                cursor.execute("""
                    INSERT INTO socio (
                        id_club, nombres, apellidos, ci_nit, telefono, 
                        correo_electronico, direccion, estado, fecha_nacimiento, 
                        tipo_membresia
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    RETURNING id_socio
                """, (
                    1,  # id_club (Club por defecto)
                    nombres_completos,
                    apellidos_completos,
                    ci_nit,
                    telefono,
                    correo,
                    direccion,
                    estado,
                    fecha_nacimiento,
                    tipo_membresia
                ))
                
                socio_id = cursor.fetchone()[0]
                socios_creados += 1
                
                if socios_creados % 10 == 0:
                    logger.info(f"✅ {socios_creados}/50 socios creados...")
                
            except psycopg2.Error as e:
                errores += 1
                logger.warning(f"⚠️  Error creando socio {i+1}: {e}")
                conn.rollback()
                continue
        
        # Confirmar transacciones
        conn.commit()
        
        logger.info(f"\n📊 RESUMEN DE CREACIÓN:")
        logger.info(f"✅ Socios creados exitosamente: {socios_creados}")
        logger.info(f"❌ Errores: {errores}")
        logger.info(f"📈 Total procesados: {socios_creados + errores}")
        
        # Verificar socios creados
        cursor.execute("SELECT COUNT(*) FROM socio")
        total_socios = cursor.fetchone()[0]
        logger.info(f"📋 Total de socios en la base de datos: {total_socios}")
        
        # Mostrar algunos ejemplos
        cursor.execute("""
            SELECT nombres, apellidos, ci_nit, telefono, correo_electronico, tipo_membresia, estado
            FROM socio 
            ORDER BY id_socio DESC 
            LIMIT 5
        """)
        
        ejemplos = cursor.fetchall()
        
        logger.info(f"\n🔍 EJEMPLOS DE SOCIOS CREADOS:")
        logger.info("=" * 80)
        for ejemplo in ejemplos:
            estado_texto = "Activo" if ejemplo[6] == 1 else "Inactivo"
            logger.info(f"👤 {ejemplo[0]} {ejemplo[1]} | CI: {ejemplo[2]} | Tel: {ejemplo[3]}")
            logger.info(f"   📧 {ejemplo[4]} | Membresía: {ejemplo[5]} | Estado: {estado_texto}")
            logger.info("-" * 80)
        
        # Estadísticas por tipo de membresía
        cursor.execute("""
            SELECT tipo_membresia, COUNT(*) as cantidad
            FROM socio 
            GROUP BY tipo_membresia
            ORDER BY cantidad DESC
        """)
        
        estadisticas = cursor.fetchall()
        
        logger.info(f"\n📈 DISTRIBUCIÓN POR TIPO DE MEMBRESÍA:")
        logger.info("=" * 40)
        for stat in estadisticas:
            logger.info(f"🏆 {stat[0]}: {stat[1]} socios")
        
        # Estadísticas por estado
        cursor.execute("""
            SELECT 
                CASE WHEN estado = 1 THEN 'Activo' ELSE 'Inactivo' END as estado_texto,
                COUNT(*) as cantidad
            FROM socio 
            GROUP BY estado
            ORDER BY estado
        """)
        
        estados = cursor.fetchall()
        
        logger.info(f"\n📊 DISTRIBUCIÓN POR ESTADO:")
        logger.info("=" * 30)
        for estado in estados:
            logger.info(f"🔵 {estado[0]}: {estado[1]} socios")
        
        cursor.close()
        conn.close()
        
        logger.info(f"\n🎉 ¡CREACIÓN DE SOCIOS COMPLETADA!")
        logger.info("=" * 50)
        logger.info("💡 Los socios están listos para usar en tu frontend")
        logger.info("🌐 Puedes probar los endpoints:")
        logger.info("   GET /socios/ - Ver todos los socios")
        logger.info("   GET /socios/{id} - Ver socio específico")
        logger.info("   POST /socios/ - Crear nuevo socio")
        logger.info("=" * 50)
        
        return True
        
    except psycopg2.Error as e:
        logger.error(f"❌ Error de base de datos: {e}")
        return False
    except Exception as e:
        logger.error(f"❌ Error general: {e}")
        return False

def main():
    """Función principal"""
    print("🚀 CREANDO 50 SOCIOS DE PRUEBA PARA FRONTEND")
    print("=" * 70)
    
    if crear_socios_prueba():
        print("\n✅ Socios de prueba creados exitosamente")
        print("🎯 Perfectos para testing del frontend")
    else:
        print("\n❌ Error creando socios de prueba")
        import sys
        sys.exit(1)

if __name__ == "__main__":
    main()
