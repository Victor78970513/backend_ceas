import os
import json
from datetime import datetime
from typing import Dict, Any, Optional
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64
import logging
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors

# Almacenamiento local únicamente

class CertificateService:
    def __init__(self):
        self.certificados_dir = "certificados"
        self.originales_dir = os.path.join(self.certificados_dir, "originales")
        self.cifrados_dir = os.path.join(self.certificados_dir, "cifrados")
        
        # Crear directorios si no existen
        os.makedirs(self.originales_dir, exist_ok=True)
        os.makedirs(self.cifrados_dir, exist_ok=True)
    
    def generar_certificado_pdf(self, accion_data: Dict[str, Any]) -> str:
        """
        Genera certificado PDF para una acción usando la plantilla de CEAS
        """
        try:
            from infrastructure.socio_repository import SocioRepository
            from infrastructure.pdf_service import PDFService
            
            # Crear nombre del archivo
            id_accion = accion_data.get('id_accion')
            id_socio = accion_data.get('id_socio')
            fecha_actual = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"certificado_accion_{id_accion}_{id_socio}_{fecha_actual}.pdf"
            filepath = os.path.join(self.originales_dir, filename)
            
            # Obtener datos del socio
            socio_repository = SocioRepository()
            socio = socio_repository.get_socio(id_socio)
            
            if not socio:
                raise Exception(f"Socio con ID {id_socio} no encontrado")
            
            # Preparar datos para el PDF
            accion_data_formatted = {
                'id_accion': id_accion,
                'id_socio': id_socio,
                'tipo_accion': accion_data.get('tipo_accion', 'compra'),
                'fecha_emision_certificado': datetime.now().isoformat()
            }
            
            socio_data = {
                'nombre': socio.nombres,
                'apellido': socio.apellidos,
                'ci_nit': socio.ci_nit
            }
            
            modalidad_data = {
                'precio_renovacion': accion_data.get('total_pago', 0.00)
            }
            
            # Generar PDF usando el servicio con plantilla
            pdf_service = PDFService()
            pdf_result = pdf_service.generar_certificado_accion(
                accion_data_formatted, socio_data, modalidad_data
            )
            
            # El servicio retorna un diccionario con el PDF cifrado
            pdf_content = pdf_result['pdf_cifrado']
            
            # Guardar el PDF generado
            with open(filepath, 'wb') as f:
                f.write(pdf_content)
            
            logging.info(f"Certificado PDF generado exitosamente usando plantilla CEAS: {filepath}")
            return filepath
            
        except Exception as e:
            logging.error(f"Error generando certificado PDF: {str(e)}")
            raise Exception(f"Error generando certificado: {str(e)}")
    
    def cifrar_certificado(self, archivo_path: str, usuario_id: int) -> str:
        """
        Cifra un certificado usando el ID del usuario como clave
        """
        try:
            # Leer el archivo original
            with open(archivo_path, 'rb') as file:
                file_data = file.read()
            
            # Generar clave basada en el ID del usuario
            password = str(usuario_id).encode()
            salt = b'ceas_certificate_salt_2024'  # Salt fijo para consistencia
            
            # Derivar clave usando PBKDF2
            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=32,
                salt=salt,
                iterations=100000,
            )
            key = base64.urlsafe_b64encode(kdf.derive(password))
            
            # Cifrar el archivo
            fernet = Fernet(key)
            encrypted_data = fernet.encrypt(file_data)
            
            # Crear nombre del archivo cifrado
            base_name = os.path.basename(archivo_path)
            name_without_ext = os.path.splitext(base_name)[0]
            encrypted_filename = f"{name_without_ext}_cifrado_{usuario_id}.bin"
            encrypted_path = os.path.join(self.cifrados_dir, encrypted_filename)
            
            # Guardar archivo cifrado
            with open(encrypted_path, 'wb') as file:
                file.write(encrypted_data)
            
            logging.info(f"Certificado cifrado exitosamente: {encrypted_path}")
            return encrypted_path
            
        except Exception as e:
            logging.error(f"Error cifrando certificado: {str(e)}")
            raise Exception(f"Error cifrando certificado: {str(e)}")

    def generar_certificado_falso(self, archivo_path: str, usuario_id: int) -> str:
        """
        Genera un archivo PDF falso que muestra contenido cifrado para usuarios no autorizados
        """
        try:
            from reportlab.lib.pagesizes import letter, A4
            from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
            from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
            from reportlab.lib import colors
            import io
            
            # Leer el archivo original para cifrarlo
            with open(archivo_path, 'rb') as file:
                file_data = file.read()
            
            # Generar clave basada en el ID del usuario
            password = str(usuario_id).encode()
            salt = b'ceas_certificate_salt_2024'
            
            # Derivar clave usando PBKDF2
            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=32,
                salt=salt,
                iterations=100000,
            )
            key = base64.urlsafe_b64encode(kdf.derive(password))
            
            # Cifrar el archivo
            fernet = Fernet(key)
            encrypted_data = fernet.encrypt(file_data)
            
            # Convertir datos cifrados a base64 para mostrar
            encrypted_b64 = base64.b64encode(encrypted_data).decode('utf-8')
            
            # Crear nombre del archivo falso
            base_name = os.path.basename(archivo_path)
            name_without_ext = os.path.splitext(base_name)[0]
            fake_filename = f"{name_without_ext}_cifrado_{usuario_id}.pdf"
            fake_path = os.path.join(self.cifrados_dir, fake_filename)
            
            # Crear PDF falso que muestre el contenido cifrado
            doc = SimpleDocTemplate(fake_path, pagesize=A4)
            styles = getSampleStyleSheet()
            
            # Estilo para el contenido cifrado
            cipher_style = ParagraphStyle(
                'CipherText',
                parent=styles['Normal'],
                fontSize=8,
                fontName='Courier',
                textColor=colors.red,
                leading=10
            )
            
            # Contenido del PDF falso
            story = []
            
            # Título
            title = Paragraph("🔒 CERTIFICADO CIFRADO - ACCESO DENEGADO", styles['Title'])
            story.append(title)
            story.append(Spacer(1, 20))
            
            # Mensaje de advertencia
            warning = Paragraph(
                "<b>⚠️ ADVERTENCIA:</b><br/>"
                "Este certificado está cifrado y solo puede ser visualizado por el propietario autorizado. "
                "El contenido que ves a continuación son datos cifrados que no pueden ser leídos sin la clave correspondiente.",
                styles['Normal']
            )
            story.append(warning)
            story.append(Spacer(1, 20))
            
            # Información del cifrado
            info = Paragraph(
                f"<b>Información del cifrado:</b><br/>"
                f"• Usuario ID: {usuario_id}<br/>"
                f"• Algoritmo: AES-256<br/>"
                f"• Salt: ceas_certificate_salt_2024<br/>"
                f"• Iteraciones PBKDF2: 100,000<br/>"
                f"• Tamaño original: {len(file_data)} bytes<br/>"
                f"• Tamaño cifrado: {len(encrypted_data)} bytes",
                styles['Normal']
            )
            story.append(info)
            story.append(Spacer(1, 20))
            
            # Contenido cifrado (dividido en líneas para mejor visualización)
            story.append(Paragraph("<b>Contenido cifrado (Base64):</b>", styles['Heading3']))
            story.append(Spacer(1, 10))
            
            # Dividir el contenido cifrado en líneas de 80 caracteres
            lines = [encrypted_b64[i:i+80] for i in range(0, len(encrypted_b64), 80)]
            for line in lines[:50]:  # Mostrar solo las primeras 50 líneas para no sobrecargar
                cipher_line = Paragraph(line, cipher_style)
                story.append(cipher_line)
            
            if len(lines) > 50:
                story.append(Spacer(1, 10))
                story.append(Paragraph(f"... y {len(lines) - 50} líneas más", styles['Normal']))
            
            story.append(Spacer(1, 20))
            
            # Pie de página
            footer = Paragraph(
                "Este documento fue generado automáticamente por el sistema CEAS.<br/>"
                "Para acceder al certificado original, contacta al administrador del sistema.",
                styles['Normal']
            )
            story.append(footer)
            
            # Construir el PDF
            doc.build(story)
            
            logging.info(f"Certificado falso generado exitosamente: {fake_path}")
            return fake_path
            
        except Exception as e:
            logging.error(f"Error generando certificado falso: {str(e)}")
            raise Exception(f"Error generando certificado falso: {str(e)}")
    
    def descifrar_certificado(self, archivo_cifrado_path: str, usuario_id: int) -> bytes:
        """
        Descifra un certificado usando el ID del usuario
        """
        try:
            # Leer el archivo cifrado
            with open(archivo_cifrado_path, 'rb') as file:
                encrypted_data = file.read()
            
            # Generar la misma clave que se usó para cifrar
            password = str(usuario_id).encode()
            salt = b'ceas_certificate_salt_2024'
            
            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=32,
                salt=salt,
                iterations=100000,
            )
            key = base64.urlsafe_b64encode(kdf.derive(password))
            
            # Descifrar el archivo
            fernet = Fernet(key)
            decrypted_data = fernet.decrypt(encrypted_data)
            
            logging.info(f"Certificado descifrado exitosamente para usuario {usuario_id}")
            return decrypted_data
            
        except Exception as e:
            logging.error(f"Error descifrando certificado: {str(e)}")
            raise Exception(f"Error descifrando certificado: {str(e)}")
    
    def generar_certificado_completo(self, accion_data: Dict[str, Any], usuario_id: int) -> Dict[str, str]:
        """
        Genera certificado PDF y lo cifra usando almacenamiento local
        """
        try:
            # 1. Generar certificado PDF original
            certificado_path = self.generar_certificado_pdf(accion_data)
            
            # 2. Cifrar certificado
            certificado_cifrado_path = self.cifrar_certificado(certificado_path, usuario_id)
            
            # Obtener solo el nombre del archivo para la BD
            certificado_filename = os.path.basename(certificado_path)
            certificado_cifrado_filename = os.path.basename(certificado_cifrado_path)
            
            result = {
                "certificado_original": certificado_filename,  # Solo el nombre del archivo
                "certificado_original_path": certificado_path,  # Ruta completa para referencia
                "certificado_cifrado": certificado_cifrado_filename,  # Solo el nombre del archivo
                "certificado_cifrado_path": certificado_cifrado_path,  # Ruta completa para referencia
                "fecha_generacion": datetime.now().isoformat(),
                "almacenamiento": "local"
            }
            
            logging.info("✅ Certificados generados y almacenados localmente")
            return result
            
        except Exception as e:
            logging.error(f"Error en generación completa de certificado: {str(e)}")
            raise Exception(f"Error generando certificado completo: {str(e)}")
    
    def limpiar_certificados_antiguos(self, dias_antiguedad: int = 30):
        """
        Limpia certificados antiguos para liberar espacio
        """
        try:
            import glob
            import time
            
            archivos_eliminados = 0
            tiempo_limite = time.time() - (dias_antiguedad * 24 * 60 * 60)
            
            # Limpiar certificados originales
            patron_originales = os.path.join(self.originales_dir, "*.pdf")
            for archivo in glob.glob(patron_originales):
                if os.path.getmtime(archivo) < tiempo_limite:
                    os.remove(archivo)
                    archivos_eliminados += 1
            
            # Limpiar certificados cifrados
            patron_cifrados = os.path.join(self.cifrados_dir, "*.bin")
            for archivo in glob.glob(patron_cifrados):
                if os.path.getmtime(archivo) < tiempo_limite:
                    os.remove(archivo)
                    archivos_eliminados += 1
            
            logging.info(f"Se eliminaron {archivos_eliminados} certificados antiguos")
            return archivos_eliminados
            
        except Exception as e:
            logging.error(f"Error limpiando certificados antiguos: {str(e)}")
            return 0
