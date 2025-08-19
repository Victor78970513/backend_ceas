#!/usr/bin/env python3
"""
Script para probar el diseño completo del PDF
"""

from infrastructure.pdf_service import PDFService

def test_diseno_completo():
    """Prueba la generación del PDF con diseño completo"""
    try:
        print("🎨 Probando diseño completo del PDF...")
        
        # Crear instancia del servicio
        pdf_service = PDFService()
        
        # Datos de prueba (como en la imagen)
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
        
        # Generar PDF con diseño completo
        print("📄 Generando PDF con diseño completo...")
        pdf_content = pdf_service.generar_certificado_accion(accion_data, socio_data, modalidad_data)
        
        # Verificar que se generó contenido
        if pdf_content and len(pdf_content) > 0:
            print(f"✅ PDF generado exitosamente!")
            print(f"📊 Tamaño: {len(pdf_content)} bytes")
            
            # Guardar PDF de prueba
            with open('certificado_diseno_completo.pdf', 'wb') as f:
                f.write(pdf_content)
            print("💾 PDF guardado como 'certificado_diseno_completo.pdf'")
            print("🎯 Verifica que incluya:")
            print("   - Logo CEAS en esquina inferior izquierda")
            print("   - QR Code en esquina superior derecha")
            print("   - Marca de agua del caballo")
            print("   - Elementos decorativos en la parte inferior")
            
        else:
            print("❌ Error: PDF vacío o no generado")
            
    except Exception as e:
        print(f"❌ Error durante la prueba: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_diseno_completo()

