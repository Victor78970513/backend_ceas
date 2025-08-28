#!/usr/bin/env python3
"""
Script para verificar la estructura de la tabla club
"""

import psycopg2

# Configuración de la base de datos
DB_CONFIG = {
    'host': 'localhost',
    'database': 'ceas_bd',
    'user': 'wiscocho',
    'password': 'admin',
    'port': '5432'
}

def get_connection():
    """Obtiene conexión a la base de datos"""
    try:
        return psycopg2.connect(**DB_CONFIG)
    except Exception as e:
        print(f"❌ Error conectando a la BD: {e}")
        return None

def check_club_structure():
    """Verifica la estructura de la tabla club"""
    conn = get_connection()
    if not conn:
        return
    
    try:
        cursor = conn.cursor()
        
        # Verificar si la tabla existe
        cursor.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name = 'club'
            );
        """)
        
        if cursor.fetchone()[0]:
            print("✅ Tabla 'club' existe")
            
            # Obtener estructura de la tabla
            cursor.execute("""
                SELECT column_name, data_type, is_nullable, column_default
                FROM information_schema.columns 
                WHERE table_name = 'club'
                ORDER BY ordinal_position;
            """)
            
            columns = cursor.fetchall()
            print("\n📋 Estructura de la tabla 'club':")
            print("   Columna | Tipo | Nullable | Default")
            print("   --------|------|----------|---------")
            
            for col in columns:
                print(f"   {col[0]:<10} | {col[1]:<15} | {col[2]:<8} | {col[3] or 'NULL'}")
            
            # Verificar datos existentes
            cursor.execute("SELECT COUNT(*) FROM club")
            count = cursor.fetchone()[0]
            print(f"\n📊 Registros existentes: {count}")
            
            if count > 0:
                cursor.execute("SELECT * FROM club LIMIT 3")
                sample_data = cursor.fetchall()
                print("\n🔍 Muestra de datos:")
                for row in sample_data:
                    print(f"   {row}")
                    
        else:
            print("❌ Tabla 'club' no existe")
            
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    check_club_structure()

