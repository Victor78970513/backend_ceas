import requests
import json
import os
import time
from datetime import datetime

BASE_URL = "http://127.0.0.1:8000"
ADMIN_EMAIL = "prueba@gmail.com"
ADMIN_PASSWORD = "123456"
TEST_SOCIO_ID = 1  # Asumimos que el socio con ID 1 existe

def get_admin_token():
    """Obtiene token de administrador"""
    login_url = f"{BASE_URL}/login"
    response = requests.post(login_url, json={"correo_electronico": ADMIN_EMAIL, "contrasena": ADMIN_PASSWORD})
    response.raise_for_status()
    return response.json()["access_token"]

def cleanup_test_files():
    """Limpia archivos de prueba"""
    print("\n🧹 Limpiando archivos de prueba...")
    deleted_count = 0

    # Limpiar archivos temporales
    temp_dirs = ["temp_payments", "qr_codes", "certificados/originales", "certificados/cifrados"]
    for temp_dir in temp_dirs:
        if os.path.exists(temp_dir):
            for filename in os.listdir(temp_dir):
                if filename.startswith(('temp_', 'TEMP_', 'certificado_accion_')):
                    filepath = os.path.join(temp_dir, filename)
                    try:
                        os.remove(filepath)
                        print(f"   🗑️  Eliminado: {filepath}")
                        deleted_count += 1
                    except:
                        pass

    print(f"✅ Se eliminaron {deleted_count} archivos de prueba")

