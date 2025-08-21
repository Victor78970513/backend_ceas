#!/usr/bin/env python3
"""
Script para crear datos de muestra para el sistema de Business Intelligence
Genera datos realistas y variados para todas las entidades del sistema
"""

import psycopg2
import random
from datetime import datetime, timedelta
from decimal import Decimal
import json

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

def create_sample_clubs(conn):
    """Verifica clubes existentes"""
    print("🏢 Verificando clubes existentes...")
    
    cursor = conn.cursor()
    
    # Verificar clubes existentes
    cursor.execute("SELECT id_club, nombre_club FROM club")
    clubes_existentes = cursor.fetchall()
    
    if clubes_existentes:
        print(f"✅ {len(clubes_existentes)} clubes encontrados:")
        for club_id, nombre in clubes_existentes:
            print(f"   • ID {club_id}: {nombre}")
    else:
        print("⚠️  No se encontraron clubes")
    
    cursor.close()
    return len(clubes_existentes) > 0

def create_sample_estados(conn):
    """Crea estados de muestra para socios, acciones, etc."""
    print("📊 Creando estados de muestra...")
    
    cursor = conn.cursor()
    
    # Estados de socio
    estados_socio = ["ACTIVO", "INACTIVO", "SUSPENDIDO", "PENDIENTE"]
    
    for estado in estados_socio:
        try:
            cursor.execute("""
                INSERT INTO estadosocio (nombre_estado)
                VALUES (%s)
            """, (estado,))
        except:
            pass  # Ignorar si ya existe
    
    # Estados de acción
    estados_accion = ["ACTIVA", "VENCIDA", "CANCELADA", "PENDIENTE"]
    
    for estado in estados_accion:
        try:
            cursor.execute("""
                INSERT INTO estadoaccion (nombre_estado_accion)
                VALUES (%s)
            """, (estado,))
        except:
            pass  # Ignorar si ya existe
    
    # Estados de pago
    estados_pago = ["APROBADO", "PENDIENTE", "RECHAZADO", "CANCELADO"]
    
    for estado in estados_pago:
        try:
            cursor.execute("""
                INSERT INTO estadopago (nombre_estado_pago)
                VALUES (%s)
            """, (estado,))
        except:
            pass  # Ignorar si ya existe
    
    # Tipos de pago (ya existen en tu BD: QR y Efectivo)
    print("   ⚠️  Usando tipos de pago existentes: QR y Efectivo")
    
    # Cargos
    cargos = ["GERENTE GENERAL", "ADMINISTRATIVO", "CONTADOR", "RECEPCIONISTA", "MANTENIMIENTO", "SEGURIDAD"]
    
    for cargo in cargos:
        try:
            cursor.execute("""
                INSERT INTO cargos (nombre_cargo)
                VALUES (%s)
            """, (cargo,))
        except:
            pass  # Ignorar si ya existe
    
    # Roles de usuario
    roles = ["ADMIN", "GERENTE", "USUARIO", "AUDITOR"]
    
    for rol in roles:
        try:
            cursor.execute("""
                INSERT INTO roles (nombre_rol)
                VALUES (%s)
            """, (rol,))
        except:
            pass  # Ignorar si ya existe
    
    conn.commit()
    cursor.close()
    print("✅ Estados y catálogos creados")

