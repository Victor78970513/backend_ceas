#!/usr/bin/env python3
"""
Script para probar el endpoint GET /socios/57/acciones
"""

import requests
import json

def test_endpoint_socio_57():
    print('🔍 PROBANDO ENDPOINT DE ACCIONES POR SOCIO')
    print('=' * 45)
    
    try:
        # Login como admin
        login_data = {'correo_electronico': 'prueba@gmail.com', 'contrasena': '123456'}
        response = requests.post('http://localhost:8000/login', json=login_data)
        
        if response.status_code != 200:
            print(f'❌ Error en login: {response.status_code}')
            return
        
        admin_token = response.json()['access_token']
        headers = {'Authorization': f'Bearer {admin_token}'}
        
        # Probar con socio 57
        print('🎯 Probando GET /socios/57/acciones...')
        response = requests.get('http://localhost:8000/socios/57/acciones', headers=headers)
        print(f'Status: {response.status_code}')
        
        if response.status_code == 200:
            data = response.json()
            print(f'✅ Éxito! Acciones encontradas: {len(data)}')
            
            if data:
                print('\n📋 DETALLE DE ACCIONES:')
                for i, accion in enumerate(data):
                    print(f'\n  Acción {i+1}:')
                    print(f'    ID: {accion.get("id_accion")}')
                    print(f'    Tipo: {accion.get("tipo_accion")}')
                    print(f'    Cantidad: {accion.get("cantidad_acciones")}')
                    print(f'    Total Pago: ${accion.get("total_pago", 0):.2f}')
                    print(f'    Estado: {accion.get("estado_accion")}')
            else:
                print('ℹ️  El socio 57 no tiene acciones registradas')
                
            print(f'\n📄 RESPUESTA COMPLETA:')
            print(json.dumps(data, indent=2, ensure_ascii=False, default=str))
        else:
            print(f'❌ Error: {response.status_code}')
            print(f'Respuesta: {response.text}')
            
            # Intentar obtener más detalles del error
            try:
                error_detail = response.json()
                print(f'Error detallado: {json.dumps(error_detail, indent=2)}')
            except:
                print('No se pudo parsear el error como JSON')
                
    except Exception as e:
        print(f'💥 Error fatal: {str(e)}')
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_endpoint_socio_57()
