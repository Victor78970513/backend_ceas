#!/usr/bin/env python3
"""
Script para crear un usuario de prueba para las pruebas del BI
"""

import requests
import json

# Configuración
BASE_URL = "http://localhost:8000"
REGISTER_URL = f"{BASE_URL}/register"

def create_test_user():
    """Crea un usuario de prueba"""
    print("👤 Creando usuario de prueba...")
    
    user_data = {
        "nombres": "Admin",
        "apellidos": "Test",
        "correo_electronico": "admin@ceas.com",
        "contrasena": "admin123",
        "rol": "ADMIN"
    }
    
    try:
        response = requests.post(REGISTER_URL, json=user_data)
        if response.status_code == 200:
            data = response.json()
            print("✅ Usuario creado exitosamente")
            print(f"   ID: {data.get('id_usuario', 'N/A')}")
            print(f"   Email: {data.get('correo_electronico', 'N/A')}")
            print(f"   Token: {data.get('access_token', 'N/A')[:50]}...")
            return True
        else:
            print(f"❌ Error al crear usuario: {response.status_code}")
            print(response.text)
            return False
    except Exception as e:
        print(f"❌ Error de conexión: {str(e)}")
        return False

def main():
    """Función principal"""
    print("🎯 CREACIÓN DE USUARIO DE PRUEBA")
    print("=" * 40)
    
    success = create_test_user()
    
    if success:
        print("\n✅ Usuario de prueba creado. Ahora puedes ejecutar:")
        print("   python test_bi_administrativo.py")
    else:
        print("\n❌ No se pudo crear el usuario de prueba.")

if __name__ == "__main__":
    main()

