#!/usr/bin/env python3
"""
Script para probar el endpoint con la versión simplificada
"""

import requests
import json

def test_endpoint_simplificado():
    """Prueba el endpoint con la versión simplificada"""
    
    base_url = "http://localhost:8000"
    
    # 1. Hacer login para obtener token
    print("🔐 Haciendo login...")
    login_data = {
        "correo_electronico": "prueba@gmail.com",
        "contrasena": "123456"
    }
    
    try:
        login_response = requests.post(f"{base_url}/login", json=login_data)
        if login_response.status_code == 200:
            token = login_response.json()["access_token"]
            print("✅ Login exitoso")
            print(f"🔑 Token: {token[:20]}...")
        else:
            print(f"❌ Error en login: {login_response.status_code}")
            print(f"Respuesta: {login_response.text}")
            return
    except Exception as e:
        print(f"❌ Error de conexión: {str(e)}")
        return
    
    # 2. Probar endpoint de generación de certificado versión simplificada
    print("\n📄 Probando endpoint versión simplificada...")
    
    headers = {
        "Authorization": f"Bearer {token}"
    }
    
    try:
        # Probar con acción ID 2
        response = requests.post(
            f"{base_url}/acciones/2/generar-certificado",
            headers=headers
        )
        
        print(f"📊 Status Code: {response.status_code}")
        print(f"📋 Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            print("✅ Certificado generado exitosamente!")
            print(f"📄 Tamaño del PDF: {len(response.content)} bytes")
            print("\n🎯 El PDF ahora incluye SOLO:")
            print("   - Título 'CERTIFICADO ACCIONARIO'")
            print("   - Información de la acción")
            print("   - Nombre del socio")
            print("   - Monto en bolivianos")
            print("   - Firmas")
            print("   - Logo de CEAS (sin QR, marca de agua, etc.)")
            print("   - Versión simple y limpia")
            print("   - Listo para defender con el presidente")
            
            # Guardar PDF
            with open('certificado_endpoint_simplificado.pdf', 'wb') as f:
                f.write(response.content)
            print("💾 PDF guardado como 'certificado_endpoint_simplificado.pdf'")
            
        else:
            print(f"❌ Error: {response.text}")
            
    except Exception as e:
        print(f"❌ Error durante la prueba: {str(e)}")

if __name__ == "__main__":
    test_endpoint_simplificado()

