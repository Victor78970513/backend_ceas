#!/usr/bin/env python3
"""
Script para probar el endpoint de finanzas y verificar la respuesta
"""

import requests
import json
from datetime import datetime

def test_finanzas_endpoint():
    # URL del endpoint
    url = "http://localhost:8000/finanzas/movimientos/"
    
    # Primero necesitamos obtener un token (login)
    login_url = "http://localhost:8000/login"
    login_data = {
        "correo_electronico": "test@ceas.com",
        "contrasena": "test123"
    }
    
    try:
        # Hacer login para obtener token
        print("🔐 Haciendo login...")
        login_response = requests.post(login_url, json=login_data)
        
        if login_response.status_code != 200:
            print(f"❌ Error en login: {login_response.status_code}")
            print(login_response.text)
            return
        
        login_result = login_response.json()
        token = login_result["access_token"]
        print("✅ Login exitoso")
        
        # Ahora probar el endpoint de finanzas
        print("\n📊 Probando endpoint de finanzas...")
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        
        finanzas_response = requests.get(url, headers=headers)
        
        if finanzas_response.status_code != 200:
            print(f"❌ Error en finanzas: {finanzas_response.status_code}")
            print(finanzas_response.text)
            return
        
        print("✅ Endpoint de finanzas funcionando")
        
        # Analizar la respuesta
        finanzas_data = finanzas_response.json()
        print(f"\n📋 Total de movimientos: {len(finanzas_data)}")
        
        # Verificar campos en el primer movimiento
        if finanzas_data:
            primer_movimiento = finanzas_data[0]
            print("\n🔍 Campos disponibles en el primer movimiento:")
            
            campos_requeridos = [
                "id_movimiento", "descripcion", "tipo_movimiento", 
                "monto", "estado", "fecha"
            ]
            
            campos_criticos = [
                "nombre_club", "categoria"
            ]
            
            campos_importantes = [
                "nombre_socio", "nombre_proveedor", "numero_comprobante"
            ]
            
            # Verificar campos requeridos
            print("\n✅ Campos requeridos:")
            for campo in campos_requeridos:
                valor = primer_movimiento.get(campo, "NO EXISTE")
                print(f"  - {campo}: {valor}")
            
            # Verificar campos críticos
            print("\n🔴 Campos críticos:")
            for campo in campos_criticos:
                valor = primer_movimiento.get(campo, "NO EXISTE")
                status = "✅" if valor != "NO EXISTE" else "❌"
                print(f"  {status} {campo}: {valor}")
            
            # Verificar campos importantes
            print("\n🟡 Campos importantes:")
            for campo in campos_importantes:
                valor = primer_movimiento.get(campo, "NO EXISTE")
                status = "✅" if valor != "NO EXISTE" else "❌"
                print(f"  {status} {campo}: {valor}")
            
            # Mostrar ejemplo completo del primer movimiento
            print("\n📝 Ejemplo completo del primer movimiento:")
            print(json.dumps(primer_movimiento, indent=2, ensure_ascii=False))
            
        else:
            print("⚠️ No hay movimientos financieros para mostrar")
            
    except requests.exceptions.ConnectionError:
        print("❌ Error de conexión. ¿Está corriendo el backend?")
    except Exception as e:
        print(f"❌ Error inesperado: {str(e)}")

if __name__ == "__main__":
    test_finanzas_endpoint()
