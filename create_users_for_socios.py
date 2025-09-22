#!/usr/bin/env python3
"""
Script para crear usuarios para todos los socios existentes
Este script crea usuarios con contraseña por defecto para que los socios puedan hacer login
"""

import psycopg2
from config import DATABASE_URL
from infrastructure.security import hash_password
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def crear_usuarios_para_socios():
    """Crea usuarios para todos los socios que no tienen usuario asociado"""
    
    try:
        # Conectar a la base de datos
        conn = psycopg2.connect(DATABASE_URL)
        cursor = conn.cursor()
        
        logger.info("👥 Creando usuarios para socios existentes...")
        
        # Obtener socios sin usuario asociado
        cursor.execute("""
            SELECT id_socio, nombres, apellidos, ci_nit, correo_electronico, id_club
            FROM socio 
            WHERE id_usuario IS NULL
            ORDER BY id_socio
        """)
        
        socios_sin_usuario = cursor.fetchall()
        
        if not socios_sin_usuario:
            logger.info("✅ Todos los socios ya tienen usuarios asociados")
            return True
        
        logger.info(f"📋 Encontrados {len(socios_sin_usuario)} socios sin usuario")
        
        usuarios_creados = 0
        errores = 0
        
        for socio in socios_sin_usuario:
            try:
                socio_id, nombres, apellidos, ci_nit, correo, id_club = socio
                
                # Generar nombre de usuario único
                # Usar las primeras letras del nombre + apellido + ci
                nombre_parts = nombres.split()
                apellido_parts = apellidos.split()
                
                # Crear nombre de usuario: primera letra del nombre + primer apellido + últimos 3 dígitos del CI
                nombre_usuario = f"{nombre_parts[0][0].lower()}{apellido_parts[0].lower()}{ci_nit[-3:]}"
                
                # Verificar que el nombre de usuario no exista
                cursor.execute("SELECT id_usuario FROM usuario WHERE nombre_usuario = %s", (nombre_usuario,))
                if cursor.fetchone():
                    # Si existe, agregar el id del socio al final
                    nombre_usuario = f"{nombre_usuario}{socio_id}"
                
                # Contraseña por defecto para todos los socios
                password_plain = "123456"
                hashed_password = hash_password(password_plain)
                
                # Crear usuario
                cursor.execute("""
                    INSERT INTO usuario (
                        nombre_usuario, 
                        contrasena_hash, 
                        rol, 
                        estado, 
                        id_club, 
                        correo_electronico
                    ) VALUES (%s, %s, %s, %s, %s, %s)
                    RETURNING id_usuario
                """, (
                    nombre_usuario,
                    hashed_password,
                    4,  # Rol: usuario (socio)
                    'activo',
                    id_club,
                    correo
                ))
                
                user_id = cursor.fetchone()[0]
                
                # Actualizar el socio con el id_usuario
                cursor.execute("""
                    UPDATE socio 
                    SET id_usuario = %s 
                    WHERE id_socio = %s
                """, (user_id, socio_id))
                
                usuarios_creados += 1
                
                if usuarios_creados % 10 == 0:
                    logger.info(f"✅ {usuarios_creados}/{len(socios_sin_usuario)} usuarios creados...")
                
            except psycopg2.Error as e:
                errores += 1
                logger.warning(f"⚠️  Error creando usuario para socio {socio_id}: {e}")
                conn.rollback()
                continue
        
        # Confirmar transacciones
        conn.commit()
        
        logger.info(f"\n📊 RESUMEN DE CREACIÓN:")
        logger.info(f"✅ Usuarios creados exitosamente: {usuarios_creados}")
        logger.info(f"❌ Errores: {errores}")
        logger.info(f"📈 Total procesados: {usuarios_creados + errores}")
        
        # Verificar usuarios creados
        cursor.execute("SELECT COUNT(*) FROM usuario")
        total_usuarios = cursor.fetchone()[0]
        logger.info(f"📋 Total de usuarios en la base de datos: {total_usuarios}")
        
        # Mostrar algunos ejemplos de usuarios creados
        cursor.execute("""
            SELECT u.nombre_usuario, u.correo_electronico, s.nombres, s.apellidos, s.ci_nit
            FROM usuario u
            JOIN socio s ON u.id_usuario = s.id_usuario
            WHERE u.rol = 4
            ORDER BY u.id_usuario DESC
            LIMIT 5
        """)
        
        ejemplos = cursor.fetchall()
        
        logger.info(f"\n🔍 EJEMPLOS DE USUARIOS SOCIO CREADOS:")
        logger.info("=" * 80)
        for ejemplo in ejemplos:
            logger.info(f"👤 Usuario: {ejemplo[0]}")
            logger.info(f"   📧 Email: {ejemplo[1]}")
            logger.info(f"   👨 Nombre: {ejemplo[2]} {ejemplo[3]}")
            logger.info(f"   🆔 CI: {ejemplo[4]}")
            logger.info(f"   🔑 Contraseña: 123456")
            logger.info("-" * 80)
        
        # Estadísticas por rol
        cursor.execute("""
            SELECT r.nombre_rol, COUNT(*) as cantidad
            FROM usuario u
            JOIN roles r ON u.rol = r.id_rol
            GROUP BY r.nombre_rol, u.rol
            ORDER BY u.rol
        """)
        
        estadisticas = cursor.fetchall()
        
        logger.info(f"\n📈 DISTRIBUCIÓN POR ROL:")
        logger.info("=" * 30)
        for stat in estadisticas:
            logger.info(f"👥 {stat[0]}: {stat[1]} usuarios")
        
        cursor.close()
        conn.close()
        
        logger.info(f"\n🎉 ¡CREACIÓN DE USUARIOS COMPLETADA!")
        logger.info("=" * 60)
        logger.info("💡 Ahora todos los socios pueden hacer login")
        logger.info("🔑 Credenciales por defecto:")
        logger.info("   Usuario: [generado automáticamente]")
        logger.info("   Contraseña: 123456")
        logger.info("📧 Email: [el mismo del socio]")
        logger.info("=" * 60)
        logger.info("🌐 Para probar el login:")
        logger.info("   POST /login")
        logger.info("   Body: {\"correo_electronico\": \"socio@email.com\", \"contrasena\": \"123456\"}")
        logger.info("=" * 60)
        
        return True
        
    except psycopg2.Error as e:
        logger.error(f"❌ Error de base de datos: {e}")
        return False
    except Exception as e:
        logger.error(f"❌ Error general: {e}")
        return False

