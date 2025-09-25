from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch, cm
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.pdfgen import canvas
from reportlab.lib.colors import HexColor
import qrcode
from io import BytesIO
import os
from datetime import datetime
import PyPDF2
import logging
import hashlib
import secrets

class PDFService:
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()
    
    def _setup_custom_styles(self):
        """Configura estilos personalizados para el certificado"""
        # Estilo para el título principal
        self.styles.add(ParagraphStyle(
            name='TituloPrincipal',
            parent=self.styles['Heading1'],
            fontSize=28,
            spaceAfter=30,
            alignment=TA_CENTER,
            textColor=colors.black,
            fontName='Helvetica-Bold'
        ))
        
        # Estilo para subtítulos
        self.styles.add(ParagraphStyle(
            name='Subtitulo',
            parent=self.styles['Heading2'],
            fontSize=18,
            spaceAfter=25,
            alignment=TA_CENTER,
            textColor=colors.black,
            fontName='Helvetica-Bold'
        ))
        
        # Estilo para texto normal
        self.styles.add(ParagraphStyle(
            name='TextoNormal',
            parent=self.styles['Normal'],
            fontSize=12,
            spaceAfter=15,
            alignment=TA_LEFT,
            textColor=colors.black,
            fontName='Helvetica'
        ))
        
        # Estilo para el nombre del socio
        self.styles.add(ParagraphStyle(
            name='NombreSocio',
            parent=self.styles['Normal'],
            fontSize=20,
            spaceAfter=25,
            alignment=TA_CENTER,
            textColor=colors.black,
            fontName='Helvetica-Bold'
        ))
        
        # Estilo para firmas
        self.styles.add(ParagraphStyle(
            name='Firma',
            parent=self.styles['Normal'],
            fontSize=11,
            spaceAfter=8,
            alignment=TA_CENTER,
            textColor=colors.black,
            fontName='Helvetica'
        ))
        
        # Estilo para el valor nominal
        self.styles.add(ParagraphStyle(
            name='ValorNominal',
            parent=self.styles['Normal'],
            fontSize=16,
            spaceAfter=20,
            alignment=TA_CENTER,
            textColor=colors.black,
            fontName='Helvetica'
        ))
    
    def generar_certificado_accion(self, accion_data, socio_data, modalidad_data):
        """Genera un certificado PDF para una acción usando la plantilla existente"""
        try:
            from PyPDF2 import PdfReader, PdfWriter
            from reportlab.pdfgen import canvas
            from reportlab.lib.pagesizes import A4
            import io
            
            # Ruta a la plantilla
            plantilla_path = "assets/plantilla_certificado.pdf"
            
            logging.info(f"🔍 Intentando leer plantilla: {plantilla_path}")
            
            if not os.path.exists(plantilla_path):
                raise FileNotFoundError(f"Plantilla no encontrada: {plantilla_path}")
            
            logging.info(f"✅ Plantilla encontrada: {os.path.getsize(plantilla_path)} bytes")
            
            # Leer la plantilla existente
            plantilla_reader = PdfReader(plantilla_path)
            plantilla_page = plantilla_reader.pages[0]
            
            logging.info(f"✅ Plantilla leída correctamente, páginas: {len(plantilla_reader.pages)}")
            
            # Crear un nuevo PDF en memoria
            output_buffer = io.BytesIO()
            
            # Crear un canvas para escribir sobre la plantilla
            packet = io.BytesIO()
            can = canvas.Canvas(packet, pagesize=A4)
            
            logging.info("✅ Canvas creado correctamente")
            
            # Configurar fuentes y estilos
            can.setFont("Helvetica-Bold", 14)
            can.setFillColorRGB(0, 0, 0)  # Negro
            
            # POSICIONES FINALES - MÁS A LA DERECHA Y UN POCO MÁS ARRIBA
            # N° de Acción (arriba, centrado - donde dice "N° Acción: 00002 CEAS LP")
            numero_accion = f"{accion_data['id_accion']:05d} CEAS LP"
            can.drawString(400, 580, numero_accion)
            
            # Nombre del Socio (centro - donde dice "Pedro Alejandro Casso Achá")
            nombre_completo = f"{socio_data['nombre']} {socio_data['apellido']}"
            can.setFont("Helvetica-Bold", 24)
            can.drawString(350, 360, nombre_completo)
            
            # CI (debajo del nombre - donde dice "CI: 2875925")
            can.setFont("Helvetica", 12)
            ci_texto = f"CI: {socio_data['ci_nit']}"
            can.drawString(350, 330, ci_texto)
            
            # Fecha (derecha - donde dice "07deagosto de 2024")
            fecha_fija = "20 de agosto de 2025"
            can.setFont("Helvetica-Bold", 14)
            can.setFillColorRGB(0, 0, 0)  # Negro
            can.drawString(450, 330, fecha_fija)  # Más a la izquierda para que se vea completa
            
            logging.info(f"✅ Datos dibujados: {numero_accion}, {nombre_completo}, {ci_texto}, {fecha_fija}")
            
            can.save()
            logging.info("✅ Canvas guardado")
            
            # Mover al inicio del buffer
            packet.seek(0)
            
            # Crear PDF temporal con los datos
            datos_pdf = PdfReader(packet)
            datos_page = datos_pdf.pages[0]
            logging.info("✅ PDF de datos creado")
            
            # Combinar plantilla + datos
            plantilla_page.merge_page(datos_page)
            logging.info("✅ Plantilla y datos combinados")
            
            # Escribir el resultado final
            output_writer = PdfWriter()
            output_writer.add_page(plantilla_page)
            
            # Guardar en el buffer de salida
            output_writer.write(output_buffer)
            output_buffer.seek(0)
            
            logging.info("✅ PDF final generado exitosamente")
            
            # Retornar PDF sin cifrar por defecto
            pdf_content = output_buffer.getvalue()
            
            logging.info("✅ PDF generado sin cifrar (acceso libre)")
            
            # Retornar PDF sin cifrar
            return {
                'pdf_cifrado': pdf_content,  # Mantener el nombre por compatibilidad
                'password': None,
                'salt': None,
                'password_hash': None,
                'fecha_cifrado': None
            }
            
        except Exception as e:
            logging.error(f"Error generando certificado con plantilla: {str(e)}")
            logging.error(f"Tipo de error: {type(e).__name__}")
            logging.error(f"Detalles completos: {e}")
            # Fallback al método anterior si hay error
            return self._generar_certificado_fallback(accion_data, socio_data, modalidad_data)
    
    def _numero_a_texto(self, numero):
        """Convierte un número a texto en español"""
        unidades = ['', 'uno', 'dos', 'tres', 'cuatro', 'cinco', 'seis', 'siete', 'ocho', 'nueve']
        decenas = ['', 'diez', 'veinte', 'treinta', 'cuarenta', 'cincuenta', 'sesenta', 'setenta', 'ochenta', 'noventa']
        
        if numero == 0:
            return "cero"
        elif numero < 10:
            return unidades[numero]
        elif numero < 100:
            if numero % 10 == 0:
                return decenas[numero // 10]
            else:
                return f"{decenas[numero // 10]} y {unidades[numero % 10]}"
        elif numero == 100:
            return "cien"
        elif numero < 1000:
            if numero // 100 == 1:
                return f"ciento {self._numero_a_texto(numero % 100)}"
            else:
                return f"{unidades[numero // 100]}cientos {self._numero_a_texto(numero % 100)}"
        elif numero == 1000:
            return "mil"
        elif numero < 10000:
            if numero // 1000 == 1:
                return f"mil {self._numero_a_texto(numero % 1000)}"
            else:
                return f"{unidades[numero // 1000]} mil {self._numero_a_texto(numero % 1000)}"
        elif numero == 10000:
            return "diez mil"
        else:
            return f"{self._numero_a_texto(numero // 1000)} mil {self._numero_a_texto(numero % 1000)}"
    
    def _agregar_logo_ceas(self, buffer, accion_data):
        """Agrega el logo de CEAS al PDF existente"""
        try:
            # Obtener el contenido del PDF
            buffer.seek(0)
            pdf_content = buffer.read()
            
            # Crear un nuevo PDF con el logo
            logo_buffer = BytesIO()
            c = canvas.Canvas(logo_buffer, pagesize=A4)
            
            # Solo el logo CEAS en la esquina inferior izquierda
            logo_x, logo_y = 2*cm, 2*cm
            logo_size = 2*cm
            
            # Intentar cargar el logo oficial de CEAS
            if os.path.exists("assets/logo_ceas.png"):
                c.drawImage("assets/logo_ceas.png", logo_x - logo_size/2, logo_y - logo_size/2, 
                           width=logo_size, height=logo_size)
            else:
                # Fallback simple
                c.setFillColor(HexColor('#228B22'))
                c.circle(logo_x, logo_y, logo_size/2, fill=1)
                c.setFillColor(colors.white)
                c.setFont("Helvetica-Bold", 10)
                c.drawString(logo_x - 0.3*cm, logo_y - 0.1*cm, "CEAS")
            
            c.save()
            
            # Combinar los dos PDFs
            pdf_reader = PyPDF2.PdfReader(BytesIO(pdf_content))
            logo_reader = PyPDF2.PdfReader(logo_buffer)
            
            # Crear writer
            writer = PyPDF2.PdfWriter()
            
            # Agregar página del certificado
            writer.add_page(pdf_reader.pages[0])
            
            # Agregar logo como overlay
            if len(logo_reader.pages) > 0:
                logo_page = logo_reader.pages[0]
                writer.add_page(logo_page)
            
            # Escribir PDF combinado
            output_buffer = BytesIO()
            writer.write(output_buffer)
            output_buffer.seek(0)
            
            return output_buffer.getvalue()
            
        except Exception as e:
            # Si hay error, retornar el PDF original
            print(f"Error agregando logo: {str(e)}")
            buffer.seek(0)
            return buffer.getvalue()

    def _generar_certificado_fallback(self, accion_data, socio_data, modalidad_data):
        """Método fallback para generar certificado básico si falla la plantilla"""
        try:
            # Crear buffer para el PDF
            buffer = BytesIO()
            
            # Crear documento
            doc = SimpleDocTemplate(
                buffer,
                pagesize=A4,
                rightMargin=2*cm,
                leftMargin=2*cm,
                topMargin=2.5*cm,
                bottomMargin=2.5*cm
            )
            
            # Lista de elementos del PDF
            story = []
            
            # Título principal
            story.append(Paragraph("CERTIFICADO ACCIONARIO", self.styles['TituloPrincipal']))
            story.append(Spacer(1, 25))
            
            # Información de la acción
            accion_info = f"Acción: Nº {accion_data['id_accion']:03d} CEAS La Paz {accion_data['tipo_accion'].upper()}"
            story.append(Paragraph(accion_info, self.styles['Subtitulo']))
            
            # Fecha de emisión
            fecha_emision = accion_data.get('fecha_emision_certificado')
            if fecha_emision:
                try:
                    fecha = datetime.fromisoformat(fecha_emision.replace('Z', '+00:00'))
                    fecha_formateada = fecha.strftime("La Paz, %d de %B de %Y")
                except:
                    fecha_formateada = "La Paz, fecha de emisión"
            else:
                fecha_formateada = "La Paz, fecha de emisión"
            
            story.append(Paragraph(fecha_formateada, self.styles['TextoNormal']))
            story.append(Spacer(1, 35))
            
            # Texto introductorio
            intro_text = """El Directorio del Centro Ecuestre Apóstol Santiago "CEAS" otorga el presente certificado accionario a:"""
            story.append(Paragraph(intro_text, self.styles['TextoNormal']))
            story.append(Spacer(1, 25))
            
            # Nombre del socio
            nombre_completo = socio_data.get('socio_titular', 'Socio no encontrado')
            story.append(Paragraph(nombre_completo, self.styles['NombreSocio']))
            story.append(Spacer(1, 25))
            
            # CI del socio (si está disponible)
            if 'ci_nit' in socio_data and socio_data['ci_nit']:
                ci_text = f"CI: {socio_data['ci_nit']}"
                story.append(Paragraph(ci_text, self.styles['TextoNormal']))
                story.append(Spacer(1, 25))
            
            # Valor nominal
            valor_nominal = modalidad_data.get('precio_renovacion', 0)
            valor_texto = self._numero_a_texto(valor_nominal)
            
            story.append(Paragraph("Con un valor nominal de:", self.styles['TextoNormal']))
            story.append(Paragraph(f"Bolivianos {valor_texto}.", self.styles['TextoNormal']))
            story.append(Paragraph(f"{valor_nominal:,.0f}.- Bolivianos", self.styles['ValorNominal']))
            story.append(Spacer(1, 50))
            
            # Tabla de firmas
            firmas_data = [
                ['', '', ''],
                ['ROMMEL MORÓN ROMERO', 'ALEJANDRO CASSO ACHA', 'RAÚL RUBÍN DE CELIS VATTUONE'],
                ['Director Administrativo', 'Presidente', 'Vicepresidente']
            ]
            
            tabla_firmas = Table(firmas_data, colWidths=[doc.width/3.0]*3)
            tabla_firmas.setStyle(TableStyle([
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 1), (-1, 1), 'Helvetica-Bold'),
                ('FONTNAME', (0, 2), (-1, 2), 'Helvetica'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 25),
                ('TOPPADDING', (0, 0), (-1, -1), 15),
            ]))
            
            story.append(tabla_firmas)
            
            # Construir PDF
            doc.build(story)
            
            # Obtener contenido del buffer
            pdf_content = buffer.getvalue()
            buffer.close()
            
            return pdf_content
            
        except Exception as e:
            logging.error(f"Error en método fallback: {str(e)}")
            # Retornar PDF de error básico
            return self._generar_pdf_error()
    
    def _generar_pdf_error(self):
        """Genera un PDF básico de error"""
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4)
        
        story = []
        story.append(Paragraph("Error Generando Certificado", self.styles['TituloPrincipal']))
        story.append(Spacer(1, 20))
        story.append(Paragraph("No se pudo generar el certificado. Contacte al administrador.", self.styles['TextoNormal']))
        
        doc.build(story)
        pdf_content = buffer.getvalue()
        buffer.close()
        
        return pdf_content
    
    def cifrar_pdf(self, pdf_content, password):
        """Cifra un PDF con contraseña"""
        try:
            from PyPDF2 import PdfReader, PdfWriter
            
            # Generar salt único para mayor seguridad
            salt = secrets.token_hex(16)
            
            # Crear hash de la contraseña con salt
            password_hash = hashlib.pbkdf2_hmac('sha256', password.encode(), salt.encode(), 100000)
            
            # Leer el PDF original
            pdf_reader = PdfReader(BytesIO(pdf_content))
            pdf_writer = PdfWriter()
            
            # Agregar todas las páginas
            for page in pdf_reader.pages:
                pdf_writer.add_page(page)
            
            # Cifrar con contraseña
            pdf_writer.encrypt(password)
            
            # Guardar PDF cifrado
            output_buffer = BytesIO()
            pdf_writer.write(output_buffer)
            output_buffer.seek(0)
            
            # Retornar PDF cifrado y metadata de seguridad
            return {
                'pdf_cifrado': output_buffer.getvalue(),
                'salt': salt,
                'password_hash': password_hash.hex(),
                'fecha_cifrado': datetime.now().isoformat()
            }
            
        except Exception as e:
            logging.error(f"Error cifrando PDF: {str(e)}")
            raise Exception(f"No se pudo cifrar el PDF: {str(e)}")
    
    def descifrar_pdf(self, pdf_cifrado, password):
        """Descifra un PDF con contraseña"""
        try:
            from PyPDF2 import PdfReader, PdfWriter
            
            # Leer PDF cifrado
            pdf_reader = PdfReader(BytesIO(pdf_cifrado))
            
            # Verificar si está cifrado
            if pdf_reader.is_encrypted:
                # Intentar descifrar
                if pdf_reader.decrypt(password):
                    # Crear PDF descifrado
                    pdf_writer = PdfWriter()
                    for page in pdf_reader.pages:
                        pdf_writer.add_page(page)
                    
                    output_buffer = BytesIO()
                    pdf_writer.write(output_buffer)
                    output_buffer.seek(0)
                    
                    return output_buffer.getvalue()
                else:
                    raise Exception("Contraseña incorrecta")
            else:
                # PDF no está cifrado
                return pdf_cifrado
                
        except Exception as e:
            logging.error(f"Error descifrando PDF: {str(e)}")
            raise Exception(f"No se pudo descifrar el PDF: {str(e)}")
