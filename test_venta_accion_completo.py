#!/usr/bin/env python3
"""
Script de prueba para el flujo completo de venta de acciones con QR
"""

import requests
import json
import time
import os
from datetime import datetime

# Configuración
BASE_URL = "http://127.0.0.1:8000"
ADMIN_EMAIL = "prueba@gmail.com"
ADMIN_PASSWORD = "123456"

def obtener_token_admin():
    """Obtiene token de administrador"""
    print("🔐 Obteniendo token de administrador...")
    
    response = requests.post(f"{BASE_URL}/login", json={
        "correo_electronico": ADMIN_EMAIL,
        "contrasena": ADMIN_PASSWORD
    })
    
    if response.status_code == 200:
        token = response.json()["access_token"]
        print("✅ Token obtenido exitosamente")
        return token
    else:
        print(f"❌ Error obteniendo token: {response.text}")
        return None

def crear_accion_prueba(token):
    """Crea una acción de prueba"""
    print("\n📝 Creando acción de prueba...")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    accion_data = {
        "id_club": 1,
        "id_socio": 1,  # Primer socio de prueba
        "modalidad_pago": 1,
        "estado_accion": 1,  # Pendiente pago
        "tipo_accion": "compra",
        "cantidad_acciones": 100,
        "precio_unitario": 50.00,
        "total_pago": 5000.00,
        "metodo_pago": "qr_transferencia"
    }
    
    response = requests.post(f"{BASE_URL}/acciones/", json=accion_data, headers=headers)
    
    if response.status_code == 200:
        accion = response.json()
        print(f"✅ Acción creada exitosamente - ID: {accion['id_accion']}")
        return accion
    else:
        print(f"❌ Error creando acción: {response.text}")
        return None

def generar_qr_pago(token, accion_id):
    """Genera QR de pago"""
    print(f"\n📱 Generando QR para acción {accion_id}...")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    response = requests.post(f"{BASE_URL}/acciones/{accion_id}/generar-qr", headers=headers)
    
    if response.status_code == 200:
        qr_info = response.json()
        print("✅ QR generado exitosamente")
        print(f"   Tipo: {qr_info['tipo']}")
        print(f"   Archivo: {qr_info['qr_image']}")
        print("   Instrucciones:")
        for i, instruccion in enumerate(qr_info['instrucciones'], 1):
            print(f"   {i}. {instruccion}")
        return qr_info
    else:
        print(f"❌ Error generando QR: {response.text}")
        return None

def simular_subida_comprobante(token, accion_id):
    """Simula subida de comprobante"""
    print(f"\n📄 Simulando subida de comprobante para acción {accion_id}...")
    
    # Crear un archivo de comprobante simulado
    comprobante_path = "comprobante_simulado.txt"
    with open(comprobante_path, "w") as f:
        f.write(f"Comprobante de pago simulado para acción {accion_id}\n")
        f.write(f"Fecha: {datetime.now()}\n")
        f.write(f"Monto: 5000.00 Bs\n")
        f.write(f"Referencia: ACC{accion_id:06d}\n")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    with open(comprobante_path, "rb") as f:
        files = {"comprobante": ("comprobante_simulado.txt", f, "text/plain")}
        response = requests.post(f"{BASE_URL}/acciones/{accion_id}/subir-comprobante", 
                               files=files, headers=headers)
    
    # Limpiar archivo temporal
    os.remove(comprobante_path)
    
    if response.status_code == 200:
        resultado = response.json()
        print("✅ Comprobante subido exitosamente")
        print(f"   Estado: {resultado['estado']}")
        print(f"   Archivo: {resultado['archivo']}")
        return resultado
    else:
        print(f"❌ Error subiendo comprobante: {response.text}")
        return None

def aprobar_pago_admin(token, accion_id):
    """Admin aprueba el pago"""
    print(f"\n✅ Aprobando pago para acción {accion_id}...")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    response = requests.post(f"{BASE_URL}/acciones/{accion_id}/aprobar-pago", headers=headers)
    
    if response.status_code == 200:
        resultado = response.json()
        print("✅ Pago aprobado exitosamente")
        print(f"   Estado: {resultado['estado']}")
        print(f"   Certificado disponible: {resultado['certificado_disponible']}")
        return resultado
    else:
        print(f"❌ Error aprobando pago: {response.text}")
        return None

