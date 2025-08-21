#!/usr/bin/env python3
"""
Script de prueba para verificar el funcionamiento del Business Intelligence Administrativo
"""

import requests
import json
from datetime import datetime

# Configuración
BASE_URL = "http://localhost:8000"
LOGIN_URL = f"{BASE_URL}/login"

def test_login():
    """Prueba el login para obtener un token válido"""
    print("🔐 Probando login...")
    
    login_data = {
        "correo_electronico": "prueba@gmail.com",
        "contrasena": "123456"
    }
    
    try:
        response = requests.post(LOGIN_URL, json=login_data)
        if response.status_code == 200:
            token = response.json()["access_token"]
            print("✅ Login exitoso")
            return token
        else:
            print(f"❌ Error en login: {response.status_code}")
            print(response.text)
            return None
    except Exception as e:
        print(f"❌ Error de conexión: {str(e)}")
        return None

def test_bi_endpoints(token):
    """Prueba todos los endpoints de BI administrativo"""
    headers = {"Authorization": f"Bearer {token}"}
    
    print("\n🚀 Probando endpoints de BI Administrativo...")
    
    # Lista de endpoints a probar
    endpoints = [
        {
            "name": "Dashboard Completo",
            "url": "/bi/administrativo/dashboard",
            "method": "GET"
        },
        {
            "name": "Métricas Financieras",
            "url": "/bi/administrativo/metricas-financieras",
            "method": "GET"
        },
        {
            "name": "Métricas Administrativas",
            "url": "/bi/administrativo/metricas-administrativas",
            "method": "GET"
        },
        {
            "name": "Top Clubes",
            "url": "/bi/administrativo/top-clubes",
            "method": "GET"
        },
        {
            "name": "Top Socios",
            "url": "/bi/administrativo/top-socios",
            "method": "GET"
        },
        {
            "name": "Distribución Financiera",
            "url": "/bi/administrativo/distribucion-financiera",
            "method": "GET"
        },
        {
            "name": "KPIs Principales",
            "url": "/bi/administrativo/kpis",
            "method": "GET"
        },
        {
            "name": "Tendencias Mensuales",
            "url": "/bi/administrativo/tendencias",
            "method": "GET"
        },
        {
            "name": "Alertas Críticas",
            "url": "/bi/administrativo/alertas",
            "method": "GET"
        },
        {
            "name": "Resumen Rápido",
            "url": "/bi/administrativo/resumen-rapido",
            "method": "GET"
        }
    ]
    
    # Probar cada endpoint
    for endpoint in endpoints:
        print(f"\n📊 Probando: {endpoint['name']}")
        print(f"   URL: {endpoint['url']}")
        
        try:
            if endpoint['method'] == 'GET':
                response = requests.get(f"{BASE_URL}{endpoint['url']}", headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                print(f"   ✅ Status: {response.status_code}")
                
                # Mostrar resumen de la respuesta
                if isinstance(data, dict):
                    if 'periodo' in data:
                        print(f"   📅 Período: {data['periodo']}")
                    if 'metricas_financieras' in data:
                        mf = data['metricas_financieras']
                        print(f"   💰 Balance: ${mf.get('balance_neto', 'N/A')}")
                    if 'metricas_administrativas' in data:
                        ma = data['metricas_administrativas']
                        print(f"   👥 Socios: {ma.get('total_socios', 'N/A')}")
                    if 'alertas_criticas' in data:
                        print(f"   ⚠️  Alertas: {len(data['alertas_criticas'])}")
                elif isinstance(data, list):
                    print(f"   📊 Elementos: {len(data)}")
                
            else:
                print(f"   ❌ Status: {response.status_code}")
                print(f"   Error: {response.text}")
                
        except Exception as e:
            print(f"   ❌ Error: {str(e)}")

def test_filters(token):
    """Prueba los filtros de los endpoints"""
    print("\n🔍 Probando filtros...")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # Probar filtros
    filters = [
        {"mes": 1, "anio": 2025},
        {"mes": 12, "anio": 2024},
        {"club": 1},
        {"mes": 8, "anio": 2025, "club": 2}
    ]
    
    for i, filter_params in enumerate(filters, 1):
        print(f"\n   📋 Filtro {i}: {filter_params}")
        
        try:
            url = f"{BASE_URL}/bi/administrativo/dashboard"
            response = requests.get(url, headers=headers, params=filter_params)
            
            if response.status_code == 200:
                data = response.json()
                print(f"      ✅ Status: {response.status_code}")
                if 'periodo' in data:
                    print(f"      📅 Período: {data['periodo']}")
            else:
                print(f"      ❌ Status: {response.status_code}")
                
        except Exception as e:
            print(f"      ❌ Error: {str(e)}")

def main():
    """Función principal"""
    print("🎯 PRUEBA DEL BUSINESS INTELLIGENCE ADMINISTRATIVO")
    print("=" * 60)
    
    # Probar login
    token = test_login()
    if not token:
        print("❌ No se pudo obtener token. Abortando pruebas.")
        return
    
    # Probar endpoints principales
    test_bi_endpoints(token)
    
    # Probar filtros
    test_filters(token)
    
    print("\n" + "=" * 60)
    print("✅ PRUEBAS COMPLETADAS")
    print("\n📚 Endpoints disponibles:")
    print("   • /bi/administrativo/dashboard - Dashboard completo")
    print("   • /bi/administrativo/metricas-financieras - Métricas financieras")
    print("   • /bi/administrativo/metricas-administrativas - Métricas administrativas")
    print("   • /bi/administrativo/top-clubes - Top clubes")
    print("   • /bi/administrativo/top-socios - Top socios")
    print("   • /bi/administrativo/distribucion-financiera - Distribución por categorías")
    print("   • /bi/administrativo/kpis - KPIs principales")
    print("   • /bi/administrativo/tendencias - Tendencias mensuales")
    print("   • /bi/administrativo/alertas - Alertas críticas")
    print("   • /bi/administrativo/resumen-rapido - Resumen rápido")

if __name__ == "__main__":
    main()
