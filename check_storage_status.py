#!/usr/bin/env python3
"""
Script para verificar el estado del almacenamiento de certificados
"""

import os
from datetime import datetime

def check_storage_status():
    """Verifica el estado del almacenamiento local y Google Drive"""
    
    print("📊 ESTADO DEL ALMACENAMIENTO DE CERTIFICADOS")
    print("=" * 50)
    
    # Verificar almacenamiento local
    print("📁 ALMACENAMIENTO LOCAL:")
    certificados_dir = "certificados"
    
    if os.path.exists(certificados_dir):
        originales_dir = os.path.join(certificados_dir, "originales")
        cifrados_dir = os.path.join(certificados_dir, "cifrados")
        
        if os.path.exists(originales_dir):
            originales_count = len([f for f in os.listdir(originales_dir) if f.endswith('.pdf')])
            print(f"   ✅ Certificados originales: {originales_count} archivos")
        else:
            print(f"   ❌ Carpeta de originales no existe")
        
        if os.path.exists(cifrados_dir):
            cifrados_count = len([f for f in os.listdir(cifrados_dir) if f.endswith('.bin')])
            print(f"   ✅ Certificados cifrados: {cifrados_count} archivos")
        else:
            print(f"   ❌ Carpeta de cifrados no existe")
    else:
        print(f"   ❌ Carpeta de certificados no existe")
    
    print()
    
    # Verificar Google Drive
    print("☁️ GOOGLE DRIVE:")
    credentials_file = "credentials/google_drive_credentials.json"
    
    if os.path.exists(credentials_file):
        print(f"   ✅ Archivo de credenciales encontrado")
        
        try:
            from infrastructure.google_drive_service import google_drive_service
            
            if google_drive_service.is_available():
                print(f"   ✅ Servicio de Google Drive disponible")
                
                # Listar archivos en Google Drive
                try:
                    originales_gd = google_drive_service.list_certificates('originales')
                    cifrados_gd = google_drive_service.list_certificates('cifrados')
                    
                    print(f"   📄 Certificados originales en Google Drive: {len(originales_gd)}")
                    print(f"   🔐 Certificados cifrados en Google Drive: {len(cifrados_gd)}")
                    
                    if originales_gd:
                        print(f"   📋 Últimos archivos originales:")
                        for file in originales_gd[-3:]:
                            print(f"      - {file['name']}")
                    
                except Exception as e:
                    print(f"   ⚠️ Error listando archivos de Google Drive: {e}")
                    
            else:
                print(f"   ❌ Servicio de Google Drive no disponible")
                
        except ImportError:
            print(f"   ❌ Dependencias de Google Drive no instaladas")
            print(f"   💡 Ejecuta: python install_google_drive.py")
            
    else:
        print(f"   ❌ Archivo de credenciales no encontrado")
        print(f"   💡 Configura Google Drive siguiendo: credentials/README_GOOGLE_DRIVE.md")
    
    print()
    
    # Verificar pagos temporales
    print("⏰ PAGOS TEMPORALES:")
    temp_dir = "temp_payments"
    
    if os.path.exists(temp_dir):
        temp_count = len([f for f in os.listdir(temp_dir) if f.endswith('.json')])
        print(f"   📄 Pagos temporales activos: {temp_count}")
        
        if temp_count > 0:
            print(f"   📋 Últimos pagos:")
            files = sorted(os.listdir(temp_dir))[-3:]
            for file in files:
                if file.endswith('.json'):
                    print(f"      - {file}")
    else:
        print(f"   ✅ No hay pagos temporales (normal)")
    
    print()
    print("🎯 RESUMEN:")
    
    # Determinar método de almacenamiento principal
    if os.path.exists(credentials_file):
        try:
            from infrastructure.google_drive_service import google_drive_service
            if google_drive_service.is_available():
                print("   ✅ Google Drive configurado y disponible")
                print("   📁 Almacenamiento local como respaldo")
            else:
                print("   📁 Solo almacenamiento local disponible")
        except:
            print("   📁 Solo almacenamiento local disponible")
    else:
        print("   📁 Solo almacenamiento local disponible")

if __name__ == "__main__":
    check_storage_status()