def descargar_certificado(token, accion_id):
    """Descarga el certificado"""
    print(f"\n📄 Descargando certificado para acción {accion_id}...")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    response = requests.get(f"{BASE_URL}/acciones/{accion_id}/descargar-certificado", headers=headers)
    
    if response.status_code == 200:
        # Guardar certificado
        filename = f"certificado_accion_{accion_id}_descargado.pdf"
        with open(filename, "wb") as f:
            f.write(response.content)
        
        print(f"✅ Certificado descargado exitosamente: {filename}")
        print(f"   Tamaño: {len(response.content)} bytes")
        return filename
    else:
        print(f"❌ Error descargando certificado: {response.text}")
        return None

def verificar_estado_accion(token, accion_id):
    """Verifica el estado de la acción"""
    print(f"\n🔍 Verificando estado de acción {accion_id}...")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    response = requests.get(f"{BASE_URL}/acciones/{accion_id}/estado", headers=headers)
    
    if response.status_code == 200:
        estado = response.json()
        print("✅ Estado obtenido exitosamente")
        print(f"   Estado: {estado['estado_nombre']}")
        print(f"   Método de pago: {estado['metodo_pago']}")
        print(f"   Total: Bs. {estado['total_pago']}")
        print(f"   Certificado disponible: {estado['certificado_disponible']}")
        return estado
    else:
        print(f"❌ Error obteniendo estado: {response.text}")
        return None

def test_flujo_completo():
    """Ejecuta el flujo completo de prueba"""
    print("🚀 INICIANDO PRUEBA COMPLETA DE VENTA DE ACCIONES CON QR")
    print("=" * 60)
    
    # 1. Obtener token de admin
    token = obtener_token_admin()
    if not token:
        return False
    
    # 2. Crear acción de prueba
    accion = crear_accion_prueba(token)
    if not accion:
        return False
    
    accion_id = accion["id_accion"]
    
    # 3. Verificar estado inicial
    verificar_estado_accion(token, accion_id)
    
    # 4. Generar QR de pago
    qr_info = generar_qr_pago(token, accion_id)
    if not qr_info:
        return False
    
    # 5. Simular subida de comprobante
    time.sleep(2)  # Pausa para simular tiempo de transferencia
    comprobante_result = simular_subida_comprobante(token, accion_id)
    if not comprobante_result:
        return False
    
    # 6. Verificar estado después de comprobante
    verificar_estado_accion(token, accion_id)
    
    # 7. Admin aprueba el pago
    time.sleep(2)  # Pausa para simular revisión
    aprobacion_result = aprobar_pago_admin(token, accion_id)
    if not aprobacion_result:
        return False
    
    # 8. Verificar estado final
    verificar_estado_accion(token, accion_id)
    
    # 9. Descargar certificado
    certificado_path = descargar_certificado(token, accion_id)
    if not certificado_path:
        return False
    
    print("\n" + "=" * 60)
    print("🎉 PRUEBA COMPLETA EXITOSA")
    print("✅ Todos los pasos del flujo se ejecutaron correctamente")
    print(f"✅ Certificado generado: {certificado_path}")
    print("✅ Sistema de venta de acciones con QR funcionando correctamente")
    
    return True

def limpiar_archivos_prueba():
    """Limpia archivos generados durante la prueba"""
    print("\n🧹 Limpiando archivos de prueba...")
    
    archivos_a_limpiar = [
        "certificado_accion_*_descargado.pdf",
        "qr_codes/transferencia_*.png",
        "certificados/originales/certificado_accion_*.pdf",
        "certificados/cifrados/certificado_accion_*_cifrado_*.bin",
        "comprobantes/comprobante_accion_*.pdf"
    ]
    
    import glob
    archivos_eliminados = 0
    
    for patron in archivos_a_limpiar:
        for archivo in glob.glob(patron):
            try:
                os.remove(archivo)
                archivos_eliminados += 1
                print(f"   🗑️  Eliminado: {archivo}")
            except Exception as e:
                print(f"   ⚠️  No se pudo eliminar {archivo}: {e}")
    
    print(f"✅ Se eliminaron {archivos_eliminados} archivos de prueba")

if __name__ == "__main__":
    try:
        # Ejecutar prueba completa
        exito = test_flujo_completo()
        
        if exito:
            print("\n🎯 RESULTADO: PRUEBA EXITOSA")
            print("El sistema de venta de acciones con QR está funcionando correctamente")
        else:
            print("\n❌ RESULTADO: PRUEBA FALLIDA")
            print("Hubo errores en el flujo de venta de acciones")
        
        # Limpiar archivos de prueba
        limpiar_archivos_prueba()
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Prueba interrumpida por el usuario")
    except Exception as e:
        print(f"\n❌ Error inesperado: {str(e)}")
        import traceback
        traceback.print_exc()
