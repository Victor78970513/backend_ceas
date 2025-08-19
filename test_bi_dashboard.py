#!/usr/bin/env python3
"""
Script para probar el endpoint de dashboard financiero
"""

import requests
import json

def test_bi_dashboard():
    # URL del endpoint
    url = "http://localhost:8000/bi/finanzas-resumen"
    
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
        
        # Ahora probar el endpoint de finanzas-resumen
        print("\n📊 Probando endpoint de finanzas-resumen...")
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        
        # Probar dashboard del período actual
        dashboard_response = requests.get(url, headers=headers)
        
        if dashboard_response.status_code != 200:
            print(f"❌ Error en dashboard: {dashboard_response.status_code}")
            print(f"Respuesta: {dashboard_response.text}")
            return
        
        print("✅ Endpoint de finanzas-resumen funcionando")
        
        # Analizar la respuesta
        dashboard_data = dashboard_response.json()
        print("\n📋 Resumen financiero obtenido:")
        print(f"📅 Período: {dashboard_data.get('periodo', 'N/A')}")
        
        # Métricas generales
        metricas = dashboard_data.get('metricas_generales', {})
        print(f"\n💰 Métricas Generales:")
        print(f"  - Ingresos: Bs. {metricas.get('ingresos', 0)}")
        print(f"  - Egresos: Bs. {metricas.get('egresos', 0)}")
        print(f"  - Balance: Bs. {metricas.get('balance', 0)}")
        print(f"  - Total Movimientos: {metricas.get('movimientos', 0)}")
        
        # Distribución por club
        distribucion_club = dashboard_data.get('distribucion_por_club', {})
        print(f"\n🏢 Distribución por Club:")
        for club, datos in distribucion_club.items():
            print(f"  - {club}:")
            print(f"    * Ingresos: Bs. {datos.get('ingresos', 0)}")
            print(f"    * Egresos: Bs. {datos.get('egresos', 0)}")
            print(f"    * Balance: Bs. {datos.get('balance', 0)}")
        
        # Top categorías
        top_categorias = dashboard_data.get('top_categorias', {})
        print(f"\n🏆 Top Categorías:")
        
        print(f"  📈 Ingresos:")
        for cat in top_categorias.get('ingresos', []):
            print(f"    - {cat.get('categoria', 'N/A')}: Bs. {cat.get('monto', 0)}")
        
        print(f"  📉 Egresos:")
        for cat in top_categorias.get('egresos', []):
            print(f"    - {cat.get('categoria', 'N/A')}: Bs. {cat.get('monto', 0)}")
        
        # Mostrar respuesta completa
        print("\n📝 Respuesta completa del endpoint:")
        print(json.dumps(dashboard_data, indent=2, ensure_ascii=False))
        
        # Probar con parámetros específicos
        print("\n🔍 Probando con parámetros específicos (Agosto 2025)...")
        params = {"mes": 8, "anio": 2025}
        finanzas_especifico = requests.get(url, headers=headers, params=params)
        
        if finanzas_especifico.status_code == 200:
            print("✅ Finanzas-resumen con parámetros funcionando")
            data_especifico = finanzas_especifico.json()
            print(f"📅 Período específico: {data_especifico.get('periodo', 'N/A')}")
        else:
            print(f"❌ Error con parámetros: {finanzas_especifico.status_code}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Error de conexión. ¿Está corriendo el backend?")
    except Exception as e:
        print(f"❌ Error inesperado: {str(e)}")

if __name__ == "__main__":
    test_bi_dashboard()
