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

class ReporteFinanzasService:
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
    
    def generar_pdf_finanzas(self, movimientos_data):
        """Genera un PDF con el reporte de finanzas"""
        try:
            buffer = BytesIO()
            doc = SimpleDocTemplate(buffer, pagesize=A4, 
                                    rightMargin=50, leftMargin=50,
                                    topMargin=50, bottomMargin=50)
            
            story = []
            
            # Título del reporte
            titulo = Paragraph("Reporte de Finanzas - CEAS", self.styles['TituloReporte'])
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
            total_movimientos = len(movimientos_data)
            total_ingresos = sum([float(m.get('monto', 0)) for m in movimientos_data if m.get('tipo_movimiento') == 'INGRESO'])
            total_egresos = sum([float(m.get('monto', 0)) for m in movimientos_data if m.get('tipo_movimiento') == 'EGRESO'])
            balance = total_ingresos - total_egresos
            
            info_general = Paragraph(
                f"<b>Total movimientos:</b> {total_movimientos} | <b>Ingresos:</b> {total_ingresos:.2f} Bs | <b>Egresos:</b> {total_egresos:.2f} Bs | <b>Balance:</b> {balance:.2f} Bs",
                self.styles['TextoNormal']
            )
            story.append(info_general)
            story.append(Spacer(1, 0.5*cm))
            
            # Subtítulo para la tabla de datos
            subtitulo_tabla = Paragraph("Listado de Movimientos Financieros", self.styles['Subtitulo'])
            story.append(subtitulo_tabla)
            story.append(Spacer(1, 0.3*cm))
            
            # Tabla de movimientos (horizontal compacta)
            if movimientos_data:
                data = [['Fecha', 'Tipo', 'Descripción', 'Monto', 'Estado', 'Método']]
                
                for mov in movimientos_data:
                    fecha = mov.get('fecha', 'N/A')[:10]
                    tipo = mov.get('tipo_movimiento', 'N/A')[:10]
                    descripcion = mov.get('descripcion', 'N/A')[:30]
                    monto = f"{float(mov.get('monto', 0)):.2f}"
                    estado = mov.get('estado', 'N/A')[:10]
                    metodo = mov.get('metodo_pago', 'N/A')[:15]
                    
                    row = [fecha, tipo, descripcion, monto, estado, metodo]
                    data.append(row)
                
                # Crear tabla
                tabla = Table(data, colWidths=[3.5*cm, 3*cm, 5.5*cm, 3*cm, 2.5*cm, 3*cm])
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
                story.append(Paragraph("<b>No hay movimientos registrados</b>", self.styles['TextoNormal']))
            
            # Agregar salto de página para las gráficas
            story.append(PageBreak())
            
            # Subtítulo para las gráficas
            subtitulo_graficas = Paragraph("Análisis y Gráficas", self.styles['Subtitulo'])
            story.append(subtitulo_graficas)
            story.append(Spacer(1, 0.3*cm))
            
            # Gráfica 1: Ingresos vs Egresos
            grafica_balance = self._generar_grafica_balance(movimientos_data)
            if grafica_balance:
                img_balance = Image(grafica_balance, width=16*cm, height=10*cm)
                story.append(img_balance)
                desc_balance = Paragraph(
                    "Comparación entre ingresos y egresos del club. Verde representa ingresos y rojo egresos.",
                    self.styles['TextoNormal']
                )
                story.append(desc_balance)
                story.append(Spacer(1, 0.5*cm))
            
            # Gráfica 2: Categorías de movimientos
            grafica_categorias = self._generar_grafica_categorias(movimientos_data)
            if grafica_categorias:
                img_categorias = Image(grafica_categorias, width=16*cm, height=10*cm)
                story.append(img_categorias)
                desc_categorias = Paragraph(
                    "Distribución de movimientos por categoría (Cuotas, Donaciones, Compras, Servicios, etc.).",
                    self.styles['TextoNormal']
                )
                story.append(desc_categorias)
                story.append(Spacer(1, 0.5*cm))
            
            # Gráfica 3: Evolución mensual
            grafica_evolucion = self._generar_grafica_evolucion_mensual(movimientos_data)
            if grafica_evolucion:
                img_evolucion = Image(grafica_evolucion, width=16*cm, height=9*cm)
                story.append(img_evolucion)
                desc_evolucion = Paragraph(
                    "Evolución temporal de ingresos y egresos mes a mes.",
                    self.styles['TextoNormal']
                )
                story.append(desc_evolucion)
                story.append(Spacer(1, 0.5*cm))
            
            # Gráfica 4: Top 10 movimientos
            grafica_top = self._generar_grafica_top_movimientos(movimientos_data)
            if grafica_top:
                img_top = Image(grafica_top, width=16*cm, height=10*cm)
                story.append(img_top)
                desc_top = Paragraph(
                    "Ranking de los 10 movimientos de mayor monto, ordenados de mayor a menor.",
                    self.styles['TextoNormal']
                )
                story.append(desc_top)
                story.append(Spacer(1, 0.5*cm))
            
            # Gráfica 5: Distribución por métodos de pago
            grafica_metodos = self._generar_grafica_metodos_pago(movimientos_data)
            if grafica_metodos:
                img_metodos = Image(grafica_metodos, width=14*cm, height=12*cm)
                story.append(img_metodos)
                desc_metodos = Paragraph(
                    "Distribución de métodos de pago utilizados en los movimientos financieros.",
                    self.styles['TextoNormal']
                )
                story.append(desc_metodos)
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
            raise Exception(f"Error al generar PDF de finanzas: {str(e)}")
    
    def _agregar_pie_de_pagina(self, canvas, doc):
        """Agrega pie de página a cada página del PDF"""
        canvas.saveState()
        canvas.setFont('Helvetica', 9)
        canvas.drawString(cm, cm, f"Página {doc.page}")
        canvas.restoreState()
    
    def _generar_grafica_balance(self, movimientos_data):
        """Genera gráfica de balance ingresos vs egresos"""
        try:
            total_ingresos = sum([float(m.get('monto', 0)) for m in movimientos_data if m.get('tipo_movimiento') == 'INGRESO'])
            total_egresos = sum([float(m.get('monto', 0)) for m in movimientos_data if m.get('tipo_movimiento') == 'EGRESO'])
            
            fig, ax = plt.subplots(figsize=(7, 5))
            fig.patch.set_facecolor('#f8f9fa')
            ax.set_facecolor('#ffffff')
            
            categorias = ['Ingresos', 'Egresos']
            valores = [total_ingresos, total_egresos]
            colores = ['#2d5a3d', '#d32f2f']
            
            bars = ax.bar(categorias, valores, color=colores, edgecolor='white', 
                          linewidth=3, width=0.6, alpha=0.85)
            
            ax.set_ylabel('Monto (Bs)', fontsize=13, fontweight='bold', color='#333')
            ax.set_title('💰 Ingresos vs Egresos', fontsize=16, fontweight='bold', 
                        pad=25, color='#2d5a3d')
            ax.grid(axis='y', alpha=0.4, linestyle='--', linewidth=1.5)
            ax.spines['top'].set_visible(False)
            ax.spines['right'].set_visible(False)
            ax.spines['left'].set_linewidth(2)
            ax.spines['bottom'].set_linewidth(2)
            
            # Agregar valores grandes
            max_val = max(valores)
            for bar, valor in zip(bars, valores):
                height = bar.get_height()
                ax.text(bar.get_x() + bar.get_width()/2., height + max_val * 0.02,
                       f'{valor:,.0f} Bs',
                       ha='center', va='bottom', fontsize=13, fontweight='bold', color='#333')
            
            plt.tight_layout()
            
            buffer = BytesIO()
            plt.savefig(buffer, format='png', dpi=200, bbox_inches='tight', facecolor='#f8f9fa')
            buffer.seek(0)
            plt.close()
            
            return buffer
            
        except Exception as e:
            return None
    
    def _generar_grafica_categorias(self, movimientos_data):
        """Genera gráfica de distribución de categorías"""
        try:
            categorias_counts = {}
            for mov in movimientos_data:
                categoria = mov.get('categoria', 'Otros')
                if categoria not in categorias_counts:
                    categorias_counts[categoria] = {'ingresos': 0, 'egresos': 0}
                
                if mov.get('tipo_movimiento') == 'INGRESO':
                    categorias_counts[categoria]['ingresos'] += float(mov.get('monto', 0))
                else:
                    categorias_counts[categoria]['egresos'] += float(mov.get('monto', 0))
            
            if not categorias_counts:
                return None
            
            # Preparar datos para gráfica de barras agrupadas
            fig, ax = plt.subplots(figsize=(10, 6))
            fig.patch.set_facecolor('#f8f9fa')
            ax.set_facecolor('#ffffff')
            
            labels = list(categorias_counts.keys())
            ingresos = [categorias_counts[c]['ingresos'] for c in labels]
            egresos = [categorias_counts[c]['egresos'] for c in labels]
            
            x = np.arange(len(labels))
            width = 0.35
            
            bars1 = ax.bar(x - width/2, ingresos, width, label='Ingresos', color='#2d5a3d', alpha=0.85)
            bars2 = ax.bar(x + width/2, egresos, width, label='Egresos', color='#d32f2f', alpha=0.85)
            
            ax.set_ylabel('Monto (Bs)', fontsize=13, fontweight='bold', color='#333')
            ax.set_title('📊 Distribución por Categorías', fontsize=16, fontweight='bold', 
                        pad=25, color='#2d5a3d')
            ax.set_xticks(x)
            ax.set_xticklabels(labels, rotation=45, ha='right', fontsize=11, fontweight='bold')
            ax.legend(fontsize=12, loc='upper right')
            ax.grid(axis='y', alpha=0.4, linestyle='--', linewidth=1.5)
            ax.spines['top'].set_visible(False)
            ax.spines['right'].set_visible(False)
            ax.spines['left'].set_linewidth(2)
            ax.spines['bottom'].set_linewidth(2)
            
            plt.tight_layout()
            
            buffer = BytesIO()
            plt.savefig(buffer, format='png', dpi=200, bbox_inches='tight', facecolor='#f8f9fa')
            buffer.seek(0)
            plt.close()
            
            return buffer
            
        except Exception as e:
            return None
    
    def _generar_grafica_evolucion_mensual(self, movimientos_data):
        """Genera gráfica de evolución mensual"""
        try:
            meses = {}
            
            for mov in movimientos_data:
                fecha = mov.get('fecha')
                if fecha:
                    try:
                        if isinstance(fecha, str):
                            fecha_obj = datetime.strptime(fecha.split()[0], '%Y-%m-%d')
                        else:
                            fecha_obj = fecha
                        
                        mes_anio = f"{fecha_obj.strftime('%Y-%m')}"
                        if mes_anio not in meses:
                            meses[mes_anio] = {'ingresos': 0, 'egresos': 0}
                        
                        if mov.get('tipo_movimiento') == 'INGRESO':
                            meses[mes_anio]['ingresos'] += float(mov.get('monto', 0))
                        else:
                            meses[mes_anio]['egresos'] += float(mov.get('monto', 0))
                    except:
                        continue
            
            if not meses:
                return None
            
            fechas_ordenadas = sorted(meses.keys())
            ingresos = [meses[f]['ingresos'] for f in fechas_ordenadas]
            egresos = [meses[f]['egresos'] for f in fechas_ordenadas]
            fechas_format = [datetime.strptime(f, '%Y-%m').strftime('%b %Y') for f in fechas_ordenadas]
            
            fig, ax = plt.subplots(figsize=(12, 6))
            fig.patch.set_facecolor('#f8f9fa')
            ax.set_facecolor('#ffffff')
            
            ax.plot(fechas_format, ingresos, marker='o', color='#2d5a3d', linewidth=3, 
                   markersize=10, label='Ingresos', markeredgecolor='white', markeredgewidth=2)
            ax.plot(fechas_format, egresos, marker='s', color='#d32f2f', linewidth=3, 
                   markersize=10, label='Egresos', markeredgecolor='white', markeredgewidth=2)
            
            ax.fill_between(fechas_format, ingresos, alpha=0.3, color='#2d5a3d')
            ax.fill_between(fechas_format, egresos, alpha=0.3, color='#d32f2f')
            
            ax.set_xlabel('Mes', fontsize=13, fontweight='bold', color='#333')
            ax.set_ylabel('Monto (Bs)', fontsize=13, fontweight='bold', color='#333')
            ax.set_title('📈 Evolución Financiera Mensual', fontsize=16, fontweight='bold', 
                        pad=25, color='#2d5a3d')
            ax.grid(alpha=0.4, linestyle='--', linewidth=1.5)
            ax.legend(fontsize=12, loc='upper left')
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
    
    def _generar_grafica_top_movimientos(self, movimientos_data):
        """Genera gráfica de top 10 movimientos"""
        try:
            # Ordenar por monto descendente
            movimientos_sorted = sorted(movimientos_data, 
                                       key=lambda x: float(x.get('monto', 0)), 
                                       reverse=True)[:10]
            
            if not movimientos_sorted:
                return None
            
            descripciones = [m.get('descripcion', 'Movimiento')[:20] for m in movimientos_sorted]
            montos = [float(m.get('monto', 0)) for m in movimientos_sorted]
            
            fig, ax = plt.subplots(figsize=(10, 6))
            fig.patch.set_facecolor('#f8f9fa')
            ax.set_facecolor('#ffffff')
            
            colors_gradient = plt.cm.viridis(np.linspace(0.2, 0.8, len(descripciones)))
            
            bars = ax.barh(range(len(descripciones)), montos, color=colors_gradient, 
                          edgecolor='white', linewidth=2.5, height=0.7, alpha=0.85)
            
            ax.set_yticks(range(len(descripciones)))
            ax.set_yticklabels(descripciones, fontsize=10, fontweight='bold')
            ax.set_xlabel('Monto (Bs)', fontsize=13, fontweight='bold', color='#333')
            ax.set_title('🏆 Top 10 Movimientos Financieros', fontsize=16, fontweight='bold', 
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
                           f'{valor:,.0f}',
                           ha='left', va='center', fontsize=11, fontweight='bold', color='#2d5a3d')
            
            plt.tight_layout()
            
            buffer = BytesIO()
            plt.savefig(buffer, format='png', dpi=200, bbox_inches='tight', facecolor='#f8f9fa')
            buffer.seek(0)
            plt.close()
            
            return buffer
            
        except Exception as e:
            return None
    
    def _generar_grafica_metodos_pago(self, movimientos_data):
        """Genera gráfica circular de métodos de pago"""
        try:
            metodos_counts = {}
            for mov in movimientos_data:
                metodo = mov.get('metodo_pago', 'Otro')
                if metodo not in metodos_counts:
                    metodos_counts[metodo] = 0
                metodos_counts[metodo] += 1
            
            if not metodos_counts:
                return None
            
            fig, ax = plt.subplots(figsize=(9, 8))
            fig.patch.set_facecolor('#f8f9fa')
            
            labels = list(metodos_counts.keys())
            valores = list(metodos_counts.values())
            colores_pie = ['#2d5a3d', '#1e88e5', '#f57c00', '#c62828', '#6a1b9a', '#00897b', '#ff5722', '#4caf50']
            
            explode = tuple([0.05] * len(labels))
            
            wedges, texts, autotexts = ax.pie(
                valores, 
                labels=labels, 
                colors=colores_pie[:len(labels)],
                autopct='%1.1f%%',
                startangle=90, 
                explode=explode, 
                shadow=True,
                textprops={'fontsize': 12, 'fontweight': 'bold', 'color': '#333'}
            )
            
            ax.set_title('💳 Distribución de Métodos de Pago', fontsize=18, fontweight='bold', 
                        pad=30, color='#2d5a3d')
            
            for autotext in autotexts:
                autotext.set_color('#ffffff')
                autotext.set_fontsize(13)
                autotext.set_fontweight('bold')
                autotext.set_bbox(dict(boxstyle='round,pad=0.3', facecolor='#333', alpha=0.7))
            
            for text in texts:
                text.set_fontsize(13)
                text.set_fontweight('bold')
            
            plt.tight_layout()
            
            buffer = BytesIO()
            plt.savefig(buffer, format='png', dpi=200, bbox_inches='tight', facecolor='#f8f9fa')
            buffer.seek(0)
            plt.close()
            
            return buffer
            
        except Exception as e:
            return None

