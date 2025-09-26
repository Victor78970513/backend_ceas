#!/usr/bin/env python3
"""
Test con socio 1 que tiene acciones
"""

from use_cases.socio import SocioUseCase
from infrastructure.socio_repository import SocioRepository

def test_socio_1():
    print('🔍 PROBANDO CON SOCIO 1 (que tiene acciones)')
    print('=' * 45)

    try:
        socio_use_case = SocioUseCase(SocioRepository())
        acciones = socio_use_case.get_acciones(1)
        print(f'✅ Socio 1 - Acciones: {len(acciones)}')
        
        if acciones:
            print('Primera acción:')
            accion = acciones[0]
            print(f'  ID: {accion.get("id_accion")}')
            print(f'  Tipo: {accion.get("tipo_accion")}')
            print(f'  Total Pago: ${accion.get("total_pago", 0):.2f}')
            
    except Exception as e:
        print(f'❌ Error: {str(e)}')
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_socio_1()