def mostrar_ejemplos_login():
    """Muestra ejemplos de cómo hacer login con los usuarios creados"""
    
    try:
        conn = psycopg2.connect(DATABASE_URL)
        cursor = conn.cursor()
        
        # Obtener algunos ejemplos de usuarios socio
        cursor.execute("""
            SELECT u.correo_electronico, u.nombre_usuario, s.nombres, s.apellidos
            FROM usuario u
            JOIN socio s ON u.id_usuario = s.id_usuario
            WHERE u.rol = 4
            LIMIT 3
        """)
        
        ejemplos = cursor.fetchall()
        
        logger.info(f"\n🧪 EJEMPLOS DE LOGIN:")
        logger.info("=" * 70)
        
        for i, ejemplo in enumerate(ejemplos, 1):
            logger.info(f"\n{i}. Login para {ejemplo[2]} {ejemplo[3]}:")
            logger.info(f"   POST http://127.0.0.1:8000/login")
            logger.info(f"   Body JSON:")
            logger.info(f"   {{")
            logger.info(f'     "correo_electronico": "{ejemplo[0]}",')
            logger.info(f'     "contrasena": "123456"')
            logger.info(f"   }}")
            logger.info(f"   Usuario: {ejemplo[1]}")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        logger.error(f"Error mostrando ejemplos: {e}")

def main():
    """Función principal"""
    print("🚀 CREANDO USUARIOS PARA SOCIOS EXISTENTES")
    print("=" * 70)
    
    if crear_usuarios_para_socios():
        print("\n✅ Usuarios para socios creados exitosamente")
        mostrar_ejemplos_login()
        print("\n🎯 Ahora todos los socios pueden hacer login")
    else:
        print("\n❌ Error creando usuarios para socios")
        import sys
        sys.exit(1)

if __name__ == "__main__":
    main()
