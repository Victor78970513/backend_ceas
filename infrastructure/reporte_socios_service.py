from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch, cm
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.pdfgen import canvas
from datetime import datetime
from io import BytesIO
import matplotlib
matplotlib.use('Agg')  # Usar backend sin GUI
import matplotlib.pyplot as plt
from matplotlib.backends.backend_agg import FigureCanvasAgg
import numpy as np

class ReporteSociosService:
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()
    
    def _setup_custom_styles(self):
        """Configura estilos personalizados para el reporte"""
        # Estilo para el título principal
        self.styles.add(ParagraphStyle(
            name='TituloReporte',
            parent=self.styles['Heading1'],
            fontSize=24,
            spaceAfter=20,
            alignment=TA_CENTER,
            textColor=colors.HexColor('#1a472a'),
            fontName='Helvetica-Bold'
        ))
        
        # Estilo para subtítulos
        self.styles.add(ParagraphStyle(
            name='Subtitulo',
            parent=self.styles['Heading2'],
            fontSize=14,
            spaceAfter=12,
            alignment=TA_LEFT,
            textColor=colors.HexColor('#2d5a3d'),
            fontName='Helvetica-Bold'
        ))
        
        # Estilo para texto normal
        self.styles.add(ParagraphStyle(
            name='TextoNormal',
            parent=self.styles['Normal'],
            fontSize=10,
            spaceAfter=8,
            alignment=TA_LEFT,
            textColor=colors.black,
            fontName='Helvetica'
        ))
        
        # Estilo para texto pequeño
        self.styles.add(ParagraphStyle(
            name='TextoPequeño',
            parent=self.styles['Normal'],
            fontSize=8,
            spaceAfter=4,
            alignment=TA_LEFT,
            textColor=colors.grey,
            fontName='Helvetica'
        ))
    
    def generar_pdf_socios(self, socios_data):
        """Genera un PDF con el reporte de socios"""
        try:
            buffer = BytesIO()
            doc = SimpleDocTemplate(buffer, pagesize=A4, 
                                    rightMargin=50, leftMargin=50,
                                    topMargin=50, bottomMargin=50)
            
            story = []
            
            # Título del reporte
            titulo = Paragraph("Reporte de Socios - CEAS", self.styles['TituloReporte'])
            story.append(titulo)
            story.append(Spacer(1, 0.3*cm))
            
            # Fecha de generación
            fecha_gen = Paragraph(
                f"<b>Fecha de generación:</b> {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}",
                self.styles['TextoNormal']
            )
            story.append(fecha_gen)
            story.append(Spacer(1, 0.3*cm))
            
            # Información general
            total_socios = len(socios_data)
            total_activos = sum(1 for s in socios_data if s.get('estado') == 'Activo')
            total_inactivos = sum(1 for s in socios_data if s.get('estado') == 'Inactivo')
            
            info_general = Paragraph(
                f"<b>Total de socios:</b> {total_socios} | <b>Activos:</b> {total_activos} | <b>Inactivos:</b> {total_inactivos}",
                self.styles['TextoNormal']
            )
            story.append(info_general)
            story.append(Spacer(1, 0.5*cm))
            
            # Subtítulo para la tabla de datos
            subtitulo_tabla = Paragraph("Listado de Socios", self.styles['Subtitulo'])
            story.append(subtitulo_tabla)
            story.append(Spacer(1, 0.3*cm))
            
            # Tabla de socios (horizontal compacta)
            if socios_data:
                # Encabezados de la tabla - solo campos esenciales
                data = [['ID', 'Nombre', 'Email', 'Teléfono', 'Acciones', 'Estado']]
                
                # Datos de socios
                for socio in socios_data:
                    # Truncar nombres y emails largos
                    nombre_completo = f"{socio.get('nombres', '')[:15]} {socio.get('apellidos', '')[:15]}"
                    email = (socio.get('correo_electronico', 'N/A') or 'N/A')[:25]
                    telefono = (socio.get('telefono', 'N/A') or 'Sin tel')[:15]
                    
                    row = [
                        str(socio.get('id_socio', 'N/A')),
                        nombre_completo.strip(),
                        email,
                        telefono,
                        str(socio.get('cantidad_acciones', 0)),
                        socio.get('estado', 'N/A')[:8]
                    ]
                    data.append(row)
                
                # Crear tabla con anchos ajustados para pagina A4 horizontal
                tabla = Table(data, colWidths=[1.5*cm, 5*cm, 5*cm, 3.5*cm, 2*cm, 2.5*cm])
                tabla.setStyle(TableStyle([
                    # Estilo para el encabezado
                    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2d5a3d')),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 9),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
                    ('TOPPADDING', (0, 0), (-1, 0), 8),
                    # Estilo para las filas
                    ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                    ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
                    ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                    ('FONTSIZE', (0, 1), (-1, -1), 8),
                    ('GRID', (0, 0), (-1, -1), 1, colors.grey),
                    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                    # Alternar colores de filas
                    ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f0f0f0')]),
                    # Padding de celdas
                    ('LEFTPADDING', (0, 0), (-1, -1), 4),
                    ('RIGHTPADDING', (0, 0), (-1, -1), 4),
                    ('TOPPADDING', (0, 1), (-1, -1), 4),
                    ('BOTTOMPADDING', (0, 1), (-1, -1), 4),
                ]))
                
                story.append(tabla)
            else:
                story.append(Paragraph("<b>No hay socios registrados</b>", self.styles['TextoNormal']))
            
            # Agregar salto de página para las gráficas
            story.append(PageBreak())
            
            # Subtítulo para las gráficas
            subtitulo_graficas = Paragraph("Análisis y Gráficas", self.styles['Subtitulo'])
            story.append(subtitulo_graficas)
            story.append(Spacer(1, 0.3*cm))
            
            # Gráfica 1: Estado de socios
            grafica_estado = self._generar_grafica_estado_socios(socios_data)
            if grafica_estado:
                img_estado = Image(grafica_estado, width=16*cm, height=10*cm)
                story.append(img_estado)
                desc_estado = Paragraph(
                    "Muestra la distribución de socios según su estado actual. Verde representa los activos y rojo los inactivos.",
                    self.styles['TextoNormal']
                )
                story.append(desc_estado)
                story.append(Spacer(1, 0.5*cm))
            
            # Gráfica 2: Distribución de acciones
            grafica_acciones = self._generar_grafica_acciones_socios(socios_data)
            if grafica_acciones:
                img_acciones = Image(grafica_acciones, width=16*cm, height=10*cm)
                story.append(img_acciones)
                desc_acciones = Paragraph(
                    "Indica cuántos socios poseen cada cantidad de acciones en el club.",
                    self.styles['TextoNormal']
                )
                story.append(desc_acciones)
                story.append(Spacer(1, 0.5*cm))
            
            # Gráfica 3: Socios por período de ingreso
            grafica_periodo = self._generar_grafica_periodo_ingreso(socios_data)
            if grafica_periodo:
                img_periodo = Image(grafica_periodo, width=16*cm, height=9*cm)
                story.append(img_periodo)
                desc_periodo = Paragraph(
                    "Presenta el número de socios que ingresaron en cada trimestre del año.",
                    self.styles['TextoNormal']
                )
                story.append(desc_periodo)
                story.append(Spacer(1, 0.5*cm))
            
            # Gráfica 4: Top 10 socios con más acciones
            grafica_top_socios = self._generar_grafica_top_socios(socios_data)
            if grafica_top_socios:
                img_top = Image(grafica_top_socios, width=16*cm, height=10*cm)
                story.append(img_top)
                desc_top = Paragraph(
                    "Ranking de los 10 socios que poseen más acciones en el club, ordenados de mayor a menor.",
                    self.styles['TextoNormal']
                )
                story.append(desc_top)
                story.append(Spacer(1, 0.5*cm))
            
            # Gráfica 5: Métodos de pago
            grafica_metodos_pago = self._generar_grafica_metodos_pago()
            if grafica_metodos_pago:
                img_metodos = Image(grafica_metodos_pago, width=14*cm, height=12*cm)
                story.append(img_metodos)
                # Descripción de la gráfica
                desc_metodos = Paragraph(
                    "Esta gráfica muestra la distribución de los métodos de pago utilizados en las transacciones del sistema.",
                    self.styles['TextoNormal']
                )
                story.append(desc_metodos)
                story.append(Spacer(1, 0.5*cm))
            
            # Gráfica 6: Crecimiento mensual
            grafica_crecimiento = self._generar_grafica_crecimiento_mensual(socios_data)
            if grafica_crecimiento:
                img_crecimiento = Image(grafica_crecimiento, width=16*cm, height=9*cm)
                story.append(img_crecimiento)
                desc_crecimiento = Paragraph(
                    "Evolución temporal del número de socios que se han incorporado al club mes a mes.",
                    self.styles['TextoNormal']
                )
                story.append(desc_crecimiento)
                story.append(Spacer(1, 0.5*cm))
            
            # Pie de página
            story.append(Spacer(1, 0.5*cm))
            pie_pagina = Paragraph(
                f"<i>Generado por CEAS ERP - {datetime.now().strftime('%Y')}</i>",
                self.styles['TextoPequeño']
            )
            story.append(pie_pagina)
            
            # Construir PDF
            doc.build(story, onFirstPage=self._agregar_pie_de_pagina, onLaterPages=self._agregar_pie_de_pagina)
            
            buffer.seek(0)
            return buffer.getvalue()
            
        except Exception as e:
            raise Exception(f"Error al generar PDF de socios: {str(e)}")
    
    def _agregar_pie_de_pagina(self, canvas, doc):
        """Agrega pie de página a cada página del PDF"""
        canvas.saveState()
        canvas.setFont('Helvetica', 9)
        canvas.drawString(cm, cm, f"Página {doc.page}")
        canvas.restoreState()
    
    def _generar_grafica_estado_socios(self, socios_data):
        """Genera gráfica de barras del estado de los socios"""
        try:
            # Contar socios activos e inactivos
            activos = sum(1 for s in socios_data if s.get('estado') == 'Activo')
            inactivos = sum(1 for s in socios_data if s.get('estado') == 'Inactivo')
            
            # Configurar la figura con fondo
            fig, ax = plt.subplots(figsize=(7, 5))
            fig.patch.set_facecolor('#f8f9fa')
            ax.set_facecolor('#ffffff')
            
            # Datos
            categorias = ['Activos', 'Inactivos']
            valores = [activos, inactivos]
            colores = ['#2d5a3d', '#d32f2f']
            
            # Crear gráfica de barras con efectos visuales
            bars = ax.bar(categorias, valores, color=colores, edgecolor='white', linewidth=3,
                         width=0.6, alpha=0.85)
            
            # Agregar sombra y degradado
            for bar in bars:
                bar.set_shadow(True)
                gradient = np.linspace(0, 1, 100).reshape(1, -1)
                im = bar.get_facecolor()
            
            # Personalizar ejes
            ax.set_ylabel('Cantidad de Socios', fontsize=13, fontweight='bold', color='#333')
            ax.set_title('📊 Distribución de Socios por Estado', fontsize=16, fontweight='bold', 
                        pad=25, color='#2d5a3d')
            ax.grid(axis='y', alpha=0.4, linestyle='--', linewidth=1.5)
            ax.spines['top'].set_visible(False)
            ax.spines['right'].set_visible(False)
            ax.spines['left'].set_linewidth(2)
            ax.spines['bottom'].set_linewidth(2)
            
            # Agregar valores grandes en las barras
            for i, (bar, valor) in enumerate(zip(bars, valores)):
                height = bar.get_height()
                # Color del texto basado en la barra
                text_color = '#ffffff' if height > 0 else '#333'
                ax.text(bar.get_x() + bar.get_width()/2., height + max(valores) * 0.02,
                       f'{int(valor)}',
                       ha='center', va='bottom', fontsize=16, fontweight='bold', color=text_color)
            
            # Agregar porcentajes
            total = activos + inactivos
            if total > 0:
                for i, (bar, valor) in enumerate(zip(bars, valores)):
                    height = bar.get_height()
                    porcentaje = (valor / total) * 100
                    ax.text(bar.get_x() + bar.get_width()/2., height/2,
                           f'{porcentaje:.1f}%',
                           ha='center', va='center', fontsize=14, fontweight='bold', color='white')
            
            plt.tight_layout()
            
            # Convertir a imagen
            buffer = BytesIO()
            plt.savefig(buffer, format='png', dpi=200, bbox_inches='tight', facecolor='#f8f9fa')
            buffer.seek(0)
            plt.close()
            
            return buffer
            
        except Exception as e:
            return None
    
    def _generar_grafica_acciones_socios(self, socios_data):
        """Genera gráfica de distribución de acciones por socio"""
        try:
            # Agrupar socios por cantidad de acciones
            acciones_counts = {}
            for socio in socios_data:
                acc = socio.get('cantidad_acciones', 0)
                if acc not in acciones_counts:
                    acciones_counts[acc] = 0
                acciones_counts[acc] += 1
            
            # Preparar datos
            acciones = sorted([k for k in acciones_counts.keys() if k > 0])
            cantidades = [acciones_counts[k] for k in acciones]
            
            if not acciones:
                return None
            
            # Configurar la figura con fondo
            fig, ax = plt.subplots(figsize=(8, 5))
            fig.patch.set_facecolor('#f8f9fa')
            ax.set_facecolor('#ffffff')
            
            # Crear paleta de colores variados
            import matplotlib.cm as cm
            colors_map = cm.get_cmap('Set3')(np.linspace(0, 1, len(acciones)))
            
            # Crear gráfica de barras con colores variados
            bars = ax.bar(range(len(acciones)), cantidades, color=colors_map, 
                         edgecolor='white', linewidth=3, width=0.7, alpha=0.85)
            
            # Personalizar ejes
            ax.set_xlabel('Cantidad de Acciones', fontsize=13, fontweight='bold', color='#333')
            ax.set_ylabel('Número de Socios', fontsize=13, fontweight='bold', color='#333')
            ax.set_title('📈 Distribución de Acciones por Socio', fontsize=16, fontweight='bold', 
                        pad=25, color='#2d5a3d')
            ax.set_xticks(range(len(acciones)))
            ax.set_xticklabels([f'{a}' for a in acciones], fontsize=12, fontweight='bold')
            ax.grid(axis='y', alpha=0.4, linestyle='--', linewidth=1.5)
            ax.spines['top'].set_visible(False)
            ax.spines['right'].set_visible(False)
            ax.spines['left'].set_linewidth(2)
            ax.spines['bottom'].set_linewidth(2)
            
            # Agregar valores en las barras
            max_val = max(cantidades) if cantidades else 1
            for bar, valor in zip(bars, cantidades):
                height = bar.get_height()
                ax.text(bar.get_x() + bar.get_width()/2., height + max_val * 0.02,
                       f'{int(valor)}',
                       ha='center', va='bottom', fontsize=14, fontweight='bold', color='#2d5a3d')
            
            plt.tight_layout()
            
            # Convertir a imagen
            buffer = BytesIO()
            plt.savefig(buffer, format='png', dpi=200, bbox_inches='tight', facecolor='#f8f9fa')
            buffer.seek(0)
            plt.close()
            
            return buffer
            
        except Exception as e:
            return None
    
    def _generar_grafica_crecimiento_mensual(self, socios_data):
        """Genera gráfica de crecimiento mensual de socios"""
        try:
            # Agrupar socios por mes de ingreso
            meses = {}
            for socio in socios_data:
                fecha = socio.get('fecha_ingreso')
                if fecha:
                    # Parsear fecha si es string
                    if isinstance(fecha, str):
                        try:
                            fecha_obj = datetime.strptime(fecha.split()[0], '%d/%m/%Y')
                        except:
                            continue
                    else:
                        fecha_obj = fecha
                    
                    mes_anio = f"{fecha_obj.strftime('%Y-%m')}"
                    if mes_anio not in meses:
                        meses[mes_anio] = 0
                    meses[mes_anio] += 1
            
            if not meses:
                return None
            
            # Ordenar por fecha
            fechas_ordenadas = sorted(meses.keys())
            valores = [meses[f] for f in fechas_ordenadas]
            fechas_format = [datetime.strptime(f, '%Y-%m').strftime('%b %Y') for f in fechas_ordenadas]
            
            # Configurar la figura con fondo
            fig, ax = plt.subplots(figsize=(10, 5))
            fig.patch.set_facecolor('#f8f9fa')
            ax.set_facecolor('#ffffff')
            
            # Crear gráfica de líneas con efecto degradado
            ax.plot(fechas_format, valores, marker='o', color='#2d5a3d', linewidth=3, 
                   markersize=10, markerfacecolor='#2d5a3d', markeredgecolor='white', 
                   markeredgewidth=2)
            ax.fill_between(fechas_format, valores, alpha=0.4, color='#2d5a3d')
            
            # Agregar valores en los puntos
            for x, y in zip(fechas_format, valores):
                ax.text(x, y + 0.3, f'{int(y)}', ha='center', va='bottom', 
                       fontsize=11, fontweight='bold', color='#2d5a3d')
            
            # Personalizar
            ax.set_xlabel('Mes', fontsize=13, fontweight='bold', color='#333')
            ax.set_ylabel('Socios Nuevos', fontsize=13, fontweight='bold', color='#333')
            ax.set_title('📈 Crecimiento Mensual de Socios', fontsize=16, fontweight='bold', 
                        pad=25, color='#2d5a3d')
            ax.grid(alpha=0.4, linestyle='--', linewidth=1.5)
            ax.spines['top'].set_visible(False)
            ax.spines['right'].set_visible(False)
            ax.spines['left'].set_linewidth(2)
            ax.spines['bottom'].set_linewidth(2)
            plt.xticks(rotation=45, ha='right', fontsize=11, fontweight='bold')
            
            plt.tight_layout()
            
            # Convertir a imagen
            buffer = BytesIO()
            plt.savefig(buffer, format='png', dpi=200, bbox_inches='tight', facecolor='#f8f9fa')
            buffer.seek(0)
            plt.close()
            
            return buffer
            
        except Exception as e:
            return None
    
    def _generar_grafica_periodo_ingreso(self, socios_data):
        """Genera gráfica de socios por período de ingreso"""
        try:
            # Categorizar por mes de ingreso
            periodos = {'Ene-Mar': 0, 'Abr-Jun': 0, 'Jul-Sep': 0, 'Oct-Dic': 0}
            
            for socio in socios_data:
                fecha = socio.get('fecha_ingreso')
                if fecha:
                    try:
                        if isinstance(fecha, str):
                            fecha_obj = datetime.strptime(fecha.split()[0], '%d/%m/%Y')
                        else:
                            fecha_obj = fecha
                        
                        mes = fecha_obj.month
                        if mes in [1, 2, 3]:
                            periodos['Ene-Mar'] += 1
                        elif mes in [4, 5, 6]:
                            periodos['Abr-Jun'] += 1
                        elif mes in [7, 8, 9]:
                            periodos['Jul-Sep'] += 1
                        else:
                            periodos['Oct-Dic'] += 1
                    except:
                        continue
            
            if sum(periodos.values()) == 0:
                return None
            
            # Configurar la figura
            fig, ax = plt.subplots(figsize=(8, 5))
            fig.patch.set_facecolor('#f8f9fa')
            ax.set_facecolor('#ffffff')
            
            # Datos
            labels = list(periodos.keys())
            valores = list(periodos.values())
            colores = ['#2d5a3d', '#1e88e5', '#f57c00', '#c62828']
            
            # Crear gráfica de barras horizontales
            bars = ax.barh(labels, valores, color=colores, edgecolor='white', linewidth=3, height=0.7, alpha=0.85)
            
            # Personalizar
            ax.set_xlabel('Cantidad de Socios', fontsize=13, fontweight='bold', color='#333')
            ax.set_title('📅 Ingreso de Socios por Trimestre', fontsize=16, fontweight='bold', pad=25, color='#2d5a3d')
            ax.grid(axis='x', alpha=0.4, linestyle='--', linewidth=1.5)
            ax.spines['top'].set_visible(False)
            ax.spines['right'].set_visible(False)
            ax.spines['left'].set_linewidth(2)
            ax.spines['bottom'].set_linewidth(2)
            
            # Agregar valores
            max_val = max(valores) if valores else 1
            for i, (bar, valor) in enumerate(zip(bars, valores)):
                if valor > 0:
                    ax.text(valor + max_val * 0.01, bar.get_y() + bar.get_height()/2,
                           f'{int(valor)}',
                           ha='left', va='center', fontsize=14, fontweight='bold', color='#2d5a3d')
            
            plt.tight_layout()
            
            # Convertir a imagen
            buffer = BytesIO()
            plt.savefig(buffer, format='png', dpi=200, bbox_inches='tight', facecolor='#f8f9fa')
            buffer.seek(0)
            plt.close()
            
            return buffer
            
        except Exception as e:
            return None
    
    def _generar_grafica_top_socios(self, socios_data):
        """Genera gráfica de top 10 socios con más acciones"""
        try:
            # Filtrar socios con acciones
            socios_con_acciones = [(s, s.get('cantidad_acciones', 0)) for s in socios_data]
            socios_con_acciones = sorted(socios_con_acciones, key=lambda x: x[1], reverse=True)[:10]
            
            if not socios_con_acciones:
                return None
            
            # Preparar datos
            nombres = [f"{s[0].get('nombres', '')[:10]} {s[0].get('apellidos', '')[:8]}" for s in socios_con_acciones]
            acciones = [s[1] for s in socios_con_acciones]
            
            # Configurar la figura
            fig, ax = plt.subplots(figsize=(10, 6))
            fig.patch.set_facecolor('#f8f9fa')
            ax.set_facecolor('#ffffff')
            
            # Crear degradado
            colors_gradient = plt.cm.Greens(np.linspace(0.3, 0.9, len(acciones)))
            
            # Gráfica de barras horizontales
            bars = ax.barh(range(len(nombres)), acciones, color=colors_gradient, 
                          edgecolor='white', linewidth=2.5, height=0.7, alpha=0.85)
            
            # Personalizar
            ax.set_yticks(range(len(nombres)))
            ax.set_yticklabels(nombres, fontsize=10, fontweight='bold')
            ax.set_xlabel('Número de Acciones', fontsize=13, fontweight='bold', color='#333')
            ax.set_title('🏆 Top 10 Socios con Más Acciones', fontsize=16, fontweight='bold', pad=25, color='#2d5a3d')
            ax.grid(axis='x', alpha=0.4, linestyle='--', linewidth=1.5)
            ax.spines['top'].set_visible(False)
            ax.spines['right'].set_visible(False)
            ax.spines['left'].set_linewidth(2)
            ax.spines['bottom'].set_linewidth(2)
            
            # Agregar valores
            max_val = max(acciones)
            for bar, valor in zip(bars, acciones):
                if valor > 0:
                    ax.text(valor + max_val * 0.02, bar.get_y() + bar.get_height()/2,
                           f'{int(valor)}',
                           ha='left', va='center', fontsize=11, fontweight='bold', color='#2d5a3d')
            
            plt.tight_layout()
            
            # Convertir a imagen
            buffer = BytesIO()
            plt.savefig(buffer, format='png', dpi=200, bbox_inches='tight', facecolor='#f8f9fa')
            buffer.seek(0)
            plt.close()
            
            return buffer
            
        except Exception as e:
            return None
    
    def _generar_grafica_metodos_pago(self):
        """Genera gráfica circular de métodos de pago desde la tabla pago_accion"""
        try:
            from config import DATABASE_URL
            import psycopg2
            
            # Conectar a la BD
            conn = psycopg2.connect(DATABASE_URL)
            cursor = conn.cursor()
            
            # Contar pagos por método (tipo_pago)
            cursor.execute('''
                SELECT 
                    tp.id_tipo_pago,
                    tp.descripcion,
                    COUNT(pa.id_pago) as cantidad
                FROM tipo_pago tp
                LEFT JOIN pago_accion pa ON tp.id_tipo_pago = pa.tipo_pago
                WHERE pa.estado_pago = 2
                GROUP BY tp.id_tipo_pago, tp.descripcion
                ORDER BY cantidad DESC
            ''')
            
            resultados = cursor.fetchall()
            cursor.close()
            conn.close()
            
            if not resultados:
                return None
            
            # Preparar datos
            metodos = []
            cantidades = []
            
            for row in resultados:
                metodo = row[1] if row[1] else f"Tipo {row[0]}"
                cantidad = row[2] if row[2] else 0
                if cantidad > 0:  # Solo incluir métodos con pagos
                    metodos.append(metodo)
                    cantidades.append(cantidad)
            
            if not metodos:
                return None
            
            # Colores vibrantes y variados
            colores = ['#2d5a3d', '#1e88e5', '#f57c00', '#c62828', '#6a1b9a', '#00897b', '#ff5722', '#4caf50']
            
            # Configurar la figura
            fig, ax = plt.subplots(figsize=(9, 8))
            fig.patch.set_facecolor('#f8f9fa')
            
            # Crear gráfica circular (pie chart)
            explode = tuple([0.05] * len(metodos))  # Separar ligeramente cada segmento
            
            wedges, texts, autotexts = ax.pie(
                cantidades, 
                labels=metodos, 
                colors=colores[:len(metodos)],
                autopct='%1.1f%%',
                startangle=90, 
                explode=explode, 
                shadow=True,
                textprops={'fontsize': 12, 'fontweight': 'bold', 'color': '#333'}
            )
            
            # Personalizar
            ax.set_title('💳 Distribución de Métodos de Pago', fontsize=18, fontweight='bold', 
                        pad=30, color='#2d5a3d')
            
            # Hacer los porcentajes más visibles y grandes
            for autotext in autotexts:
                autotext.set_color('#ffffff')
                autotext.set_fontsize(13)
                autotext.set_fontweight('bold')
                autotext.set_bbox(dict(boxstyle='round,pad=0.3', facecolor='#333', alpha=0.7))
            
            # Hacer las etiquetas más grandes
            for text in texts:
                text.set_fontsize(13)
                text.set_fontweight('bold')
            
            plt.tight_layout()
            
            # Convertir a imagen
            buffer = BytesIO()
            plt.savefig(buffer, format='png', dpi=200, bbox_inches='tight', facecolor='#f8f9fa')
            buffer.seek(0)
            plt.close()
            
            return buffer
            
        except Exception as e:
            print(f"Error en _generar_grafica_metodos_pago: {e}")
            return None
    
    def generar_excel_socios(self, socios_data):
        """Genera un archivo Excel con el reporte de socios"""
        try:
            # Preparar datos para Excel
            data_excel = []
            for socio in socios_data:
                data_excel.append({
                    'ID Socio': socio.get('id_socio', 'N/A'),
                    'Nombres': socio.get('nombres', 'N/A'),
                    'Apellidos': socio.get('apellidos', 'N/A'),
                    'Email': socio.get('correo_electronico', 'N/A'),
                    'Teléfono': socio.get('telefono', 'N/A') or 'Sin teléfono',
                    'Dirección': socio.get('direccion', 'N/A') or 'Sin dirección',
                    'Fecha Ingreso': socio.get('fecha_ingreso', 'N/A'),
                    'Estado': socio.get('estado', 'N/A'),
                    'Cantidad Acciones': socio.get('cantidad_acciones', 0)
                })
            
            # Crear DataFrame
            df = pd.DataFrame(data_excel)
            
            # Crear Excel en memoria
            buffer = BytesIO()
            with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
                df.to_excel(writer, sheet_name='Socios', index=False)
                
                # Obtener la hoja de trabajo
                worksheet = writer.sheets['Socios']
                
                # Ajustar ancho de columnas
                for idx, col in enumerate(df.columns):
                    max_length = max(
                        df[col].astype(str).map(len).max(),
                        len(col)
                    )
                    worksheet.column_dimensions[chr(65 + idx)].width = min(max_length + 2, 50)
            
            buffer.seek(0)
            return buffer.getvalue()
            
        except Exception as e:
            raise Exception(f"Error al generar Excel de socios: {str(e)}")

