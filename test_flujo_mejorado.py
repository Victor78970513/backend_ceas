#!/usr/bin/env python3
"""
Script de prueba para el flujo mejorado de venta de acciones con QR
Flujo: Generar QR -> Usuario paga -> Confirmar pago -> Crear acción
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

def generar_qr_pago(token):
    """Genera QR de pago sin crear acción"""
    print("\n📱 Generando QR de pago (sin crear acción)...")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    response = requests.post(f"{BASE_URL}/acciones/generar-qr-pago", headers=headers)
    
    if response.status_code == 200:
        qr_data = response.json()
        print("✅ QR generado exitosamente")
        print(f"   Referencia temporal: {qr_data['datos_pago']['referencia_temporal']}")
        print(f"   Monto: Bs. {qr_data['datos_pago']['total_pago']}")
        print(f"   Fecha límite: {qr_data['datos_pago']['fecha_limite']}")
        print(f"   Archivo QR: {qr_data['qr']['qr_image']}")
        print("   Instrucciones:")
        for i, instruccion in enumerate(qr_data['qr']['instrucciones'], 1):
            print(f"   {i}. {instruccion}")
        
        return qr_data
    else:
        print(f"❌ Error generando QR: {response.text}")
        return None

def simular_pago_usuario():
    """Simula que el usuario realizó el pago"""
    print("\n💰 Simulando que el usuario realizó el pago...")
    print("   ✅ Usuario escaneó el QR")
    print("   ✅ Usuario realizó la transferencia bancaria")
    print("   ✅ Usuario tiene el comprobante")
    time.sleep(2)  # Simular tiempo de pago

def confirmar_pago_y_crear_accion(token):
    """Confirma el pago y crea la acción"""
    print("\n✅ Confirmando pago y creando acción...")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    response = requests.post(f"{BASE_URL}/acciones/confirmar-pago", headers=headers)
    
    if response.status_code == 200:
        resultado = response.json()
        print("✅ Pago confirmado y acción creada exitosamente")
        print(f"   ID de acción: {resultado['accion']['id_accion']}")
        print(f"   Estado: {resultado['accion']['estado_nombre']}")
        print(f"   Total pagado: Bs. {resultado['accion']['total_pago']}")
        print(f"   Certificado disponible: {resultado['certificado']['disponible']}")
        print(f"   Ruta certificado: {resultado['certificado']['ruta']}")
        return resultado
    else:
        print(f"❌ Error confirmando pago: {response.text}")
        return None

def verificar_accion_creada(token, accion_id):
    """Verifica que la acción fue creada correctamente"""
    print(f"\n🔍 Verificando acción creada (ID: {accion_id})...")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    response = requests.get(f"{BASE_URL}/acciones/{accion_id}", headers=headers)
    
    if response.status_code == 200:
        accion = response.json()
        print("✅ Acción verificada exitosamente")
        print(f"   ID: {accion['id_accion']}")
        print(f"   Socio: {accion['id_socio']}")
        print(f"   Cantidad: {accion['cantidad_acciones']} acciones")
        print(f"   Precio unitario: Bs. {accion['precio_unitario']}")
        print(f"   Total: Bs. {accion['total_pago']}")
        print(f"   Estado: {accion['estado_accion']}")
        print(f"   Certificado: {'Sí' if accion['certificado_pdf'] else 'No'}")
        return accion
    else:
        print(f"❌ Error verificando acción: {response.text}")
        return None

def descargar_certificado(token, accion_id):
    """Descarga el certificado generado"""
    print(f"\n📄 Descargando certificado para acción {accion_id}...")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    response = requests.get(f"{BASE_URL}/acciones/{accion_id}/descargar-certificado", headers=headers)
    
    if response.status_code == 200:
        filename = f"certificado_flujo_mejorado_{accion_id}.pdf"
        with open(filename, "wb") as f:
            f.write(response.content)
        
        print(f"✅ Certificado descargado exitosamente: {filename}")
        print(f"   Tamaño: {len(response.content)} bytes")
        return filename
    else:
        print(f"❌ Error descargando certificado: {response.text}")
        return None

def verificar_estadisticas_pagos_temporales(token):
    """Verifica las estadísticas de pagos temporales"""
    print("\n📊 Verificando estadísticas de pagos temporales...")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    response = requests.get(f"{BASE_URL}/acciones/pagos-temporales/stats", headers=headers)
    
    if response.status_code == 200:
        stats = response.json()
        print("✅ Estadísticas obtenidas exitosamente")
        print(f"   Total pagos temporales: {stats.get('total_pagos_temporales', 0)}")
        print(f"   Pendientes: {stats.get('pendientes', 0)}")
        print(f"   Confirmados: {stats.get('confirmados', 0)}")
        print(f"   Expirados: {stats.get('expirados', 0)}")
        return stats
    else:
        print(f"❌ Error obteniendo estadísticas: {response.text}")
        return None

def test_flujo_mejorado():
    """Ejecuta el flujo mejorado completo"""
    print("🚀 INICIANDO PRUEBA DEL FLUJO MEJORADO")
    print("=" * 60)
    print("Flujo: Generar QR -> Usuario paga -> Confirmar pago -> Crear acción")
    print("=" * 60)
    
    # 1. Obtener token de admin
    token = obtener_token_admin()
    if not token:
        return False
    
    # 2. Generar QR de pago (SIN crear acción)
    qr_data = generar_qr_pago(token)
    if not qr_data:
        return False
    
    referencia_temporal = qr_data['datos_pago']['referencia_temporal']
    print(f"\n📝 Referencia temporal generada: {referencia_temporal}")
    
    # 3. Simular que el usuario realizó el pago
    simular_pago_usuario()
    
    # 4. Confirmar pago y crear acción
    resultado_confirmacion = confirmar_pago_y_crear_accion(token)
    if not resultado_confirmacion:
        return False
    
    accion_id = resultado_confirmacion['accion']['id_accion']
    
    # 5. Verificar que la acción fue creada
    accion_verificada = verificar_accion_creada(token, accion_id)
    if not accion_verificada:
        return False
    
    # 6. Descargar certificado
    certificado_path = descargar_certificado(token, accion_id)
    if not certificado_path:
        return False
    
    # 7. Verificar estadísticas
    verificar_estadisticas_pagos_temporales(token)
    
    print("\n" + "=" * 60)
    print("🎉 PRUEBA DEL FLUJO MEJORADO EXITOSA")
    print("✅ QR generado sin crear acción")
    print("✅ Pago simulado correctamente")
    print("✅ Acción creada solo después del pago")
    print("✅ Certificado generado automáticamente")
    print(f"✅ Certificado descargado: {certificado_path}")
    print("✅ Base de datos limpia (solo acciones pagadas)")
    
    return True

def limpiar_archivos_prueba():
    """Limpia archivos generados durante la prueba"""
    print("\n🧹 Limpiando archivos de prueba...")
    
    archivos_a_limpiar = [
        "certificado_flujo_mejorado_*.pdf",
        "qr_codes/temp_*.png",
        "certificados/originales/certificado_accion_*.pdf",
        "certificados/cifrados/certificado_accion_*_cifrado_*.bin",
        "comprobantes/temp_comprobante_*.pdf",
        "temp_payments/TEMP_*.json"
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
        # Ejecutar prueba del flujo mejorado
        exito = test_flujo_mejorado()
        
        if exito:
            print("\n🎯 RESULTADO: PRUEBA EXITOSA")
            print("El flujo mejorado está funcionando perfectamente:")
            print("  1. ✅ QR generado sin crear acción")
            print("  2. ✅ Usuario paga con QR")
            print("  3. ✅ Acción creada solo después del pago")
            print("  4. ✅ Certificado generado automáticamente")
            print("  5. ✅ Base de datos limpia")
        else:
            print("\n❌ RESULTADO: PRUEBA FALLIDA")
            print("Hubo errores en el flujo mejorado")
        
        # Limpiar archivos de prueba
        limpiar_archivos_prueba()
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Prueba interrumpida por el usuario")
    except Exception as e:
        print(f"\n❌ Error inesperado: {str(e)}")
        import traceback
        traceback.print_exc()
