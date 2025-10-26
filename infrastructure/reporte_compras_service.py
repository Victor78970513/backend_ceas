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
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.backends.backend_agg import FigureCanvasAgg
import numpy as np
import psycopg2
from config import DATABASE_URL

class ReporteComprasService:
    """
    Servicio para generar reportes de compras y proveedores
    """
    
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()
    
    def _setup_custom_styles(self):
        """Configura estilos personalizados"""
        self.styles.add(ParagraphStyle(
            name='Titulo',
            parent=self.styles['Title'],
            fontSize=20,
            spaceAfter=30,
            alignment=TA_CENTER,
            textColor=colors.HexColor('#2d5a3d')
        ))
        
        self.styles.add(ParagraphStyle(
            name='Subtitulo',
            parent=self.styles['Heading1'],
            fontSize=14,
            spaceAfter=12,
            textColor=colors.HexColor('#2d5a3d')
        ))
        
        self.styles.add(ParagraphStyle(
            name='TextoNormal',
            parent=self.styles['Normal'],
            fontSize=10,
            spaceAfter=6,
            textColor=colors.black
        ))
        
        self.styles.add(ParagraphStyle(
            name='TextoPequeño',
            parent=self.styles['Normal'],
            fontSize=9,
            spaceAfter=10,
            alignment=TA_CENTER,
            textColor=colors.grey
        ))

    def generar_pdf_compras(self, compras_data, proveedores_data):
        """
        Genera un reporte completo de compras y proveedores
        """
        buffer = BytesIO()
        
        # Crear documento PDF
        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            rightMargin=2*cm,
            leftMargin=2*cm,
            topMargin=2*cm,
            bottomMargin=2*cm
        )
        
        story = []
        
        # Título
        titulo = Paragraph("📦 REPORTE DE COMPRAS Y PROVEEDORES", self.styles['Titulo'])
        story.append(titulo)
        
        subtitulo = Paragraph(
            f"Club de Emprendedores y Accionistas<br/>"
            f"Reporte del {datetime.now().strftime('%d/%m/%Y')}",
            self.styles['TextoNormal']
        )
        story.append(subtitulo)
        story.append(Spacer(1, 0.3*cm))
        
        fecha_gen = Paragraph(
            f"<i>Generado el {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}</i>",
            self.styles['TextoPequeño']
        )
        story.append(fecha_gen)
        story.append(Spacer(1, 0.5*cm))
        
        # Resumen general
        total_compras = sum([compra.get('monto_total', 0) for compra in compras_data])
        total_proveedores = len(proveedores_data)
        compras_pendientes = len([c for c in compras_data if c.get('estado') == 'pendiente'])
        
        info_general = Paragraph(
            f"<b>Resumen:</b> {len(compras_data)} compras registradas | "
            f"Monto total: Bs. {total_compras:,.2f} | "
            f"{total_proveedores} proveedores activos | "
            f"{compras_pendientes} compras pendientes",
            self.styles['TextoNormal']
        )
        story.append(info_general)
        story.append(Spacer(1, 0.3*cm))
        
        # TABLA DE COMPRAS
        story.append(Paragraph("Listado de Compras", self.styles['Subtitulo']))
        story.append(Spacer(1, 0.2*cm))
        
        if compras_data:
            # Preparar datos de la tabla
            data = [['ID', 'Fecha', 'Proveedor', 'Categoría', 'Monto', 'Estado']]
            
            for compra in compras_data[:50]:  # Limitar a 50 para evitar desbordamiento
                fecha = compra.get('fecha_de_compra', 'N/A')
                if fecha:
                    try:
                        fecha_obj = datetime.fromisoformat(str(fecha))
                        fecha_str = fecha_obj.strftime('%d/%m/%Y')
                    except:
                        fecha_str = str(fecha)[:10]
                else:
                    fecha_str = 'N/A'
                
                proveedor = (compra.get('proveedor', 'N/A') or 'N/A')[:20]
                categoria = (compra.get('categoria_proveedor', 'N/A') or 'N/A')[:15]
                monto = float(compra.get('monto_total', 0))
                estado = (compra.get('estado', 'N/A') or 'N/A')[:10]
                
                data.append([
                    str(compra.get('id_compra', 'N/A')),
                    fecha_str,
                    proveedor,
                    categoria,
                    f"Bs. {monto:,.2f}",
                    estado
                ])
            
            tabla = Table(data, colWidths=[1.5*cm, 2.5*cm, 5*cm, 3*cm, 2.5*cm, 2.5*cm])
            tabla.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2d5a3d')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('ALIGN', (4, 0), (-1, -1), 'RIGHT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 9),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
                ('TOPPADDING', (0, 0), (-1, 0), 8),
                ('FONTSIZE', (0, 1), (-1, -1), 8),
                ('GRID', (0, 0), (-1, -1), 1, colors.grey),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f0f0f0')]),
            ]))
            
            story.append(tabla)
        else:
            story.append(Paragraph("No hay compras registradas", self.styles['TextoNormal']))
        
        story.append(PageBreak())
        
        # TABLA DE PROVEEDORES
        story.append(Paragraph("Listado de Proveedores", self.styles['Subtitulo']))
        story.append(Spacer(1, 0.2*cm))
        
        if proveedores_data:
            data = [['ID', 'Proveedor', 'Contacto', 'Teléfono', 'Categoría', 'Estado']]
            
            for proveedor in proveedores_data:
                contacto = (proveedor.get('contacto', 'N/A') or 'N/A')[:20]
                telefono = (proveedor.get('telefono', 'N/A') or 'N/A')[:15]
                categoria = (proveedor.get('categoria', 'N/A') or 'N/A')[:15]
                estado = 'Activo' if proveedor.get('estado', False) else 'Inactivo'
                
                data.append([
                    str(proveedor.get('id_proveedor', 'N/A')),
                    proveedor.get('nombre_proveedor', 'N/A')[:25],
                    contacto,
                    telefono,
                    categoria,
                    estado
                ])
            
            tabla = Table(data, colWidths=[1.5*cm, 5*cm, 4*cm, 3*cm, 3*cm, 2.5*cm])
            tabla.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2d5a3d')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 9),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
                ('TOPPADDING', (0, 0), (-1, 0), 8),
                ('FONTSIZE', (0, 1), (-1, -1), 8),
                ('GRID', (0, 0), (-1, -1), 1, colors.grey),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f0f0f0')]),
            ]))
            
            story.append(tabla)
        
        story.append(PageBreak())
        
        # GRÁFICAS
        story.append(Paragraph("Análisis y Gráficas", self.styles['Subtitulo']))
        story.append(Spacer(1, 0.3*cm))
        
        # Gráfica 1: Compras por estado
        grafica_estado = self._generar_grafica_compras_por_estado(compras_data)
        if grafica_estado:
            img = Image(grafica_estado, width=16*cm, height=10*cm)
            story.append(img)
            desc = Paragraph(
                "Distribución de compras según su estado (pendiente, completado, etc.)",
                self.styles['TextoNormal']
            )
            story.append(desc)
            story.append(Spacer(1, 0.5*cm))
        
        # Gráfica 2: Compras por proveedor
        grafica_proveedor = self._generar_grafica_compras_por_proveedor(compras_data)
        if grafica_proveedor:
            img = Image(grafica_proveedor, width=16*cm, height=10*cm)
            story.append(img)
            desc = Paragraph(
                "Top 10 proveedores con mayor volumen de compras",
                self.styles['TextoNormal']
            )
            story.append(desc)
            story.append(Spacer(1, 0.5*cm))
        
        # Gráfica 3: Compras por categoría
        grafica_categoria = self._generar_grafica_compras_por_categoria(compras_data)
        if grafica_categoria:
            img = Image(grafica_categoria, width=14*cm, height=12*cm)
            story.append(img)
            desc = Paragraph(
                "Distribución de compras por categoría de proveedor",
                self.styles['TextoNormal']
            )
            story.append(desc)
            story.append(Spacer(1, 0.5*cm))
        
        # Gráfica 4: Evolución mensual de compras
        grafica_evolucion = self._generar_grafica_evolucion_compras(compras_data)
        if grafica_evolucion:
            img = Image(grafica_evolucion, width=16*cm, height=9*cm)
            story.append(img)
            desc = Paragraph(
                "Evolución temporal de las compras en los últimos meses",
                self.styles['TextoNormal']
            )
            story.append(desc)
        
        # Generar PDF
        doc.build(story, onFirstPage=self._agregar_header_footer, onLaterPages=self._agregar_header_footer)
        
        buffer.seek(0)
        return buffer.getvalue()
    
    def _generar_grafica_compras_por_estado(self, compras_data):
        """Genera gráfica de compras por estado"""
        try:
            estados = {}
            for compra in compras_data:
                estado = compra.get('estado', 'N/A')
                estados[estado] = estados.get(estado, 0) + 1
            
            if not estados:
                return None
            
            fig, ax = plt.subplots(figsize=(8, 6))
            fig.patch.set_facecolor('#f8f9fa')
            
            estados_list = list(estados.keys())
            cantidades = list(estados.values())
            colores = ['#2d5a3d', '#d32f2f', '#1e88e5', '#f57c00', '#6a1b9a']
            
            bars = ax.bar(estados_list, cantidades, color=colores[:len(estados_list)], edgecolor='white', linewidth=2)
            
            ax.set_title('📊 Compras por Estado', fontsize=16, fontweight='bold', color='#2d5a3d', pad=20)
            ax.set_ylabel('Cantidad', fontsize=12, fontweight='bold')
            ax.grid(axis='y', alpha=0.3)
            
            for bar in bars:
                height = bar.get_height()
                ax.text(bar.get_x() + bar.get_width()/2., height,
                       f'{int(height)}',
                       ha='center', va='bottom', fontsize=11, fontweight='bold')
            
            plt.tight_layout()
            
            buffer = BytesIO()
            plt.savefig(buffer, format='png', dpi=150, bbox_inches='tight')
            buffer.seek(0)
            plt.close()
            
            return buffer
            
        except Exception as e:
            print(f"Error generando gráfica de estados: {e}")
            return None
    
    def _generar_grafica_compras_por_proveedor(self, compras_data):
        """Genera gráfica de compras por proveedor"""
        try:
            proveedores = {}
            for compra in compras_data:
                proveedor = compra.get('proveedor', 'N/A')
                monto = float(compra.get('monto_total', 0))
                if proveedor not in proveedores:
                    proveedores[proveedor] = 0
                proveedores[proveedor] += monto
            
            # Ordenar y tomar top 10
            top_proveedores = sorted(proveedores.items(), key=lambda x: x[1], reverse=True)[:10]
            
            if not top_proveedores:
                return None
            
            nombres = [p[0][:20] for p in top_proveedores]
            montos = [p[1] for p in top_proveedores]
            
            fig, ax = plt.subplots(figsize=(10, 6))
            fig.patch.set_facecolor('#f8f9fa')
            
            colors_gradient = plt.cm.Greens(np.linspace(0.3, 0.9, len(nombres)))
            bars = ax.barh(nombres, montos, color=colors_gradient)
            
            ax.set_xlabel('Monto Total (Bs)', fontsize=12, fontweight='bold')
            ax.set_title('🏆 Top 10 Proveedores por Volumen de Compras', fontsize=16, fontweight='bold', color='#2d5a3d', pad=20)
            ax.grid(axis='x', alpha=0.3)
            
            for i, (bar, monto) in enumerate(zip(bars, montos)):
                width = bar.get_width()
                ax.text(width + max(montos) * 0.01, bar.get_y() + bar.get_height()/2,
                       f'Bs. {monto:,.0f}',
                       ha='left', va='center', fontsize=9, fontweight='bold')
            
            plt.tight_layout()
            
            buffer = BytesIO()
            plt.savefig(buffer, format='png', dpi=150, bbox_inches='tight')
            buffer.seek(0)
            plt.close()
            
            return buffer
            
        except Exception as e:
            print(f"Error generando gráfica de proveedores: {e}")
            return None
    
    def _generar_grafica_compras_por_categoria(self, compras_data):
        """Genera gráfica circular de compras por categoría"""
        try:
            categorias = {}
            for compra in compras_data:
                categoria = compra.get('categoria_proveedor', 'N/A')
                monto = float(compra.get('monto_total', 0))
                if categoria not in categorias:
                    categorias[categoria] = 0
                categorias[categoria] += monto
            
            if not categorias:
                return None
            
            categorias_list = list(categorias.keys())
            montos = list(categorias.values())
            
            fig, ax = plt.subplots(figsize=(8, 8))
            fig.patch.set_facecolor('#f8f9fa')
            
            colores = ['#2d5a3d', '#1e88e5', '#f57c00', '#c62828', '#6a1b9a', '#00897b', '#ff5722', '#4caf50']
            explode = tuple([0.05] * len(categorias_list))
            
            wedges, texts, autotexts = ax.pie(
                montos,
                labels=categorias_list,
                colors=colores[:len(categorias_list)],
                autopct='%1.1f%%',
                startangle=90,
                explode=explode,
                shadow=True,
                textprops={'fontsize': 11, 'fontweight': 'bold'}
            )
            
            ax.set_title('📦 Distribución por Categoría', fontsize=16, fontweight='bold', color='#2d5a3d', pad=30)
            
            for autotext in autotexts:
                autotext.set_color('#ffffff')
                autotext.set_fontsize(12)
                autotext.set_fontweight('bold')
            
            plt.tight_layout()
            
            buffer = BytesIO()
            plt.savefig(buffer, format='png', dpi=150, bbox_inches='tight')
            buffer.seek(0)
            plt.close()
            
            return buffer
            
        except Exception as e:
            print(f"Error generando gráfica de categorías: {e}")
            return None
    
    def _generar_grafica_evolucion_compras(self, compras_data):
        """Genera gráfica de evolución mensual de compras"""
        try:
            meses = {}
            for compra in compras_data:
                fecha = compra.get('fecha_de_compra')
                if not fecha:
                    continue
                
                try:
                    fecha_obj = datetime.fromisoformat(str(fecha))
                    mes = fecha_obj.strftime('%Y-%m')
                except:
                    continue
                
                monto = float(compra.get('monto_total', 0))
                if mes not in meses:
                    meses[mes] = 0
                meses[mes] += monto
            
            if not meses:
                return None
            
            # Ordenar por mes
            meses_ordenados = sorted(meses.items())
            fechas = [m[0] for m in meses_ordenados[-12:]]  # Últimos 12 meses
            valores = [m[1] for m in meses_ordenados[-12:]]
            
            fig, ax = plt.subplots(figsize=(10, 6))
            fig.patch.set_facecolor('#f8f9fa')
            
            ax.plot(fechas, valores, marker='o', color='#2d5a3d', linewidth=3, markersize=10)
            ax.fill_between(fechas, valores, alpha=0.4, color='#2d5a3d')
            
            ax.set_xlabel('Mes', fontsize=12, fontweight='bold')
            ax.set_ylabel('Monto (Bs)', fontsize=12, fontweight='bold')
            ax.set_title('📈 Evolución Mensual de Compras', fontsize=16, fontweight='bold', color='#2d5a3d', pad=20)
            ax.grid(alpha=0.3)
            ax.tick_params(axis='x', rotation=45)
            
            for x, y in zip(fechas, valores):
                ax.text(x, y + max(valores) * 0.02, f'Bs. {y:,.0f}',
                       ha='center', va='bottom', fontsize=9, fontweight='bold')
            
            plt.tight_layout()
            
            buffer = BytesIO()
            plt.savefig(buffer, format='png', dpi=150, bbox_inches='tight')
            buffer.seek(0)
            plt.close()
            
            return buffer
            
        except Exception as e:
            print(f"Error generando gráfica de evolución: {e}")
            return None
    
    def _agregar_header_footer(self, canvas, doc):
        """Agrega encabezado y pie de página"""
        canvas.saveState()
        canvas.setFont('Helvetica', 9)
        canvas.drawString(cm, cm, f"Reporte de Compras - Página {doc.page}")
        canvas.restoreState()
