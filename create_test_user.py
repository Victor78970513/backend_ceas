#!/usr/bin/env python3
"""
Script para crear un usuario de prueba en el sistema CEAS
Este script crea un usuario administrador para testing
"""

import psycopg2
from config import DATABASE_URL
from infrastructure.security import hash_password
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_test_user():
    """Crea un usuario de prueba en la base de datos"""
    
    # Datos del usuario de prueba
    user_data = {
        'nombre_usuario': 'admin',
        'correo_electronico': 'prueba@gmail.com',
        'password_plain': '123456',
        'rol': 1,  # ID del rol administrador
        'id_club': 1,  # ID del club por defecto
        'estado': 'activo'
    }
    
    try:
        # Conectar a la base de datos
        conn = psycopg2.connect(DATABASE_URL)
        cursor = conn.cursor()
        
        logger.info("🔐 Creando usuario de prueba...")
        
        # Verificar si el usuario ya existe
        cursor.execute(
            "SELECT id_usuario FROM usuario WHERE nombre_usuario = %s OR correo_electronico = %s",
            (user_data['nombre_usuario'], user_data['correo_electronico'])
        )
        
        existing_user = cursor.fetchone()
        
        if existing_user:
            logger.warning(f"⚠️  El usuario ya existe con ID: {existing_user[0]}")
            
            # Actualizar la contraseña del usuario existente
            hashed_password = hash_password(user_data['password_plain'])
            cursor.execute("""
                UPDATE usuario 
                SET contrasena_hash = %s, 
                    correo_electronico = %s,
                    fecha_actualizacion = NOW()
                WHERE id_usuario = %s
            """, (hashed_password, user_data['correo_electronico'], existing_user[0]))
            
            conn.commit()
            logger.info("✅ Contraseña del usuario existente actualizada")
            
        else:
            # Crear nuevo usuario
            hashed_password = hash_password(user_data['password_plain'])
            
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
                user_data['nombre_usuario'],
                hashed_password,
                user_data['rol'],
                user_data['estado'],
                user_data['id_club'],
                user_data['correo_electronico']
            ))
            
            user_id = cursor.fetchone()[0]
            conn.commit()
            
            logger.info(f"✅ Usuario creado exitosamente con ID: {user_id}")
        
        # Verificar que el usuario se creó/actualizó correctamente
        cursor.execute("""
            SELECT u.id_usuario, u.nombre_usuario, u.correo_electronico, 
                   r.nombre_rol, c.nombre_club, u.estado
            FROM usuario u
            LEFT JOIN roles r ON u.rol = r.id_rol
            LEFT JOIN club c ON u.id_club = c.id_club
            WHERE u.nombre_usuario = %s OR u.correo_electronico = %s
        """, (user_data['nombre_usuario'], user_data['correo_electronico']))
        
        user_info = cursor.fetchone()
        
        if user_info:
            logger.info("\n📋 INFORMACIÓN DEL USUARIO CREADO:")
            logger.info("=" * 50)
            logger.info(f"ID Usuario: {user_info[0]}")
            logger.info(f"Nombre: {user_info[1]}")
            logger.info(f"Correo: {user_info[2]}")
            logger.info(f"Rol: {user_info[3]}")
            logger.info(f"Club: {user_info[4]}")
            logger.info(f"Estado: {user_info[5]}")
            logger.info("=" * 50)
            
            logger.info("\n🔑 CREDENCIALES DE PRUEBA:")
            logger.info(f"Usuario: {user_data['nombre_usuario']}")
            logger.info(f"Correo: {user_data['correo_electronico']}")
            logger.info(f"Contraseña: {user_data['password_plain']}")
            logger.info("=" * 50)
            
            logger.info("\n🌐 PARA PROBAR EL LOGIN:")
            logger.info("POST http://127.0.0.1:8000/login")
            logger.info("Body JSON:")
            logger.info("{")
            logger.info(f'  "nombre_usuario": "{user_data["nombre_usuario"]}",')
            logger.info(f'  "contrasena": "{user_data["password_plain"]}"')
            logger.info("}")
            logger.info("=" * 50)
        
        cursor.close()
        conn.close()
        
        return True
        
    except psycopg2.Error as e:
        logger.error(f"❌ Error de base de datos: {e}")
        return False
    except Exception as e:
        logger.error(f"❌ Error general: {e}")
        return False

def test_login():
    """Prueba el login con las credenciales creadas"""
    try:
        from use_cases.login import LoginUseCase
        from infrastructure.user_repository import UserRepository
        from schemas.user import UserLoginRequest
        
        logger.info("\n🧪 PROBANDO LOGIN...")
        
        # Crear request de login
        login_request = UserLoginRequest(
            nombre_usuario="admin",
            contrasena="123456"
        )
        
        # Ejecutar login
        use_case = LoginUseCase(UserRepository())
        result = use_case.login(login_request)
        
        logger.info("✅ Login exitoso!")
        logger.info(f"Token generado: {result.access_token[:50]}...")
        logger.info(f"Usuario: {result.nombre_usuario}")
        logger.info(f"Rol: {result.rol}")
        logger.info(f"Club ID: {result.id_club}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Error en login: {e}")
        return False

def main():
    """Función principal"""
    print("🚀 CREANDO USUARIO DE PRUEBA PARA CEAS")
    print("=" * 60)
    
    # Crear usuario
    if create_test_user():
        print("\n✅ Usuario de prueba creado exitosamente")
        
        # Probar login
        if test_login():
            print("\n🎉 ¡Sistema completamente funcional!")
            print("=" * 60)
            print("💡 Puedes usar las siguientes credenciales:")
            print("   Usuario: admin")
            print("   Correo: prueba@gmail.com")
            print("   Contraseña: 123456")
            print("\n🌐 Accede a la documentación en:")
            print("   http://127.0.0.1:8000/docs")
        else:
            print("\n⚠️  Usuario creado pero hay problemas con el login")
    else:
        print("\n❌ Error creando usuario de prueba")
        sys.exit(1)

if __name__ == "__main__":
    import sys
    main()