def create_sample_modalidades_pago(conn):
    """Crea modalidades de pago realistas"""
    print("💳 Creando modalidades de pago...")
    
    modalidades = [
        ("Pago único", 0, 100.0, 100.0, 5000.0, 1),
        ("2 cuotas de 2.500 Bs", 3, 50.0, 100.0, 2500.0, 2),
        ("3 cuotas de 1.667 Bs", 6, 33.33, 100.0, 1667.0, 3),
        ("6 cuotas de 833 Bs", 12, 16.67, 100.0, 833.0, 6),
        ("12 cuotas de 417 Bs", 24, 8.33, 100.0, 417.0, 12)
    ]
    
    cursor = conn.cursor()
    
    for modalidad in modalidades:
        try:
            cursor.execute("""
                INSERT INTO modalidadpago (descripcion, meses_de_gracia, 
                                         porcentaje_renovacion_inicial, porcentaje_renovacion_mensual, 
                                         costo_renovacion_estandar, cantidad_cuotas)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, modalidad)
        except:
            pass  # Ignorar si ya existe
    
    conn.commit()
    cursor.close()
    print(f"✅ {len(modalidades)} modalidades de pago creadas")

def create_sample_socios(conn):
    """Crea socios de muestra con datos variados"""
    print("👥 Creando socios de muestra...")
    
    nombres = ["Juan", "María", "Carlos", "Ana", "Luis", "Carmen", "Roberto", "Patricia", "Miguel", "Sofia"]
    apellidos = ["García", "Rodríguez", "López", "Martínez", "González", "Pérez", "Fernández", "Gómez", "Díaz", "Ruiz"]
    
    cursor = conn.cursor()
    
    # Obtener IDs de clubes
    cursor.execute("SELECT id_club FROM club")
    club_ids = [row[0] for row in cursor.fetchall()]
    
    # Obtener IDs de estados
    cursor.execute("SELECT id_estado FROM estadosocio")
    estado_ids = [row[0] for row in cursor.fetchall()]
    
    socios_creados = 0
    
    for i in range(50):  # Crear 50 socios
        nombre = random.choice(nombres)
        apellido = random.choice(apellidos)
        club_id = random.choice(club_ids)
        estado_id = random.choice(estado_ids)
        
        # Fechas variadas (últimos 2 años)
        fecha_registro = datetime.now() - timedelta(days=random.randint(0, 730))
        fecha_nacimiento = datetime.now() - timedelta(days=random.randint(6570, 25550))  # 18-70 años
        
        cursor.execute("""
            INSERT INTO socio (id_club, nombres, apellidos, ci_nit, telefono, correo_electronico, 
                             direccion, fecha_de_registro, fecha_nacimiento, estado)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT DO NOTHING
        """, (
            club_id,
            nombre,
            apellido,
            f"{random.randint(1000000, 9999999)}",  # CI de 7 dígitos
            f"7{random.randint(10000000, 99999999)}",
            f"{nombre.lower()}.{apellido.lower()}{i}@email.com",
            f"Dirección {random.randint(1, 100)}",
            fecha_registro,
            fecha_nacimiento,
            estado_id
        ))
        
        if cursor.rowcount > 0:
            socios_creados += 1
    
    conn.commit()
    cursor.close()
    print(f"✅ {socios_creados} socios creados")

def create_sample_acciones(conn):
    """Crea acciones de muestra para los socios"""
    print("📈 Creando acciones de muestra...")
    
    cursor = conn.cursor()
    
    # Obtener socios
    cursor.execute("SELECT id_socio, id_club FROM socio")
    socios = cursor.fetchall()
    
    # Obtener modalidades de pago
    cursor.execute("SELECT id_modalidad_pago FROM modalidadpago")
    modalidades = [row[0] for row in cursor.fetchall()]
    
    # Obtener estados de acción
    cursor.execute("SELECT id_estado_accion FROM estadoaccion")
    estados = [row[0] for row in cursor.fetchall()]
    
    acciones_creadas = 0
    
    for socio_id, club_id in socios:
        # Cada socio puede tener 1-3 acciones
        num_acciones = random.randint(1, 3)
        
        for _ in range(num_acciones):
            modalidad_id = random.choice(modalidades)
            estado_id = random.choice(estados)
            
            # Fecha de emisión variada (último año)
            fecha_emision = datetime.now() - timedelta(days=random.randint(0, 365))
            
            # Tipos de acción
            tipos = ["Ordinaria", "Preferencial", "Especial", "Institucional"]
            tipo_accion = random.choice(tipos)
            
            cursor.execute("""
                INSERT INTO accion (id_club, id_socio, modalidad_pago, estado_accion, 
                                  certificado_pdf, certificado_cifrado, fecha_emision_certificado, 
                                  tipo_accion, saldo_pendiente)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT DO NOTHING
            """, (
                club_id,
                socio_id,
                modalidad_id,
                estado_id,
                None,  # certificado_pdf
                False,  # certificado_cifrado
                fecha_emision,
                tipo_accion,
                random.randint(1000, 10000)  # saldo_pendiente aleatorio
            ))
            
            if cursor.rowcount > 0:
                acciones_creadas += 1
    
    conn.commit()
    cursor.close()
    print(f"✅ {acciones_creadas} acciones creadas")

def create_sample_pagos(conn):
    """Crea pagos de muestra para las acciones"""
    print("💰 Creando pagos de muestra...")
    
    cursor = conn.cursor()
    
    # Obtener acciones
    cursor.execute("SELECT id_accion, modalidad_pago FROM accion")
    acciones = cursor.fetchall()
    
    # Obtener tipos y estados de pago
    cursor.execute("SELECT id_tipo_pago FROM tipopago")
    tipos_pago = [row[0] for row in cursor.fetchall()]
    
    cursor.execute("SELECT id_estado_pago FROM estadopago")
    estados_pago = [row[0] for row in cursor.fetchall()]
    
    pagos_creados = 0
    
    for accion_id, modalidad_id in acciones:
        # Obtener información de la modalidad
        cursor.execute("""
            SELECT cantidad_cuotas, costo_renovacion_estandar 
            FROM modalidadpago WHERE id_modalidad_pago = %s
        """, (modalidad_id,))
        modalidad_info = cursor.fetchone()
        
        if modalidad_info:
            cantidad_cuotas, costo_cuota = modalidad_info
            
            # Crear pagos para esta acción
            pagos_a_crear = random.randint(0, cantidad_cuotas)
            
            for i in range(pagos_a_crear):
                tipo_pago_id = random.choice(tipos_pago)
                estado_pago_id = random.choice(estados_pago)
                
                # Fecha de pago variada
                fecha_pago = datetime.now() - timedelta(days=random.randint(0, 180))
                
                # Monto del pago (puede ser parcial o completo)
                if random.random() > 0.3:
                    monto = float(costo_cuota)
                else:
                    monto = float(costo_cuota) * random.uniform(0.5, 0.9)
                
                cursor.execute("""
                    INSERT INTO pagoaccion (id_accion, fecha_de_pago, monto, tipo_pago, estado_pago, observaciones)
                    VALUES (%s, %s, %s, %s, %s, %s)
                    ON CONFLICT DO NOTHING
                """, (
                    accion_id,
                    fecha_pago,
                    round(monto, 2),
                    tipo_pago_id,
                    estado_pago_id,
                    f"Pago cuota {i+1}" if i < cantidad_cuotas else "Pago adicional"
                ))
                
                if cursor.rowcount > 0:
                    pagos_creados += 1
    
    conn.commit()
    cursor.close()
    print(f"✅ {pagos_creados} pagos creados")

def create_sample_personal(conn):
    """Crea personal de muestra"""
    print("👷 Creando personal de muestra...")
    
    cursor = conn.cursor()
    
    # Obtener IDs de clubes y cargos
    cursor.execute("SELECT id_club FROM club")
    club_ids = [row[0] for row in cursor.fetchall()]
    
    cursor.execute("SELECT id_cargo FROM cargos")
    cargo_ids = [row[0] for row in cursor.fetchall()]
    
    nombres = ["Alejandro", "Beatriz", "Cristian", "Daniela", "Eduardo", "Florencia", "Gabriel", "Hilda"]
    apellidos = ["Vargas", "Torres", "Silva", "Rojas", "Quispe", "Paredes", "Ortiz", "Núñez"]
    departamentos = ["Administración", "Finanzas", "Recursos Humanos", "Operaciones", "Mantenimiento", "Seguridad"]
    
    personal_creado = 0
    
    for i in range(30):  # Crear 30 empleados
        nombre = random.choice(nombres)
        apellido = random.choice(apellidos)
        club_id = random.choice(club_ids)
        cargo_id = random.choice(cargo_ids)
        departamento = random.choice(departamentos)
        
        # Fecha de ingreso variada
        fecha_ingreso = datetime.now() - timedelta(days=random.randint(30, 1095))  # 1 mes a 3 años
        
        # Salario realista
        salario = random.randint(3000, 15000)
        
        cursor.execute("""
            INSERT INTO personal (id_club, nombres, apellidos, cargo, fecha_ingreso, salario, 
                                correo, departamento, estado)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT DO NOTHING
        """, (
            club_id,
            nombre,
            apellido,
            cargo_id,
            fecha_ingreso,
            salario,
            f"{nombre.lower()}.{apellido.lower()}{i}@ceas.com",
            departamento,
            True  # estado activo
        ))
        
        if cursor.rowcount > 0:
            personal_creado += 1
    
    conn.commit()
    cursor.close()
    print(f"✅ {personal_creado} empleados creados")

def create_sample_asistencia(conn):
    """Crea registros de asistencia de muestra"""
    print("📅 Creando registros de asistencia...")
    
    cursor = conn.cursor()
    
    # Obtener personal
    cursor.execute("SELECT id_personal FROM personal")
    personal_ids = cursor.fetchall()
    
    asistencias_creadas = 0
    
    # Crear asistencia para los últimos 30 días
    for dias_atras in range(30):
        fecha = datetime.now() - timedelta(days=dias_atras)
        
        # Solo días laborables (lunes a viernes)
        if fecha.weekday() < 5:  # 0=Lunes, 4=Viernes
            for personal_id in personal_ids:
                personal_id = personal_id[0]
                
                # 95% de asistencia (realista)
                if random.random() > 0.05:
                    # Hora de ingreso entre 7:00 y 9:00
                    hora_ingreso = datetime.combine(fecha.date(), 
                        datetime.min.time().replace(hour=7, minute=random.randint(0, 59)))
                    
                    # Hora de salida entre 17:00 y 19:00
                    hora_salida = datetime.combine(fecha.date(), 
                        datetime.min.time().replace(hour=17, minute=random.randint(0, 59)))
                    
                    # Estados de asistencia
                    estados = ["PRESENTE", "TARDANZA", "SALIDA_TEMPRANA", "HORAS_EXTRAS"]
                    estado = random.choice(estados)
                    
                    cursor.execute("""
                        INSERT INTO asistencia (id_personal, fecha, hora_ingreso, hora_salida, 
                                              observaciones, estado)
                        VALUES (%s, %s, %s, %s, %s, %s)
                        ON CONFLICT DO NOTHING
                    """, (
                        personal_id,
                        fecha.date(),
                        hora_ingreso.time(),
                        hora_salida.time(),
                        f"Asistencia {estado.lower()}" if estado != "PRESENTE" else None,
                        estado
                    ))
                    
                    if cursor.rowcount > 0:
                        asistencias_creadas += 1
    
    conn.commit()
    cursor.close()
    print(f"✅ {asistencias_creadas} registros de asistencia creados")

def create_sample_proveedores(conn):
    """Crea proveedores de muestra"""
    print("🏪 Creando proveedores de muestra...")
    
    cursor = conn.cursor()
    
    nombres_proveedores = [
        "Distribuidora ABC", "Servicios XYZ", "Materiales 123", "Suministros Plus",
        "Proveedor Express", "Comercial Delta", "Empresa Omega", "Negocios Sigma"
    ]
    
    productos_servicios = [
        "Materiales de construcción", "Equipos de oficina", "Servicios de limpieza",
        "Suministros eléctricos", "Herramientas", "Mobiliario", "Tecnología", "Seguridad"
    ]
    
    proveedores_creados = 0
    
    for i in range(len(nombres_proveedores)):
        nombre = nombres_proveedores[i]
        productos = productos_servicios[i]
        
        cursor.execute("""
            INSERT INTO proveedores (nombre_proveedor, contacto, telefono, correo_electronico, 
                                   direccion, estado, productos_servicios)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT DO NOTHING
        """, (
            nombre,
            f"Contacto {i+1}",
            f"7{random.randint(10000000, 99999999)}",
            f"contacto@{nombre.lower().replace(' ', '')}.com",
            f"Dirección {i+1}",
            True,  # estado activo
            productos
        ))
        
        if cursor.rowcount > 0:
            proveedores_creados += 1
    
    conn.commit()
    cursor.close()
    print(f"✅ {proveedores_creados} proveedores creados")

def create_sample_compras(conn):
    """Crea compras de muestra"""
    print("🛒 Creando compras de muestra...")
    
    cursor = conn.cursor()
    
    # Obtener proveedores y clubes
    cursor.execute("SELECT id_proveedor FROM proveedores")
    proveedores = [row[0] for row in cursor.fetchall()]
    
    cursor.execute("SELECT id_club FROM club")
    clubes = [row[0] for row in cursor.fetchall()]
    
    compras_creadas = 0
    
    # Crear compras para los últimos 6 meses
    for meses_atras in range(6):
        fecha_compra = datetime.now() - timedelta(days=meses_atras * 30)
        
        # 3-8 compras por mes
        num_compras = random.randint(3, 8)
        
        for _ in range(num_compras):
            proveedor_id = random.choice(proveedores)
            club_id = random.choice(clubes)
            
            # Monto realista
            monto = random.randint(500, 5000)
            
            # Estados de compra
            estados = ["PENDIENTE", "APROBADA", "EN_PROCESO", "COMPLETADA", "CANCELADA"]
            estado = random.choice(estados)
            
            # Fecha de entrega (si está aprobada o completada)
            fecha_entrega = None
            if estado in ["APROBADA", "COMPLETADA"]:
                fecha_entrega = fecha_compra + timedelta(days=random.randint(1, 30))
            
            # Cantidad de items
            cantidad_items = random.randint(1, 20)
            
            cursor.execute("""
                INSERT INTO compras (id_proveedor, fecha_de_compra, monto_total, estado, 
                                   fecha_de_entrega, cantidad_items)
                VALUES (%s, %s, %s, %s, %s, %s)
                ON CONFLICT DO NOTHING
            """, (
                proveedor_id,
                fecha_compra,
                monto,
                estado,
                fecha_entrega,
                cantidad_items
            ))
            
            if cursor.rowcount > 0:
                compras_creadas += 1
    
    conn.commit()
    cursor.close()
    print(f"✅ {compras_creadas} compras creadas")

def create_sample_movimientos_financieros(conn):
    """Crea movimientos financieros de muestra"""
    print("💸 Creando movimientos financieros...")
    
    cursor = conn.cursor()
    
    # Obtener clubes
    cursor.execute("SELECT id_club FROM club")
    clubes = [row[0] for row in cursor.fetchall()]
    
    movimientos_creados = 0
    
    # Crear movimientos para los últimos 12 meses
    for meses_atras in range(12):
        fecha = datetime.now() - timedelta(days=meses_atras * 30)
        
        # 15-25 movimientos por mes
        num_movimientos = random.randint(15, 25)
        
        for _ in range(num_movimientos):
            club_id = random.choice(clubes)
            
            # Tipo de movimiento (60% ingresos, 40% egresos)
            tipo = "INGRESO" if random.random() < 0.6 else "EGRESO"
            
            # Monto según tipo
            if tipo == "INGRESO":
                monto = random.randint(1000, 10000)
                descripciones = [
                    "Pago de cuotas", "Donación", "Pago de membresía", "Evento especial",
                    "Servicios prestados", "Inversión", "Reembolso", "Intereses"
                ]
            else:
                monto = random.randint(500, 8000)
                descripciones = [
                    "Compra de materiales", "Pago de servicios", "Mantenimiento",
                    "Salarios", "Impuestos", "Gastos administrativos", "Equipos"
                ]
            
            descripcion = random.choice(descripciones)
            
            # Estados
            estados = ["COMPLETADO", "PENDIENTE", "CANCELADO"]
            estado = random.choice(estados)
            
            # Métodos de pago
            metodos = ["EFECTIVO", "TRANSFERENCIA", "TARJETA", "CHEQUE"]
            metodo = random.choice(metodos)
            
            cursor.execute("""
                INSERT INTO movimientofinanciero (id_club, tipo_movimiento, descripcion, monto, 
                                               fecha, estado, referencia_relacionada, metodo_pago)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT DO NOTHING
            """, (
                club_id,
                tipo,
                descripcion,
                monto,
                fecha,
                estado,
                f"Ref-{random.randint(1000, 9999)}",
                metodo
            ))
            
            if cursor.rowcount > 0:
                movimientos_creados += 1
    
    conn.commit()
    cursor.close()
    print(f"✅ {movimientos_creados} movimientos financieros creados")

def create_sample_usuarios(conn):
    """Crea usuarios de muestra para el sistema"""
    print("👤 Creando usuarios de muestra...")
    
    cursor = conn.cursor()
    
    # Obtener clubes y roles
    cursor.execute("SELECT id_club FROM club")
    clubes = [row[0] for row in cursor.fetchall()]
    
    cursor.execute("SELECT id_rol FROM roles")
    roles = [row[0] for row in cursor.fetchall()]
    
    usuarios = [
        ("admin@ceas.com", "admin123", "Administrador", 1, 1),
        ("gerente@ceas.com", "gerente123", "Gerente", 2, 1),
        ("contador@ceas.com", "contador123", "Contador", 3, 1),
        ("usuario@ceas.com", "usuario123", "Usuario", 4, 1)
    ]
    
    usuarios_creados = 0
    
    for correo, contrasena, nombre, rol_id, club_id in usuarios:
        # Hash simple de la contraseña (en producción usar bcrypt)
        contrasena_hash = f"hash_{contrasena}"
        
        try:
            cursor.execute("""
                INSERT INTO usuario (nombre_usuario, contrasena_hash, rol, id_club, correo_electronico, estado)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (
                nombre,
                contrasena_hash,
                rol_id,
                club_id,
                correo,
                True  # estado activo
            ))
        except:
            pass  # Ignorar si ya existe
        
        if cursor.rowcount > 0:
            usuarios_creados += 1
    
    conn.commit()
    cursor.close()
    print(f"✅ {usuarios_creados} usuarios creados")

