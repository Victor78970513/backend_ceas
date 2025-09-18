#!/usr/bin/env python3
"""
Script para configurar y crear la base de datos CEAS completa
Este script automatiza la creación de la base de datos PostgreSQL
"""

import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
import os
import sys
from pathlib import Path

# Configuración de la base de datos
DB_CONFIG = {
    'host': 'localhost',
    'port': '5432',
    'user': 'wiscocho',
    'password': 'admin',
    'database': 'ceas_bd'
}

def create_database():
    """Crea la base de datos si no existe"""
    try:
        # Conectar a PostgreSQL sin especificar base de datos
        conn = psycopg2.connect(
            host=DB_CONFIG['host'],
            port=DB_CONFIG['port'],
            user=DB_CONFIG['user'],
            password=DB_CONFIG['password'],
            database='postgres'  # Conectar a la BD por defecto
        )
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()
        
        # Verificar si la base de datos existe
        cursor.execute(
            "SELECT 1 FROM pg_database WHERE datname = %s",
            (DB_CONFIG['database'],)
        )
        
        if cursor.fetchone():
            print(f"✅ La base de datos '{DB_CONFIG['database']}' ya existe")
        else:
            # Crear la base de datos
            cursor.execute(f"CREATE DATABASE {DB_CONFIG['database']}")
            print(f"✅ Base de datos '{DB_CONFIG['database']}' creada exitosamente")
        
        cursor.close()
        conn.close()
        
    except psycopg2.Error as e:
        print(f"❌ Error creando la base de datos: {e}")
        return False
    
    return True

def execute_sql_file(file_path):
    """Ejecuta un archivo SQL"""
    try:
        # Conectar a la base de datos CEAS
        conn = psycopg2.connect(
            host=DB_CONFIG['host'],
            port=DB_CONFIG['port'],
            user=DB_CONFIG['user'],
            password=DB_CONFIG['password'],
            database=DB_CONFIG['database']
        )
        cursor = conn.cursor()
        
        # Leer y ejecutar el archivo SQL
        with open(file_path, 'r', encoding='utf-8') as file:
            sql_content = file.read()
            
        print(f"📄 Ejecutando archivo: {file_path}")
        
        # Ejecutar el SQL
        cursor.execute(sql_content)
        conn.commit()
        
        print(f"✅ Archivo SQL ejecutado exitosamente")
        
        cursor.close()
        conn.close()
        
        return True
        
    except psycopg2.Error as e:
        print(f"❌ Error ejecutando archivo SQL: {e}")
        return False
    except FileNotFoundError:
        print(f"❌ Archivo no encontrado: {file_path}")
        return False

def check_postgresql_connection():
    """Verifica la conexión a PostgreSQL"""
    try:
        conn = psycopg2.connect(
            host=DB_CONFIG['host'],
            port=DB_CONFIG['port'],
            user=DB_CONFIG['user'],
            password=DB_CONFIG['password'],
            database='postgres'
        )
        conn.close()
        print("✅ Conexión a PostgreSQL exitosa")
        return True
    except psycopg2.Error as e:
        print(f"❌ Error conectando a PostgreSQL: {e}")
        print("💡 Asegúrate de que PostgreSQL esté ejecutándose y las credenciales sean correctas")
        return False

def verify_database_structure():
    """Verifica que la estructura de la base de datos esté correcta"""
    try:
        conn = psycopg2.connect(
            host=DB_CONFIG['host'],
            port=DB_CONFIG['port'],
            user=DB_CONFIG['user'],
            password=DB_CONFIG['password'],
            database=DB_CONFIG['database']
        )
        cursor = conn.cursor()
        
        # Verificar tablas principales
        expected_tables = [
            'club', 'roles', 'usuario', 'socio', 'accion', 'pago_accion',
            'personal', 'asistencia', 'movimiento_financiero', 'logs_sistema',
            'inventario', 'eventos', 'reservas', 'proveedores', 'compras', 'facturacion'
        ]
        
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
            ORDER BY table_name
        """)
        
        existing_tables = [row[0] for row in cursor.fetchall()]
        
        print("\n📋 VERIFICACIÓN DE TABLAS:")
        print("=" * 50)
        
        all_tables_exist = True
        for table in expected_tables:
            if table in existing_tables:
                print(f"✅ {table}")
            else:
                print(f"❌ {table} - FALTANTE")
                all_tables_exist = False
        
        print("=" * 50)
        
        if all_tables_exist:
            print("✅ Todas las tablas están presentes")
        else:
            print("⚠️  Algunas tablas faltan")
        
        # Verificar datos iniciales
        cursor.execute("SELECT COUNT(*) FROM club")
        club_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM roles")
        roles_count = cursor.fetchone()[0]
        
        print(f"\n📊 DATOS INICIALES:")
        print(f"   Clubes: {club_count}")
        print(f"   Roles: {roles_count}")
        
        cursor.close()
        conn.close()
        
        return all_tables_exist
        
    except psycopg2.Error as e:
        print(f"❌ Error verificando estructura: {e}")
        return False

def main():
    """Función principal"""
    print("🚀 CONFIGURACIÓN DE BASE DE DATOS CEAS")
    print("=" * 60)
    
    # Paso 1: Verificar conexión a PostgreSQL
    print("\n1️⃣ Verificando conexión a PostgreSQL...")
    if not check_postgresql_connection():
        print("❌ No se puede continuar sin conexión a PostgreSQL")
        sys.exit(1)
    
    # Paso 2: Crear base de datos
    print("\n2️⃣ Creando base de datos...")
    if not create_database():
        print("❌ Error creando la base de datos")
        sys.exit(1)
    
    # Paso 3: Ejecutar script de creación
    print("\n3️⃣ Creando estructura de tablas...")
    sql_file = Path(__file__).parent / "create_database_complete.sql"
    
    if not execute_sql_file(sql_file):
        print("❌ Error ejecutando script de creación")
        sys.exit(1)
    
    # Paso 4: Verificar estructura
    print("\n4️⃣ Verificando estructura creada...")
    if not verify_database_structure():
        print("⚠️  La estructura no está completa")
        sys.exit(1)
    
    # Paso 5: Crear tablas BI si existe el script
    bi_script = Path(__file__).parent / "create_bi_tables.py"
    if bi_script.exists():
        print("\n5️⃣ Creando tablas de Business Intelligence...")
        try:
            import subprocess
            result = subprocess.run([sys.executable, str(bi_script)], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                print("✅ Tablas BI creadas exitosamente")
            else:
                print(f"⚠️  Error creando tablas BI: {result.stderr}")
        except Exception as e:
            print(f"⚠️  Error ejecutando script BI: {e}")
    
    print("\n🎉 ¡CONFIGURACIÓN COMPLETADA EXITOSAMENTE!")
    print("=" * 60)
    print("✅ Base de datos CEAS configurada y lista para usar")
    print("✅ Todas las tablas y datos iniciales creados")
    print("✅ El backend puede conectarse a la base de datos")
    print("\n💡 Para probar la conexión, ejecuta:")
    print("   python check_tables.py")

if __name__ == "__main__":
    main()