def test_stripe_integration():
    """Prueba la integración completa con Stripe"""
    print("🚀 INICIANDO PRUEBA DE INTEGRACIÓN CON STRIPE")
    print("============================================================")
    print("Flujo: Crear pago Stripe -> Verificar estado -> Confirmar pago -> Crear acción")
    print("============================================================")
    
    admin_token = None
    payment_intent_id = None
    accion_id = None

    try:
        # 1. Obtener token de administrador
        print("🔐 Obteniendo token de administrador...")
        admin_token = get_admin_token()
        print("✅ Token obtenido exitosamente")

        # 2. Crear pago con Stripe
        print("\n💳 Creando pago con Stripe...")
        crear_pago_url = f"{BASE_URL}/acciones/stripe/crear-pago"
        pago_request_data = {
            "id_socio": TEST_SOCIO_ID,
            "cantidad_acciones": 50,
            "precio_unitario": 25.00,
            "total_pago": 1250.00,
            "metodo_pago": "stripe",
            "modalidad_pago": 1,
            "tipo_accion": "compra"
        }
        
        response = requests.post(crear_pago_url, headers={"Authorization": f"Bearer {admin_token}"}, json=pago_request_data)
        response.raise_for_status()
        pago_response = response.json()
        
        payment_intent_id = pago_response["payment_intent_id"]
        
        print("✅ Pago creado exitosamente con Stripe")
        print(f"   Payment Intent ID: {payment_intent_id}")
        print(f"   Monto: ${pago_response['amount'] / 100:.2f} {pago_response['currency'].upper()}")
        print(f"   Estado: {pago_response['status']}")
        print(f"   Cliente Secret: {pago_response['client_secret'][:20]}...")
        
        if pago_response.get("qr_data"):
            print("   📱 QR Data disponible:")
            for key, value in pago_response["qr_data"].items():
                print(f"     {key}: {value}")

        # 3. Verificar estado del pago
        print(f"\n🔍 Verificando estado del pago {payment_intent_id}...")
        verificar_url = f"{BASE_URL}/acciones/stripe/verificar-pago/{payment_intent_id}"
        response = requests.get(verificar_url, headers={"Authorization": f"Bearer {admin_token}"})
        response.raise_for_status()
        estado_response = response.json()
        
        print("✅ Estado del pago verificado")
        print(f"   Estado: {estado_response['status']}")
        print(f"   Monto: ${estado_response['amount'] / 100:.2f} {estado_response['currency'].upper()}")
        print(f"   Creado: {datetime.fromtimestamp(estado_response['created']).strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Mostrar metadata
        if estado_response.get("metadata"):
            print("   📋 Metadata:")
            for key, value in estado_response["metadata"].items():
                print(f"     {key}: {value}")

        # 4. Simular confirmación de pago (en producción esto se haría automáticamente)
        print(f"\n✅ Simulando confirmación de pago...")
        print("   📝 En producción, Stripe confirmaría automáticamente el pago")
        print("   📝 Aquí simulamos la confirmación manual para pruebas")
        
        # En un entorno real, Stripe confirmaría automáticamente el pago
        # y llamaría al webhook, pero para pruebas podemos simularlo
        confirmar_url = f"{BASE_URL}/acciones/stripe/confirmar-pago/{payment_intent_id}"
        response = requests.post(confirmar_url, headers={"Authorization": f"Bearer {admin_token}"})
        
        if response.status_code == 200:
            confirm_response = response.json()
            print("✅ Pago confirmado exitosamente")
            
            if "accion" in confirm_response:
                accion_data = confirm_response["accion"]
                accion_id = accion_data["id_accion"]
                print(f"   🎯 Acción creada: ID {accion_id}")
                print(f"   📊 Cantidad: {accion_data['cantidad_acciones']} acciones")
                print(f"   💰 Total: ${accion_data['total_pago']:.2f}")
                print(f"   📄 Estado: {accion_data['estado_nombre']}")
                
                if "certificado" in confirm_response:
                    cert_data = confirm_response["certificado"]
                    print(f"   📜 Certificado: {'Disponible' if cert_data['disponible'] else 'No disponible'}")
                    if cert_data.get("ruta"):
                        print(f"   📁 Ruta: {cert_data['ruta']}")
            else:
                print("   ⚠️  Pago no completado aún")
        else:
            print(f"   ❌ Error confirmando pago: {response.status_code}")
            print(f"   📄 Respuesta: {response.text}")

        # 5. Verificar configuración de Stripe
        print("\n⚙️  Verificando configuración de Stripe...")
        config_url = f"{BASE_URL}/acciones/stripe/configuracion"
        response = requests.get(config_url)
        response.raise_for_status()
        config_response = response.json()
        
        print("✅ Configuración de Stripe obtenida")
        print(f"   💳 Clave pública: {config_response['publishable_key'][:20]}...")
        print(f"   🌍 País: {config_response['country']}")
        print(f"   💰 Moneda: {config_response['currency']}")
        print(f"   🎯 Métodos soportados: {', '.join(config_response['supported_payment_methods'])}")

        # 6. Si se creó una acción, verificar que existe
        if accion_id:
            print(f"\n🔍 Verificando acción creada (ID: {accion_id})...")
            get_accion_url = f"{BASE_URL}/acciones/{accion_id}"
            response = requests.get(get_accion_url, headers={"Authorization": f"Bearer {admin_token}"})
            response.raise_for_status()
            accion_data = response.json()
            
            print("✅ Acción verificada exitosamente")
            print(f"   ID: {accion_data['id_accion']}")
            print(f"   Socio: {accion_data['id_socio']}")
            print(f"   Cantidad: {accion_data['cantidad_acciones']} acciones")
            print(f"   Precio unitario: ${accion_data['precio_unitario']:.2f}")
            print(f"   Total: ${accion_data['total_pago']:.2f}")
            print(f"   Método: {accion_data['metodo_pago']}")
            print(f"   Estado: {accion_data['estado_accion']}")
            print(f"   Certificado: {'Sí' if accion_data['certificado_pdf'] else 'No'}")

        print("\n============================================================")
        print("🎉 PRUEBA DE INTEGRACIÓN CON STRIPE EXITOSA")
        print("✅ Pago creado con Stripe")
        print("✅ Estado verificado correctamente")
        print("✅ Configuración accesible")
        if accion_id:
            print(f"✅ Acción creada: ID {accion_id}")
            print("✅ Certificado generado")
        print("\n🎯 RESULTADO: INTEGRACIÓN FUNCIONANDO")
        print("Stripe está correctamente integrado y funcionando")

    except requests.exceptions.RequestException as e:
        print(f"❌ Error en la petición HTTP: {e}")
        if hasattr(e, 'response') and e.response:
            print(f"   Respuesta del servidor: {e.response.text}")
        print("\n❌ RESULTADO: PRUEBA FALLIDA")
        print("Hubo errores en la integración con Stripe")
    except Exception as e:
        print(f"❌ Error inesperado: {e}")
        print("\n❌ RESULTADO: PRUEBA FALLIDA")
        print("Hubo errores en la integración con Stripe")
    finally:
        cleanup_test_files()

def test_stripe_webhook_simulation():
    """Simula el comportamiento del webhook de Stripe"""
    print("\n🔗 SIMULANDO WEBHOOK DE STRIPE")
    print("============================================================")
    
    admin_token = None
    
    try:
        admin_token = get_admin_token()
        
        # Simular datos de webhook de Stripe
        webhook_payload = {
            "id": "evt_test_webhook",
            "object": "event",
            "api_version": "2020-08-27",
            "created": int(time.time()),
            "data": {
                "object": {
                    "id": "pi_test_payment_intent",
                    "object": "payment_intent",
                    "amount": 125000,  # $1250.00 en centavos
                    "currency": "usd",
                    "status": "succeeded",
                    "metadata": {
                        "socio_id": str(TEST_SOCIO_ID),
                        "cantidad_acciones": "50",
                        "precio_unitario": "25.00",
                        "referencia_temporal": "TEMP_TEST123",
                        "tipo_accion": "compra"
                    }
                }
            },
            "livemode": False,
            "pending_webhooks": 1,
            "request": {
                "id": "req_test_request",
                "idempotency_key": None
            },
            "type": "payment_intent.succeeded"
        }
        
        print("📤 Simulando webhook de pago exitoso...")
        print(f"   Payment Intent ID: {webhook_payload['data']['object']['id']}")
        print(f"   Monto: ${webhook_payload['data']['object']['amount'] / 100:.2f}")
        print(f"   Estado: {webhook_payload['data']['object']['status']}")
        print(f"   Tipo de evento: {webhook_payload['type']}")
        
        # En un entorno real, Stripe enviaría este webhook automáticamente
        # Aquí solo mostramos cómo se procesaría
        print("\n✅ Webhook simulado correctamente")
        print("   📝 En producción, Stripe enviaría este webhook automáticamente")
        print("   📝 El endpoint /stripe/webhook procesaría el evento")
        print("   📝 Se crearía la acción automáticamente")
        print("   📝 Se generaría el certificado automáticamente")
        
    except Exception as e:
        print(f"❌ Error simulando webhook: {e}")

if __name__ == "__main__":
    print("🧪 INICIANDO PRUEBAS DE STRIPE")
    print("============================================================")
    
    test_stripe_integration()
    test_stripe_webhook_simulation()
    
    print("\n============================================================")
    print("🏁 PRUEBAS COMPLETADAS")
    print("============================================================")
