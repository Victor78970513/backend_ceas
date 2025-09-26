#!/usr/bin/env python3
"""
Test directo de la lógica del endpoint
"""

from use_cases.socio import SocioUseCase
from infrastructure.socio_repository import SocioRepository

def test_logic_direct():
    print('🔍 PROBANDO LÓGICA DIRECTA')
    print('=' * 30)

    try:
        socio_use_case = SocioUseCase(SocioRepository())
        print('✅ SocioUseCase creado correctamente')
        
        # Probar obtener acciones del socio 57
        acciones = socio_use_case.get_acciones(57)
        print(f'✅ Acciones obtenidas: {len(acciones)} acciones')
        
        if acciones:
            print('Primera acción:')
            accion = acciones[0]
            print(f'  ID: {accion.get("id_accion")}')
            print(f'  Tipo: {accion.get("tipo_accion")}')
            print(f'  Cantidad: {accion.get("cantidad_acciones")}')
            print(f'  Total Pago: ${accion.get("total_pago", 0):.2f}')
        else:
            print('ℹ️  No hay acciones para este socio')
        
    except Exception as e:
        print(f'❌ Error: {str(e)}')
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_logic_direct()
