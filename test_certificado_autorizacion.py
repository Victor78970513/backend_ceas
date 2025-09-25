#!/usr/bin/env python3
"""
Script para probar la autorización de certificados
"""

import requests
import json
import os

BASE_URL = "http://localhost:8000"

def login(email, password):
    """Hacer login y obtener token"""
    login_data = {
        "correo_electronico": email,
        "contrasena": password
    }
    
    # Usar JSON para el login
    response = requests.post(f"{BASE_URL}/login", json=login_data)
    if response.status_code == 200:
        return response.json()["access_token"]
    else:
        raise Exception(f"Error en login: {response.status_code} - {response.text}")

def descargar_certificado(filename, token):
    """Descargar certificado con token de autorización"""
    headers = {
        "Authorization": f"Bearer {token}"
    }
    
    response = requests.get(f"{BASE_URL}/acciones/certificados/{filename}", headers=headers)
    
    return response

def main():
    print("🔐 PRUEBA DE AUTORIZACIÓN DE CERTIFICADOS")
    print("=" * 50)
    
    # Usar el certificado más reciente
    filename = "certificado_accion_29_1_20250924_221218.pdf"
    
    print(f"📄 Probando certificado: {filename}")
    print(f"📋 Propietario: Socio ID 1")
    print()
    
    # 1. Probar con admin (debería ver PDF original)
    print("1️⃣ PROBANDO CON ADMIN...")
    try:
        admin_token = login("prueba@gmail.com", "admin123")
        response = descargar_certificado(filename, admin_token)
        
        print(f"   Status: {response.status_code}")
        print(f"   Content-Type: {response.headers.get('Content-Type', 'N/A')}")
        print(f"   Content-Length: {response.headers.get('Content-Length', 'N/A')}")
        
        if response.status_code == 200:
            # Guardar archivo
            with open("certificado_admin.pdf", "wb") as f:
                f.write(response.content)
            print("   ✅ Certificado descargado como: certificado_admin.pdf")
            
            # Verificar si es PDF legible
            if response.content.startswith(b'%PDF'):
                print("   📄 Tipo: PDF original (legible)")
            else:
                print("   🔒 Tipo: Archivo cifrado (binario)")
        else:
            print(f"   ❌ Error: {response.text}")
            
    except Exception as e:
        print(f"   ❌ Error: {str(e)}")
    
    print()
    
    # 2. Probar con socio propietario (debería ver PDF original)
    print("2️⃣ PROBANDO CON SOCIO PROPIETARIO (ID 1)...")
    try:
        # Usar el primer socio creado (ID 1)
        socio_token = login("socio@gmail.com", "123456")  # CI del socio
        response = descargar_certificado(filename, socio_token)
        
        print(f"   Status: {response.status_code}")
        print(f"   Content-Type: {response.headers.get('Content-Type', 'N/A')}")
        print(f"   Content-Length: {response.headers.get('Content-Length', 'N/A')}")
        
        if response.status_code == 200:
            # Guardar archivo
            with open("certificado_propietario.pdf", "wb") as f:
                f.write(response.content)
            print("   ✅ Certificado descargado como: certificado_propietario.pdf")
            
            # Verificar si es PDF legible
            if response.content.startswith(b'%PDF'):
                print("   📄 Tipo: PDF original (legible)")
            else:
                print("   🔒 Tipo: Archivo cifrado (binario)")
        else:
            print(f"   ❌ Error: {response.text}")
            
    except Exception as e:
        print(f"   ❌ Error: {str(e)}")
    
    print()
    
    # 3. Probar con socio NO propietario (debería ver PDF cifrado)
    print("3️⃣ PROBANDO CON SOCIO NO PROPIETARIO (ID 2)...")
    try:
        # Usar otro socio (ID 2)
        socio_token = login("luis.moreno1@gmail.com", "234567")  # CI del socio 2
        response = descargar_certificado(filename, socio_token)
        
        print(f"   Status: {response.status_code}")
        print(f"   Content-Type: {response.headers.get('Content-Type', 'N/A')}")
        print(f"   Content-Length: {response.headers.get('Content-Length', 'N/A')}")
        
        if response.status_code == 200:
            # Guardar archivo
            with open("certificado_no_propietario.bin", "wb") as f:
                f.write(response.content)
            print("   ✅ Certificado descargado como: certificado_no_propietario.bin")
            
            # Verificar si es PDF legible
            if response.content.startswith(b'%PDF'):
                print("   📄 Tipo: PDF original (legible)")
            else:
                print("   🔒 Tipo: Archivo cifrado (binario)")
        else:
            print(f"   ❌ Error: {response.text}")
            
    except Exception as e:
        print(f"   ❌ Error: {str(e)}")
    
    print()
    
    # 4. Probar sin token (debería fallar)
    print("4️⃣ PROBANDO SIN TOKEN...")
    try:
        response = requests.get(f"{BASE_URL}/acciones/certificados/{filename}")
        
        print(f"   Status: {response.status_code}")
        if response.status_code == 401:
            print("   ✅ Correctamente rechazado (sin autorización)")
        else:
            print(f"   ⚠️  Respuesta inesperada: {response.text}")
            
    except Exception as e:
        print(f"   ❌ Error: {str(e)}")
    
    print()
    print("🎉 PRUEBA COMPLETADA")
    print("=" * 50)

if __name__ == "__main__":
    main()
