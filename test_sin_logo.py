#!/usr/bin/env python3
"""
Script para probar el PDF sin logo
"""

from infrastructure.pdf_service import PDFService

def test_sin_logo():
    """Prueba el PDF sin logo"""
    try:
        print("📄 Probando PDF sin logo...")
        
        # Crear instancia del servicio
        pdf_service = PDFService()
        
        # Datos de prueba
        accion_data = {
            'id_accion': 6,
            'id_socio': 1,
            'tipo_accion': 'FUNDADOR',
            'fecha_emision_certificado': '2023-09-07T00:00:00'
        }
        
        socio_data = {
            'socio_titular': 'Juan Ernesto Sáenz Loza',
            'ci_nit': '4299168'
        }
        
        modalidad_data = {
            'precio_renovacion': 10000.0
        }
        
        # Generar PDF sin logo
        print("\n📄 Generando PDF sin logo...")
        pdf_content = pdf_service.generar_certificado_accion(accion_data, socio_data, modalidad_data)
        
        # Verificar que se generó contenido
        if pdf_content and len(pdf_content) > 0:
            print(f"✅ PDF generado exitosamente!")
            print(f"📊 Tamaño del PDF: {len(pdf_content)} bytes")
            
            # Guardar PDF de prueba
            with open('certificado_sin_logo.pdf', 'wb') as f:
                f.write(pdf_content)
            print("💾 PDF guardado como 'certificado_sin_logo.pdf'")
            print("\n🎯 El PDF ahora incluye SOLO:")
            print("   - Título 'CERTIFICADO ACCIONARIO'")
            print("   - Información de la acción")
            print("   - Nombre del socio")
            print("   - Monto en bolivianos")
            print("   - Firmas")
            print("   - Sin logo (UI limpia y funcional)")
            
        else:
            print("❌ Error: PDF vacío o no generado")
            
    except Exception as e:
        print(f"❌ Error durante la prueba: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_sin_logo()

