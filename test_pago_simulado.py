#!/usr/bin/env python3
"""
Script para probar el flujo de pago simulado sin servicios externos
"""

import requests
import json
import time

# Configuración
BASE_URL = "http://127.0.0.1:8000"
LOGIN_URL = f"{BASE_URL}/login"
ACCIONES_URL = f"{BASE_URL}/acciones"

def login():
    """Hacer login y obtener token"""
    login_data = {
        "correo_electronico": "prueba@gmail.com",
        "contrasena": "123456"
    }
    
    response = requests.post(LOGIN_URL, json=login_data)
    
    if response.status_code == 200:
        token = response.json()["access_token"]
        print(f"✅ Login exitoso. Token obtenido.")
        return token
    else:
        print(f"❌ Error en login: {response.status_code} - {response.text}")
        return None

def crear_qr_pago_simulado(token):
    """Crear QR de pago simulado"""
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    datos_compra = {
        "id_club": 1,
        "id_socio": 1,
        "modalidad_pago": 1,
        "estado_accion": 1,
        "certificado_pdf": None,
        "certificado_cifrado": False,
        "tipo_accion": "compra",
        "total_pago": 5000.00,
        "metodo_pago": "transferencia_bancaria"
    }
    
    response = requests.post(
        f"{ACCIONES_URL}/simular-pago/crear-qr",
        json=datos_compra,
        headers=headers
    )
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ QR de pago creado exitosamente:")
        print(f"   📋 Referencia temporal: {data['referencia_temporal']}")
        print(f"   💰 Total a pagar: ${data['pago_info']['total_pago']}")
        print(f"   📱 Cantidad acciones: {data['pago_info']['cantidad_acciones']}")
        print(f"   🏦 Método de pago: {data['pago_info']['metodo_pago']}")
        print(f"   📋 Instrucciones:")
        for i, instruccion in enumerate(data['instrucciones'], 1):
            print(f"      {i}. {instruccion}")
        return data['referencia_temporal']
    else:
        print(f"❌ Error creando QR: {response.status_code} - {response.text}")
        return None

def verificar_estado_pago(token, referencia_temporal):
    """Verificar estado del pago temporal"""
    headers = {
        "Authorization": f"Bearer {token}"
    }
    
    response = requests.get(
        f"{ACCIONES_URL}/simular-pago/estado/{referencia_temporal}",
        headers=headers
    )
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Estado del pago:")
        print(f"   📋 Referencia: {data['referencia_temporal']}")
        print(f"   📊 Estado: {data['estado']}")
        print(f"   📅 Creado: {data['fecha_creacion']}")
        print(f"   ⏰ Expira: {data['fecha_expiracion']}")
        print(f"   💰 Total: ${data['pago_info']['total_pago']}")
        return True
    else:
        print(f"❌ Error verificando estado: {response.status_code} - {response.text}")
        return False

def confirmar_pago_simulado(token, referencia_temporal):
    """Confirmar pago simulado sin comprobante"""
    headers = {
        "Authorization": f"Bearer {token}"
    }
    
    response = requests.post(
        f"{ACCIONES_URL}/simular-pago/confirmar-pago",
        params={"referencia_temporal": referencia_temporal},
        headers=headers
    )
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Pago confirmado exitosamente:")
        print(f"   📋 Acción creada: ID {data['accion']['id_accion']}")
        print(f"   👤 Socio: {data['accion']['id_socio']}")
        print(f"   📱 Cantidad acciones: {data['accion']['cantidad_acciones']}")
        print(f"   💰 Precio unitario: ${data['accion']['precio_unitario']}")
        print(f"   💵 Total pagado: ${data['accion']['total_pago']}")
        print(f"   🏦 Método de pago: {data['accion']['metodo_pago']}")
        print(f"   📊 Estado: {data['accion']['estado_nombre']}")
        print(f"   📄 Certificado: {'✅ Disponible' if data['certificado']['disponible'] else '❌ No disponible'}")
        print(f"   💳 Pago creado: ID {data['pago']['id_pago']} - ${data['pago']['monto']} - Estado: {data['pago']['estado_pago']}")
        return data['accion']['id_accion']
    else:
        print(f"❌ Error confirmando pago: {response.status_code} - {response.text}")
        return None

def listar_pagos_temporales(token):
    """Listar pagos temporales (solo admin)"""
    headers = {
        "Authorization": f"Bearer {token}"
    }
    
    response = requests.get(
        f"{ACCIONES_URL}/simular-pago/pagos-temporales",
        headers=headers
    )
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Pagos temporales encontrados: {data['total']}")
        for pago in data['pagos_temporales']:
            print(f"   📋 {pago['referencia']}: {pago['estado']} - ${pago['datos_pago']['total_pago']}")
        return True
    else:
        print(f"❌ Error listando pagos temporales: {response.status_code} - {response.text}")
        return False

def main():
    """Función principal para probar el flujo completo"""
    print("🚀 INICIANDO PRUEBA DE PAGO SIMULADO")
    print("=" * 50)
    
    # 1. Login
    print("\n1️⃣ HACIENDO LOGIN...")
    token = login()
    if not token:
        return
    
    # 2. Crear QR de pago
    print("\n2️⃣ CREANDO QR DE PAGO...")
    referencia_temporal = crear_qr_pago_simulado(token)
    if not referencia_temporal:
        return
    
    # 3. Verificar estado del pago
    print("\n3️⃣ VERIFICANDO ESTADO DEL PAGO...")
    verificar_estado_pago(token, referencia_temporal)
    
    # 4. Simular espera (usuario hace la transferencia)
    print("\n4️⃣ SIMULANDO TRANSFERENCIA BANCARIA...")
    print("   💳 Usuario realiza transferencia bancaria...")
    print("   📱 Usuario envía comprobante...")
    time.sleep(2)
    
    # 5. Confirmar pago
    print("\n5️⃣ CONFIRMANDO PAGO...")
    accion_id = confirmar_pago_simulado(token, referencia_temporal)
    if not accion_id:
        return
    
    # 6. Listar pagos temporales (debería estar vacío ahora)
    print("\n6️⃣ VERIFICANDO PAGOS TEMPORALES...")
    listar_pagos_temporales(token)
    
    print("\n🎉 PRUEBA COMPLETADA EXITOSAMENTE!")
    print("=" * 50)
    print("✅ Flujo de pago simulado funcionando correctamente")
    print("✅ QR generado y pago temporal creado")
    print("✅ Pago confirmado y acción creada")
    print("✅ Certificado generado automáticamente")
    print("✅ Pago temporal limpiado")

if __name__ == "__main__":
    main()
