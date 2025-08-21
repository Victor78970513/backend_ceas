#!/usr/bin/env python3
"""
Script completo para probar todos los endpoints de BI
Verifica que funcionen correctamente y que las respuestas sean válidas
"""

import requests
import json
from datetime import datetime

# Configuración
BASE_URL = "http://localhost:8000"
CREDENCIALES = {
    'correo_electronico': 'prueba@gmail.com',
    'contrasena': '123456'
}

def login():
    """Realiza login y retorna el token"""
    try:
        response = requests.post(f"{BASE_URL}/login", json=CREDENCIALES)
        if response.status_code == 200:
            return response.json()['access_token']
        else:
            print(f"❌ Error en login: {response.status_code}")
            print(response.text)
            return None
    except Exception as e:
        print(f"❌ Error de conexión: {e}")
        return None

def test_endpoint(url, name, expected_fields=None, expected_types=None):
    """Prueba un endpoint específico"""
    print(f"\n📊 Probando: {name}")
    print(f"   URL: {url}")
    
    try:
        response = requests.get(f"{BASE_URL}{url}", headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Status: {response.status_code}")
            
            # Verificar estructura básica
            if isinstance(data, dict):
                print(f"   📋 Tipo: Dict con {len(data)} campos")
                print(f"   🔍 Campos: {list(data.keys())}")
                
                # Verificar campos esperados
                if expected_fields:
                    missing_fields = [field for field in expected_fields if field not in data]
                    if missing_fields:
                        print(f"   ⚠️  Campos faltantes: {missing_fields}")
                    else:
                        print(f"   ✅ Todos los campos esperados presentes")
                
                # Verificar tipos de datos
                if expected_types:
                    for field, expected_type in expected_types.items():
                        if field in data:
                            actual_type = type(data[field]).__name__
                            if actual_type == expected_type:
                                print(f"   ✅ {field}: {expected_type}")
                            else:
                                print(f"   ⚠️  {field}: esperado {expected_type}, actual {actual_type}")
                
                # Mostrar resumen de datos
                if 'periodo' in data:
                    print(f"   📅 Período: {data['periodo']}")
                if 'metricas_financieras' in data:
                    mf = data['metricas_financieras']
                    if isinstance(mf, dict):
                        print(f"   💰 Balance: ${mf.get('balance_neto', 'N/A')}")
                if 'metricas_administrativas' in data:
                    ma = data['metricas_administrativas']
                    if isinstance(ma, dict):
                        print(f"   👥 Socios: {ma.get('total_socios', 'N/A')}")
                if 'alertas_criticas' in data:
                    print(f"   ⚠️  Alertas: {len(data['alertas_criticas'])}")
                
                # Verificar datos específicos según el endpoint
                if 'ingresos' in data and 'egresos' in data:
                    print(f"   📊 Ingresos: {len(data['ingresos'])} categorías")
                    print(f"   📊 Egresos: {len(data['egresos'])} categorías")
                    if 'resumen' in data:
                        resumen = data['resumen']
                        print(f"   💰 Total ingresos: ${resumen.get('total_ingresos', 0):,.2f}")
                        print(f"   💸 Total egresos: ${resumen.get('total_egresos', 0):,.2f}")
                        print(f"   📈 Balance: ${resumen.get('balance', 0):,.2f}")
                
                if 'top_clubes' in data:
                    print(f"   🏢 Top clubes: {len(data['top_clubes'])} elementos")
                
                if 'top_socios' in data:
                    print(f"   👥 Top socios: {len(data['top_socios'])} elementos")
                
                if 'distribucion_ingresos' in data:
                    print(f"   📊 Distribución ingresos: {len(data['distribucion_ingresos'])} elementos")
                
                if 'distribucion_egresos' in data:
                    print(f"   📊 Distribución egresos: {len(data['distribucion_egresos'])} elementos")
                
                if 'kpis_principales' in data:
                    print(f"   📈 KPIs: {len(data['kpis_principales'])} elementos")
                
                if 'tendencias_mensuales' in data:
                    print(f"   📅 Tendencias: {len(data['tendencias_mensuales'])} meses")
                
                if 'alertas_criticas' in data:
                    print(f"   ⚠️  Alertas: {len(data['alertas_criticas'])} elementos")
                
            elif isinstance(data, list):
                print(f"   📋 Tipo: Lista con {len(data)} elementos")
                if data:
                    print(f"   🔍 Primer elemento: {list(data[0].keys()) if isinstance(data[0], dict) else 'No es dict'}")
            
            return True
            
        else:
            print(f"   ❌ Status: {response.status_code}")
            print(f"   Error: {response.text}")
            return False
            
    except Exception as e:
        print(f"   ❌ Error: {str(e)}")
        return False

def test_bi_administrativo():
    """Prueba todos los endpoints de BI Administrativo"""
    print("\n🏢 TESTING BI ADMINISTRATIVO")
    print("=" * 50)
    
    endpoints = [
        {
            "url": "/bi/administrativo/dashboard",
            "name": "Dashboard Completo",
            "expected_fields": ["periodo", "metricas_financieras", "metricas_administrativas", "top_clubes", "top_socios", "distribucion_ingresos", "distribucion_egresos", "kpis_principales", "tendencias_mensuales", "alertas_criticas"],
            "expected_types": {"periodo": "str", "metricas_financieras": "dict", "metricas_administrativas": "dict"}
        },
        {
            "url": "/bi/administrativo/metricas-financieras",
            "name": "Métricas Financieras",
            "expected_fields": ["ingresos_totales", "egresos_totales", "balance_neto", "margen_rentabilidad", "flujo_caja"],
            "expected_types": {"ingresos_totales": "float", "egresos_totales": "float", "balance_neto": "float"}
        },
        {
            "url": "/bi/administrativo/metricas-administrativas",
            "name": "Métricas Administrativas",
            "expected_fields": ["total_socios", "socios_activos", "tasa_retencion", "acciones_totales"],
            "expected_types": {"total_socios": "int", "socios_activos": "int", "tasa_retencion": "float"}
        },
        {
            "url": "/bi/administrativo/top-clubes",
            "name": "Top Clubes",
            "expected_fields": ["id_club", "nombre_club", "rendimiento_financiero", "rendimiento_operativo"],
            "expected_types": {"id_club": "int", "nombre_club": "str"}
        },
        {
            "url": "/bi/administrativo/top-socios",
            "name": "Top Socios",
            "expected_fields": ["id_socio", "nombre_completo", "nombre_club", "acciones_compradas", "total_invertido"],
            "expected_types": {"id_socio": "int", "nombre_completo": "str", "nombre_club": "str"}
        },
        {
            "url": "/bi/administrativo/distribucion-financiera",
            "name": "Distribución Financiera",
            "expected_fields": ["ingresos", "egresos", "resumen"],
            "expected_types": {"ingresos": "list", "egresos": "list", "resumen": "dict"}
        },
        {
            "url": "/bi/administrativo/kpis",
            "name": "KPIs Principales",
            "expected_fields": ["conversion", "rentabilidad", "eficiencia"],
            "expected_types": {"conversion": "float", "rentabilidad": "float", "eficiencia": "float"}
        },
        {
            "url": "/bi/administrativo/tendencias",
            "name": "Tendencias Mensuales",
            "expected_fields": ["tendencias_ingresos", "tendencias_egresos", "tendencias_socios"],
            "expected_types": {"tendencias_ingresos": "dict", "tendencias_egresos": "dict"}
        },
        {
            "url": "/bi/administrativo/alertas",
            "name": "Alertas Críticas",
            "expected_fields": ["alertas"],
            "expected_types": {"alertas": "list"}
        },
        {
            "url": "/bi/administrativo/resumen-rapido",
            "name": "Resumen Rápido",
            "expected_fields": ["periodo_actual", "balance_neto", "total_socios", "estado_general"],
            "expected_types": {"periodo_actual": "str", "balance_neto": "float", "total_socios": "int"}
        }
    ]
    
    resultados = []
    for endpoint in endpoints:
        resultado = test_endpoint(
            endpoint["url"], 
            endpoint["name"],
            endpoint.get("expected_fields"),
            endpoint.get("expected_types")
        )
        resultados.append(resultado)
    
    return resultados

def test_bi_personal():
    """Prueba todos los endpoints de BI Personal"""
    print("\n👷 TESTING BI PERSONAL")
    print("=" * 50)
    
    endpoints = [
        {
            "url": "/bi/personal/dashboard",
            "name": "Dashboard Personal",
            "expected_fields": ["periodo", "metricas_generales", "metricas_asistencia", "top_empleados_asistencia", "asistencia_por_departamento", "tendencias_mensuales"],
            "expected_types": {"periodo": "str", "metricas_generales": "dict", "metricas_asistencia": "dict"}
        },
        {
            "url": "/bi/personal/metricas-generales",
            "name": "Métricas Generales Personal",
            "expected_fields": ["total_empleados", "empleados_activos", "promedio_salario", "departamentos"],
            "expected_types": {"total_empleados": "int", "empleados_activos": "int", "promedio_salario": "float"}
        },
        {
            "url": "/bi/personal/metricas-asistencia",
            "name": "Métricas de Asistencia",
            "expected_fields": ["tasa_asistencia", "promedio_horas", "tardanzas", "ausencias"],
            "expected_types": {"tasa_asistencia": "float", "promedio_horas": "float"}
        },
        {
            "url": "/bi/personal/top-empleados",
            "name": "Top Empleados Asistencia",
            "expected_fields": ["id_personal", "nombre_empleado", "departamento", "tasa_asistencia", "horas_trabajadas"],
            "expected_types": {"id_personal": "int", "nombre_empleado": "str", "departamento": "str"}
        },
        {
            "url": "/bi/personal/asistencia-departamento",
            "name": "Asistencia por Departamento",
            "expected_fields": ["departamento", "empleados", "tasa_asistencia", "promedio_horas"],
            "expected_types": {"departamento": "str", "empleados": "int", "tasa_asistencia": "float"}
        },
        {
            "url": "/bi/personal/tendencias-mensuales",
            "name": "Tendencias Mensuales Personal",
            "expected_fields": ["tendencias_asistencia", "tendencias_salarios", "tendencias_empleados"],
            "expected_types": {"tendencias_asistencia": "dict", "tendencias_salarios": "dict"}
        }
    ]
    
    resultados = []
    for endpoint in endpoints:
        resultado = test_endpoint(
            endpoint["url"], 
            endpoint["name"],
            endpoint.get("expected_fields"),
            endpoint.get("expected_types")
        )
        resultados.append(resultado)
    
    return resultados

def test_bi_finanzas():
    """Prueba todos los endpoints de BI Finanzas"""
    print("\n💰 TESTING BI FINANZAS")
    print("=" * 50)
    
    endpoints = [
        {
            "url": "/bi/finanzas-resumen",
            "name": "Resumen Financiero",
            "expected_fields": ["periodo", "metricas_generales", "distribucion_por_club", "top_categorias"],
            "expected_types": {"periodo": "str", "metricas_generales": "dict", "distribucion_por_club": "dict"}
        }
    ]
    
    resultados = []
    for endpoint in endpoints:
        resultado = test_endpoint(
            endpoint["url"], 
            endpoint["name"],
            endpoint.get("expected_fields"),
            endpoint.get("expected_types")
        )
        resultados.append(resultado)
    
    return resultados

def test_bi_avanzado():
    """Prueba endpoints de BI Avanzado"""
    print("\n🚀 TESTING BI AVANZADO")
    print("=" * 50)
    
    endpoints = [
        {
            "url": "/bi/avanzado/dashboard/ejecutivo",
            "name": "Dashboard Ejecutivo",
            "expected_fields": ["tipo", "periodo", "kpis_estrategicos", "resumen_financiero", "tendencias_clave", "alertas_criticas", "proyecciones"],
            "expected_types": {"tipo": "str", "periodo": "str", "kpis_estrategicos": "list"}
        },
        {
            "url": "/bi/avanzado/dashboard/operativo",
            "name": "Dashboard Operativo",
            "expected_fields": ["tipo", "timestamp", "metricas_operativas", "alertas_tiempo_real", "indicadores_proceso", "estado_sistema", "tareas_pendientes"],
            "expected_types": {"tipo": "str", "timestamp": "str", "metricas_operativas": "dict"}
        },
        {
            "url": "/bi/avanzado/dashboard/financiero",
            "name": "Dashboard Financiero",
            "expected_fields": ["tipo", "timestamp", "metricas_financieras", "distribucion_ingresos", "distribucion_egresos", "flujo_caja", "presupuestos", "analisis_costos", "proyecciones_financieras"],
            "expected_types": {"tipo": "str", "timestamp": "str", "metricas_financieras": "dict"}
        },
        {
            "url": "/bi/avanzado/dashboard/ventas",
            "name": "Dashboard de Ventas",
            "expected_fields": ["tipo", "timestamp", "pipeline_ventas", "conversiones", "metas", "top_socios", "metricas_administrativas", "analisis_tendencias", "oportunidades"],
            "expected_types": {"tipo": "str", "timestamp": "str", "top_socios": "list"}
        }
    ]
    
    resultados = []
    for endpoint in endpoints:
        resultado = test_endpoint(
            endpoint["url"], 
            endpoint["name"],
            endpoint.get("expected_fields"),
            endpoint.get("expected_types")
        )
        resultados.append(resultado)
    
    return resultados

def main():
    """Función principal"""
    print("🔍 VERIFICACIÓN COMPLETA DEL SISTEMA DE BUSINESS INTELLIGENCE")
    print("=" * 80)
    
    global headers
    
    # Login
    token = login()
    if not token:
        print("❌ No se pudo obtener el token. Abortando pruebas.")
        return
    
    headers = {"Authorization": f"Bearer {token}"}
    print("✅ Login exitoso, iniciando pruebas...")
    
    # Ejecutar todas las pruebas
    resultados_admin = test_bi_administrativo()
    resultados_personal = test_bi_personal()
    resultados_finanzas = test_bi_finanzas()
    resultados_avanzado = test_bi_avanzado()
    
    # Resumen final
    print("\n" + "=" * 80)
    print("📊 RESUMEN FINAL DE PRUEBAS")
    print("=" * 80)
    
    total_endpoints = len(resultados_admin) + len(resultados_personal) + len(resultados_finanzas) + len(resultados_avanzado)
    total_exitosos = sum(resultados_admin) + sum(resultados_personal) + sum(resultados_finanzas) + sum(resultados_avanzado)
    
    print(f"🏢 BI Administrativo: {sum(resultados_admin)}/{len(resultados_admin)} endpoints funcionando")
    print(f"👷 BI Personal: {sum(resultados_personal)}/{len(resultados_personal)} endpoints funcionando")
    print(f"💰 BI Finanzas: {sum(resultados_finanzas)}/{len(resultados_finanzas)} endpoints funcionando")
    print(f"🚀 BI Avanzado: {sum(resultados_avanzado)}/{len(resultados_avanzado)} endpoints funcionando")
    
    print(f"\n📈 TOTAL: {total_exitosos}/{total_endpoints} endpoints funcionando correctamente")
    
    if total_exitosos == total_endpoints:
        print("🎉 ¡TODOS LOS ENDPOINTS DE BI ESTÁN FUNCIONANDO PERFECTAMENTE!")
    elif total_exitosos >= total_endpoints * 0.8:
        print("✅ La mayoría de endpoints funcionan correctamente")
    else:
        print("⚠️  Hay varios endpoints que requieren atención")
    
    print(f"\n⏰ Pruebas completadas: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    main()
