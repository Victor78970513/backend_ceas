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

class ReporteAccionesService:
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
    
    def generar_pdf_acciones(self, acciones_data):
        """Genera un PDF con el reporte de acciones"""
        try:
            buffer = BytesIO()
            doc = SimpleDocTemplate(buffer, pagesize=A4, 
                                    rightMargin=50, leftMargin=50,
                                    topMargin=50, bottomMargin=50)
            
            story = []
            
            # Título del reporte
            titulo = Paragraph("Reporte de Acciones - CEAS", self.styles['TituloReporte'])
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
            total_acciones = len(acciones_data)
            total_pagadas = sum(1 for a in acciones_data if a.get('estado_pago') == 'COMPLETAMENTE_PAGADA')
            total_pendientes = sum(1 for a in acciones_data if a.get('estado_pago') == 'PENDIENTE_DE_PAGO')
            total_parciales = sum(1 for a in acciones_data if a.get('estado_pago') == 'PARCIALMENTE_PAGADA')
            
            info_general = Paragraph(
                f"<b>Total de acciones:</b> {total_acciones} | <b>Pagadas:</b> {total_pagadas} | <b>Pendientes:</b> {total_pendientes} | <b>Parciales:</b> {total_parciales}",
                self.styles['TextoNormal']
            )
            story.append(info_general)
            story.append(Spacer(1, 0.5*cm))
            
            # Subtítulo para la tabla de datos
            subtitulo_tabla = Paragraph("Listado de Acciones", self.styles['Subtitulo'])
            story.append(subtitulo_tabla)
            story.append(Spacer(1, 0.3*cm))
            
            # Tabla de acciones (horizontal compacta)
            if acciones_data:
                data = [['ID', 'Socio', 'Tipo', 'Estado Pago', 'Pagado', 'Restante']]
                
                for accion in acciones_data:
                    socio_nombre = accion.get('socio_titular', 'N/A')[:20]
                    tipo_accion = accion.get('tipo_accion', 'N/A')[:8]
                    estado_pago = accion.get('estado_pago', 'N/A')[:10]
                    
                    estado_pagos = accion.get('estado_pagos', {})
                    total_pagado = estado_pagos.get('total_pagado', 0)
                    saldo = estado_pagos.get('saldo_pendiente', 0)
                    
                    row = [
                        str(accion.get('id_accion', 'N/A')),
                        socio_nombre,
                        tipo_accion,
                        estado_pago[:10],
                        f"{float(total_pagado):.0f}",
                        f"{float(saldo):.0f}"
                    ]
                    data.append(row)
                
                # Crear tabla
                tabla = Table(data, colWidths=[1.5*cm, 5.5*cm, 3*cm, 4*cm, 3*cm, 3*cm])
                tabla.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2d5a3d')),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 9),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
                    ('TOPPADDING', (0, 0), (-1, 0), 8),
                    ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                    ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
                    ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                    ('FONTSIZE', (0, 1), (-1, -1), 8),
                    ('GRID', (0, 0), (-1, -1), 1, colors.grey),
                    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                    ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f0f0f0')]),
                    ('LEFTPADDING', (0, 0), (-1, -1), 4),
                    ('RIGHTPADDING', (0, 0), (-1, -1), 4),
                    ('TOPPADDING', (0, 1), (-1, -1), 4),
                    ('BOTTOMPADDING', (0, 1), (-1, -1), 4),
                ]))
                
                story.append(tabla)
            else:
                story.append(Paragraph("<b>No hay acciones registradas</b>", self.styles['TextoNormal']))
            
            # Agregar salto de página para las gráficas
            story.append(PageBreak())
            
            # Subtítulo para las gráficas
            subtitulo_graficas = Paragraph("Análisis y Gráficas", self.styles['Subtitulo'])
            story.append(subtitulo_graficas)
            story.append(Spacer(1, 0.3*cm))
            
            # Gráfica 1: Estado de pagos
            grafica_estado = self._generar_grafica_estado_pagos(acciones_data)
            if grafica_estado:
                img_estado = Image(grafica_estado, width=16*cm, height=10*cm)
                story.append(img_estado)
                desc_estado = Paragraph(
                    "Muestra la distribución de acciones según su estado de pago. Verde representa las completamente pagadas.",
                    self.styles['TextoNormal']
                )
                story.append(desc_estado)
                story.append(Spacer(1, 0.5*cm))
            
            # Gráfica 2: Tipos de acciones
            grafica_tipos = self._generar_grafica_tipos_acciones(acciones_data)
            if grafica_tipos:
                img_tipos = Image(grafica_tipos, width=16*cm, height=10*cm)
                story.append(img_tipos)
                desc_tipos = Paragraph(
                    "Indica cuántas acciones hay de cada tipo en el club.",
                    self.styles['TextoNormal']
                )
                story.append(desc_tipos)
                story.append(Spacer(1, 0.5*cm))
            
            # Gráfica 3: Distribución de montos pagados
            grafica_montos = self._generar_grafica_montos_pagados(acciones_data)
            if grafica_montos:
                img_montos = Image(grafica_montos, width=16*cm, height=10*cm)
                story.append(img_montos)
                desc_montos = Paragraph(
                    "Presenta la distribución de montos pagados por rango de valores.",
                    self.styles['TextoNormal']
                )
                story.append(desc_montos)
                story.append(Spacer(1, 0.5*cm))
            
            # Gráfica 4: Top 10 acciones con mayor monto
            grafica_top = self._generar_grafica_top_acciones(acciones_data)
            if grafica_top:
                img_top = Image(grafica_top, width=16*cm, height=10*cm)
                story.append(img_top)
                desc_top = Paragraph(
                    "Ranking de las 10 acciones con mayor monto total, ordenadas de mayor a menor.",
                    self.styles['TextoNormal']
                )
                story.append(desc_top)
                story.append(Spacer(1, 0.5*cm))
            
            # Gráfica 5: Progreso de pagos mensual
            grafica_progreso = self._generar_grafica_progreso_mensual(acciones_data)
            if grafica_progreso:
                img_progreso = Image(grafica_progreso, width=16*cm, height=9*cm)
                story.append(img_progreso)
                desc_progreso = Paragraph(
                    "Evolución temporal de los pagos realizados en las acciones mes a mes.",
                    self.styles['TextoNormal']
                )
                story.append(desc_progreso)
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
            raise Exception(f"Error al generar PDF de acciones: {str(e)}")
    
    def _agregar_pie_de_pagina(self, canvas, doc):
        """Agrega pie de página a cada página del PDF"""
        canvas.saveState()
        canvas.setFont('Helvetica', 9)
        canvas.drawString(cm, cm, f"Página {doc.page}")
        canvas.restoreState()
    
    def _generar_grafica_estado_pagos(self, acciones_data):
        """Genera gráfica del estado de pagos de las acciones"""
        try:
            pagadas = sum(1 for a in acciones_data if a.get('estado_pago') == 'COMPLETAMENTE_PAGADA')
            parciales = sum(1 for a in acciones_data if a.get('estado_pago') == 'PARCIALMENTE_PAGADA')
            pendientes = sum(1 for a in acciones_data if a.get('estado_pago') == 'PENDIENTE_DE_PAGO')
            
            fig, ax = plt.subplots(figsize=(7, 5))
            fig.patch.set_facecolor('#f8f9fa')
            ax.set_facecolor('#ffffff')
            
            categorias = ['Completas', 'Parciales', 'Pendientes']
            valores = [pagadas, parciales, pendientes]
            colores = ['#2d5a3d', '#1e88e5', '#d32f2f']
            
            bars = ax.bar(categorias, valores, color=colores, edgecolor='white', 
                          linewidth=3, width=0.6, alpha=0.85)
            
            ax.set_ylabel('Cantidad de Acciones', fontsize=13, fontweight='bold', color='#333')
            ax.set_title('📊 Estado de Pagos de Acciones', fontsize=16, fontweight='bold', 
                        pad=25, color='#2d5a3d')
            ax.grid(axis='y', alpha=0.4, linestyle='--', linewidth=1.5)
            ax.spines['top'].set_visible(False)
            ax.spines['right'].set_visible(False)
            ax.spines['left'].set_linewidth(2)
            ax.spines['bottom'].set_linewidth(2)
            
            # Agregar valores y porcentajes
            total = pagadas + parciales + pendientes
            for i, (bar, valor) in enumerate(zip(bars, valores)):
                height = bar.get_height()
                porcentaje = (valor / total * 100) if total > 0 else 0
                ax.text(bar.get_x() + bar.get_width()/2., height + max(valores) * 0.02,
                       f'{int(valor)} ({porcentaje:.1f}%)',
                       ha='center', va='bottom', fontsize=13, fontweight='bold', color='#333')
                ax.text(bar.get_x() + bar.get_width()/2., height/2,
                       f'{porcentaje:.1f}%',
                       ha='center', va='center', fontsize=12, fontweight='bold', color='white')
            
            plt.tight_layout()
            
            buffer = BytesIO()
            plt.savefig(buffer, format='png', dpi=200, bbox_inches='tight', facecolor='#f8f9fa')
            buffer.seek(0)
            plt.close()
            
            return buffer
            
        except Exception as e:
            return None
    
    def _generar_grafica_tipos_acciones(self, acciones_data):
        """Genera gráfica de tipos de acciones"""
        try:
            tipos_counts = {}
            for accion in acciones_data:
                tipo = accion.get('tipo_accion', 'Otro')
                tipos_counts[tipo] = tipos_counts.get(tipo, 0) + 1
            
            if not tipos_counts:
                return None
            
            fig, ax = plt.subplots(figsize=(8, 5))
            fig.patch.set_facecolor('#f8f9fa')
            ax.set_facecolor('#ffffff')
            
            import matplotlib.cm as cm
            colors_map = cm.get_cmap('Set3')(np.linspace(0, 1, len(tipos_counts)))
            
            labels = list(tipos_counts.keys())
            valores = list(tipos_counts.values())
            
            bars = ax.bar(labels, valores, color=colors_map, edgecolor='white', 
                          linewidth=3, width=0.7, alpha=0.85)
            
            ax.set_ylabel('Cantidad', fontsize=13, fontweight='bold', color='#333')
            ax.set_title('📈 Tipos de Acciones', fontsize=16, fontweight='bold', pad=25, color='#2d5a3d')
            ax.grid(axis='y', alpha=0.4, linestyle='--', linewidth=1.5)
            plt.xticks(rotation=45, ha='right', fontsize=11, fontweight='bold')
            ax.spines['top'].set_visible(False)
            ax.spines['right'].set_visible(False)
            ax.spines['left'].set_linewidth(2)
            ax.spines['bottom'].set_linewidth(2)
            
            max_val = max(valores) if valores else 1
            for bar, valor in zip(bars, valores):
                height = bar.get_height()
                ax.text(bar.get_x() + bar.get_width()/2., height + max_val * 0.02,
                       f'{int(valor)}',
                       ha='center', va='bottom', fontsize=12, fontweight='bold', color='#2d5a3d')
            
            plt.tight_layout()
            
            buffer = BytesIO()
            plt.savefig(buffer, format='png', dpi=200, bbox_inches='tight', facecolor='#f8f9fa')
            buffer.seek(0)
            plt.close()
            
            return buffer
            
        except Exception as e:
            return None
    
    def _generar_grafica_montos_pagados(self, acciones_data):
        """Genera gráfica de distribución de montos pagados"""
        try:
            rangos = {'0-1000': 0, '1000-5000': 0, '5000-10000': 0, '10000+': 0}
            
            for accion in acciones_data:
                estado_pagos = accion.get('estado_pagos', {})
                total_pagado = float(estado_pagos.get('total_pagado', 0))
                
                if total_pagado <= 1000:
                    rangos['0-1000'] += 1
                elif total_pagado <= 5000:
                    rangos['1000-5000'] += 1
                elif total_pagado <= 10000:
                    rangos['5000-10000'] += 1
                else:
                    rangos['10000+'] += 1
            
            fig, ax = plt.subplots(figsize=(8, 5))
            fig.patch.set_facecolor('#f8f9fa')
            ax.set_facecolor('#ffffff')
            
            labels = list(rangos.keys())
            valores = list(rangos.values())
            colores = ['#2d5a3d', '#1e88e5', '#f57c00', '#d32f2f']
            
            bars = ax.barh(labels, valores, color=colores, edgecolor='white', 
                          linewidth=3, height=0.7, alpha=0.85)
            
            ax.set_xlabel('Cantidad de Acciones', fontsize=13, fontweight='bold', color='#333')
            ax.set_title('💰 Distribución de Montos Pagados', fontsize=16, fontweight='bold', 
                        pad=25, color='#2d5a3d')
            ax.grid(axis='x', alpha=0.4, linestyle='--', linewidth=1.5)
            ax.spines['top'].set_visible(False)
            ax.spines['right'].set_visible(False)
            ax.spines['left'].set_linewidth(2)
            ax.spines['bottom'].set_linewidth(2)
            
            max_val = max(valores) if valores else 1
            for bar, valor in zip(bars, valores):
                if valor > 0:
                    ax.text(valor + max_val * 0.02, bar.get_y() + bar.get_height()/2,
                           f'{int(valor)}',
                           ha='left', va='center', fontsize=13, fontweight='bold', color='#2d5a3d')
            
            plt.tight_layout()
            
            buffer = BytesIO()
            plt.savefig(buffer, format='png', dpi=200, bbox_inches='tight', facecolor='#f8f9fa')
            buffer.seek(0)
            plt.close()
            
            return buffer
            
        except Exception as e:
            return None
    
    def _generar_grafica_top_acciones(self, acciones_data):
        """Genera gráfica de top 10 acciones con mayor monto"""
        try:
            acciones_con_monto = []
            for accion in acciones_data:
                estado_pagos = accion.get('estado_pagos', {})
                precio_inicial = float(estado_pagos.get('precio_inicial', 0))
                if precio_inicial > 0:
                    acciones_con_monto.append((
                        accion.get('socio_titular', 'Socio')[:20],
                        precio_inicial
                    ))
            
            acciones_con_monto = sorted(acciones_con_monto, key=lambda x: x[1], reverse=True)[:10]
            
            if not acciones_con_monto:
                return None
            
            fig, ax = plt.subplots(figsize=(10, 6))
            fig.patch.set_facecolor('#f8f9fa')
            ax.set_facecolor('#ffffff')
            
            nombres = [a[0] for a in acciones_con_monto]
            montos = [a[1] for a in acciones_con_monto]
            
            colors_gradient = plt.cm.Greens(np.linspace(0.3, 0.9, len(nombres)))
            
            bars = ax.barh(range(len(nombres)), montos, color=colors_gradient, 
                          edgecolor='white', linewidth=2.5, height=0.7, alpha=0.85)
            
            ax.set_yticks(range(len(nombres)))
            ax.set_yticklabels(nombres, fontsize=10, fontweight='bold')
            ax.set_xlabel('Monto Total (Bs)', fontsize=13, fontweight='bold', color='#333')
            ax.set_title('🏆 Top 10 Acciones con Mayor Monto', fontsize=16, fontweight='bold', 
                        pad=25, color='#2d5a3d')
            ax.grid(axis='x', alpha=0.4, linestyle='--', linewidth=1.5)
            ax.spines['top'].set_visible(False)
            ax.spines['right'].set_visible(False)
            ax.spines['left'].set_linewidth(2)
            ax.spines['bottom'].set_linewidth(2)
            
            max_val = max(montos)
            for bar, valor in zip(bars, montos):
                if valor > 0:
                    ax.text(valor + max_val * 0.02, bar.get_y() + bar.get_height()/2,
                           f'{int(valor)}',
                           ha='left', va='center', fontsize=11, fontweight='bold', color='#2d5a3d')
            
            plt.tight_layout()
            
            buffer = BytesIO()
            plt.savefig(buffer, format='png', dpi=200, bbox_inches='tight', facecolor='#f8f9fa')
            buffer.seek(0)
            plt.close()
            
            return buffer
            
        except Exception as e:
            return None
    
    def _generar_grafica_progreso_mensual(self, acciones_data):
        """Genera gráfica de progreso de pagos mensual"""
        try:
            from datetime import datetime
            meses = {}
            
            for accion in acciones_data:
                fecha_venta = accion.get('fecha_venta')
                if fecha_venta:
                    try:
                        if isinstance(fecha_venta, str):
                            fecha_obj = datetime.strptime(fecha_venta.split()[0], '%Y-%m-%d')
                        else:
                            fecha_obj = fecha_venta
                        
                        mes_anio = f"{fecha_obj.strftime('%Y-%m')}"
                        if mes_anio not in meses:
                            meses[mes_anio] = 0
                        meses[mes_anio] += 1
                    except:
                        continue
            
            if not meses:
                return None
            
            fechas_ordenadas = sorted(meses.keys())
            valores = [meses[f] for f in fechas_ordenadas]
            fechas_format = [datetime.strptime(f, '%Y-%m').strftime('%b %Y') for f in fechas_ordenadas]
            
            fig, ax = plt.subplots(figsize=(10, 5))
            fig.patch.set_facecolor('#f8f9fa')
            ax.set_facecolor('#ffffff')
            
            ax.plot(fechas_format, valores, marker='o', color='#2d5a3d', linewidth=3, 
                   markersize=10, markerfacecolor='#2d5a3d', markeredgecolor='white', 
                   markeredgewidth=2)
            ax.fill_between(fechas_format, valores, alpha=0.4, color='#2d5a3d')
            
            for x, y in zip(fechas_format, valores):
                ax.text(x, y + 0.3, f'{int(y)}', ha='center', va='bottom', 
                       fontsize=11, fontweight='bold', color='#2d5a3d')
            
            ax.set_xlabel('Mes', fontsize=13, fontweight='bold', color='#333')
            ax.set_ylabel('Acciones Creadas', fontsize=13, fontweight='bold', color='#333')
            ax.set_title('📈 Progreso de Acciones Mensual', fontsize=16, fontweight='bold', 
                        pad=25, color='#2d5a3d')
            ax.grid(alpha=0.4, linestyle='--', linewidth=1.5)
            ax.spines['top'].set_visible(False)
            ax.spines['right'].set_visible(False)
            ax.spines['left'].set_linewidth(2)
            ax.spines['bottom'].set_linewidth(2)
            plt.xticks(rotation=45, ha='right', fontsize=11, fontweight='bold')
            
            plt.tight_layout()
            
            buffer = BytesIO()
            plt.savefig(buffer, format='png', dpi=200, bbox_inches='tight', facecolor='#f8f9fa')
            buffer.seek(0)
            plt.close()
            
            return buffer
            
        except Exception as e:
            return None

