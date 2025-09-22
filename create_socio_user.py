#!/usr/bin/env python3
"""
Script para crear un usuario socio de prueba
Este script crea un usuario con rol de socio y su perfil correspondiente
"""

import psycopg2
from config import DATABASE_URL
from infrastructure.security import hash_password
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_socio_user():
    """Crea un usuario socio de prueba"""
    
    # Datos del usuario socio
    user_data = {
        'nombre_usuario': 'socio_test',
        'correo_electronico': 'socio@gmail.com',
        'password_plain': '123456',
        'rol': 4,  # ID del rol usuario (socio)
        'id_club': 1,  # ID del club por defecto
        'estado': 'activo'
    }
    
    # Datos del socio
    socio_data = {
        'id_club': 1,
        'nombres': 'Juan',
        'apellidos': 'Pérez',
        'ci_nit': '12345678',
        'telefono': '555-0123',
        'correo_electronico': 'socio@gmail.com',
        'direccion': 'Av. Principal 123',
        'estado': 1,  # ID del estado activo
        'fecha_nacimiento': '1990-05-15',
        'tipo_membresia': 'VIP'
    }
    
    try:
        # Conectar a la base de datos
        conn = psycopg2.connect(DATABASE_URL)
        cursor = conn.cursor()
        
        logger.info("👤 Creando usuario socio de prueba...")
        
        # Verificar si el usuario ya existe
        cursor.execute(
            "SELECT id_usuario FROM usuario WHERE nombre_usuario = %s OR correo_electronico = %s",
            (user_data['nombre_usuario'], user_data['correo_electronico'])
        )
        
        existing_user = cursor.fetchone()
        
        if existing_user:
            logger.warning(f"⚠️  El usuario ya existe con ID: {existing_user[0]}")
            user_id = existing_user[0]
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
        
        # Verificar si el socio ya existe
        cursor.execute(
            "SELECT id_socio FROM socio WHERE id_usuario = %s OR correo_electronico = %s",
            (user_id, socio_data['correo_electronico'])
        )
        
        existing_socio = cursor.fetchone()
        
        if existing_socio:
            logger.warning(f"⚠️  El socio ya existe con ID: {existing_socio[0]}")
            socio_id = existing_socio[0]
        else:
            # Crear nuevo socio asociado al usuario
            cursor.execute("""
                INSERT INTO socio (
                    id_club, nombres, apellidos, ci_nit, telefono, 
                    correo_electronico, direccion, estado, fecha_nacimiento, 
                    tipo_membresia, id_usuario
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                RETURNING id_socio
            """, (
                socio_data['id_club'],
                socio_data['nombres'],
                socio_data['apellidos'],
                socio_data['ci_nit'],
                socio_data['telefono'],
                socio_data['correo_electronico'],
                socio_data['direccion'],
                socio_data['estado'],
                socio_data['fecha_nacimiento'],
                socio_data['tipo_membresia'],
                user_id
            ))
            
            socio_id = cursor.fetchone()[0]
            conn.commit()
            logger.info(f"✅ Socio creado exitosamente con ID: {socio_id}")
        
        # Verificar la relación creada
        cursor.execute("""
            SELECT u.id_usuario, u.nombre_usuario, u.correo_electronico, 
                   r.nombre_rol, c.nombre_club, u.estado,
                   s.id_socio, s.nombres, s.apellidos, s.ci_nit, s.tipo_membresia
            FROM usuario u
            LEFT JOIN roles r ON u.rol = r.id_rol
            LEFT JOIN club c ON u.id_club = c.id_club
            LEFT JOIN socio s ON u.id_usuario = s.id_usuario
            WHERE u.id_usuario = %s
        """, (user_id,))
        
        user_info = cursor.fetchone()
        
        if user_info:
            logger.info("\n📋 INFORMACIÓN DEL USUARIO SOCIO CREADO:")
            logger.info("=" * 60)
            logger.info(f"🔑 USUARIO:")
            logger.info(f"   ID Usuario: {user_info[0]}")
            logger.info(f"   Nombre: {user_info[1]}")
            logger.info(f"   Correo: {user_info[2]}")
            logger.info(f"   Rol: {user_info[3]}")
            logger.info(f"   Club: {user_info[4]}")
            logger.info(f"   Estado: {user_info[5]}")
            logger.info(f"")
            logger.info(f"👤 SOCIO:")
            logger.info(f"   ID Socio: {user_info[6]}")
            logger.info(f"   Nombres: {user_info[7]} {user_info[8]}")
            logger.info(f"   CI/NIT: {user_info[9]}")
            logger.info(f"   Tipo Membresía: {user_info[10]}")
            logger.info("=" * 60)
            
            logger.info("\n🔑 CREDENCIALES DE PRUEBA:")
            logger.info(f"Usuario: {user_data['nombre_usuario']}")
            logger.info(f"Correo: {user_data['correo_electronico']}")
            logger.info(f"Contraseña: {user_data['password_plain']}")
            logger.info("=" * 60)
            
            logger.info("\n🌐 PARA PROBAR EL LOGIN:")
            logger.info("POST http://127.0.0.1:8000/login")
            logger.info("Body JSON:")
            logger.info("{")
            logger.info(f'  "correo_electronico": "{user_data["correo_electronico"]}",')
            logger.info(f'  "contrasena": "{user_data["password_plain"]}"')
            logger.info("}")
            logger.info("=" * 60)
            
            logger.info("\n💡 FUNCIONALIDADES:")
            logger.info("✅ Login como socio")
            logger.info("✅ Acceso a sus propios datos")
            logger.info("✅ Ver sus acciones y pagos")
            logger.info("✅ Acceso limitado según rol")
            logger.info("=" * 60)
        
        cursor.close()
        conn.close()
        
        return True
        
    except psycopg2.Error as e:
        logger.error(f"❌ Error de base de datos: {e}")
        return False
    except Exception as e:
        logger.error(f"❌ Error general: {e}")
        return False

def main():
    """Función principal"""
    print("🚀 CREANDO USUARIO SOCIO DE PRUEBA PARA CEAS")
    print("=" * 70)
    
    # Crear usuario socio
    if create_socio_user():
        print("\n✅ Usuario socio de prueba creado exitosamente")
        print("\n🎉 ¡Sistema completamente funcional!")
        print("=" * 70)
        print("💡 Ahora tienes dos tipos de usuarios:")
        print("   🔑 Admin: admin / prueba@gmail.com")
        print("   👤 Socio: socio_test / socio@gmail.com")
        print("   📝 Contraseña para ambos: 123456")
        print("\n🌐 Accede a la documentación en:")
        print("   http://127.0.0.1:8000/docs")
    else:
        print("\n❌ Error creando usuario socio de prueba")
        import sys
        sys.exit(1)

if __name__ == "__main__":
    main()