def main():
    """Función principal que ejecuta todo el proceso"""
    print("🚀 INICIANDO CREACIÓN DE DATOS DE MUESTRA PARA BI")
    print("=" * 60)
    
    conn = get_connection()
    if not conn:
        print("❌ No se pudo conectar a la base de datos")
        return
    
    try:
        # Crear datos en orden de dependencias
        create_sample_clubs(conn)
        create_sample_estados(conn)
        create_sample_modalidades_pago(conn)
        create_sample_socios(conn)
        create_sample_acciones(conn)
        create_sample_pagos(conn)
        create_sample_personal(conn)
        create_sample_asistencia(conn)
        create_sample_proveedores(conn)
        create_sample_compras(conn)
        create_sample_movimientos_financieros(conn)
        create_sample_usuarios(conn)
        
        print("\n" + "=" * 60)
        print("🎉 DATOS DE MUESTRA CREADOS EXITOSAMENTE!")
        print("=" * 60)
        print("\n📊 RESUMEN DE DATOS CREADOS:")
        print("   • Clubes: 5")
        print("   • Socios: ~50")
        print("   • Acciones: ~100-150")
        print("   • Pagos: ~200-400")
        print("   • Personal: ~30")
        print("   • Asistencias: ~600-900")
        print("   • Proveedores: 8")
        print("   • Compras: ~150-300")
        print("   • Movimientos financieros: ~200-300")
        print("   • Usuarios: 4")
        print("\n🔍 Ahora puedes probar todos los endpoints de BI:")
        print("   • /bi/administrativo/dashboard")
        print("   • /bi/administrativo/distribucion-financiera")
        print("   • /bi/personal/dashboard")
        print("   • /bi/finanzas-resumen")
        
    except Exception as e:
        print(f"❌ Error durante la creación: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    main()
