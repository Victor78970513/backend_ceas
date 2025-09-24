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
        Genera certificado PDF para una acción
        """
        try:
            # Crear nombre del archivo
            id_accion = accion_data.get('id_accion')
            id_socio = accion_data.get('id_socio')
            fecha_actual = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"certificado_accion_{id_accion}_{id_socio}_{fecha_actual}.pdf"
            filepath = os.path.join(self.originales_dir, filename)
            
            # Crear documento PDF
            doc = SimpleDocTemplate(filepath, pagesize=A4)
            styles = getSampleStyleSheet()
            story = []
            
            # Estilo personalizado para el título
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=styles['Heading1'],
                fontSize=24,
                spaceAfter=30,
                alignment=1,  # Centrado
                textColor=colors.darkblue
            )
            
            # Estilo para subtítulos
            subtitle_style = ParagraphStyle(
                'CustomSubtitle',
                parent=styles['Heading2'],
                fontSize=16,
                spaceAfter=15,
                textColor=colors.darkgreen
            )
            
            # Estilo para texto normal
            normal_style = ParagraphStyle(
                'CustomNormal',
                parent=styles['Normal'],
                fontSize=12,
                spaceAfter=10
            )
            
            # Título del certificado
            story.append(Paragraph("CERTIFICADO DE ACCIÓN", title_style))
            story.append(Spacer(1, 20))
            
            # Información del club
            story.append(Paragraph("CLUB DE EMPRENDEDORES Y ACCIONISTAS", subtitle_style))
            story.append(Paragraph("CEAS - Bolivia", normal_style))
            story.append(Spacer(1, 20))
            
            # Información de la acción
            story.append(Paragraph("INFORMACIÓN DE LA ACCIÓN", subtitle_style))
            story.append(Paragraph(f"<b>Número de Acción:</b> {id_accion}", normal_style))
            story.append(Paragraph(f"<b>Tipo de Acción:</b> {accion_data.get('tipo_accion', 'Compra')}", normal_style))
            story.append(Paragraph(f"<b>Cantidad de Acciones:</b> {accion_data.get('cantidad_acciones', 1)}", normal_style))
            story.append(Paragraph(f"<b>Precio Unitario:</b> Bs. {accion_data.get('precio_unitario', 0.00):.2f}", normal_style))
            story.append(Paragraph(f"<b>Total Pagado:</b> Bs. {accion_data.get('total_pago', 0.00):.2f}", normal_style))
            story.append(Paragraph(f"<b>Fecha de Compra:</b> {datetime.now().strftime('%d/%m/%Y')}", normal_style))
            story.append(Spacer(1, 20))
            
            # Información del socio
            story.append(Paragraph("INFORMACIÓN DEL SOCIO", subtitle_style))
            story.append(Paragraph(f"<b>Nombre Completo:</b> {accion_data.get('socio_titular', 'No especificado')}", normal_style))
            story.append(Paragraph(f"<b>ID Socio:</b> {id_socio}", normal_style))
            story.append(Spacer(1, 20))
            
            # Información de pago
            story.append(Paragraph("INFORMACIÓN DE PAGO", subtitle_style))
            story.append(Paragraph(f"<b>Método de Pago:</b> {accion_data.get('metodo_pago', 'No especificado')}", normal_style))
            story.append(Paragraph(f"<b>Modalidad de Pago:</b> {accion_data.get('modalidad_pago_info', 'No especificado')}", normal_style))
            story.append(Spacer(1, 20))
            
            # Firma y sello
            story.append(Spacer(1, 30))
            story.append(Paragraph("_________________________", normal_style))
            story.append(Paragraph("Firma del Administrador", normal_style))
            story.append(Spacer(1, 20))
            story.append(Paragraph("Este certificado es válido y auténtico", normal_style))
            story.append(Paragraph(f"Generado el: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}", normal_style))
            
            # Construir PDF
            doc.build(story)
            
            logging.info(f"Certificado PDF generado exitosamente: {filepath}")
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
        Genera certificado PDF y lo cifra
        """
        try:
            # 1. Generar certificado PDF original
            certificado_path = self.generar_certificado_pdf(accion_data)
            
            # 2. Cifrar certificado
            certificado_cifrado_path = self.cifrar_certificado(certificado_path, usuario_id)
            
            return {
                "certificado_original": certificado_path,
                "certificado_cifrado": certificado_cifrado_path,
                "fecha_generacion": datetime.now().isoformat()
            }
            
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
