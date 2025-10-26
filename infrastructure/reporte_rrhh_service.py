from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch, cm
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.pdfgen import canvas
from datetime import datetime, timedelta
from io import BytesIO
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.backends.backend_agg import FigureCanvasAgg
import numpy as np

class ReporteRRHHService:
    """
    Servicio para generar reportes de recursos humanos (personal y asistencia)
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

    def generar_pdf_rrhh(self, personal_data, asistencia_data):
        """
        Genera un reporte completo de recursos humanos
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
        titulo = Paragraph("👥 REPORTE DE RECURSOS HUMANOS", self.styles['Titulo'])
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
            self.styles['TextoNormal']
        )
        story.append(fecha_gen)
        story.append(Spacer(1, 0.5*cm))
        
        # Resumen general
        total_empleados = len(personal_data)
        empleados_activos = len([p for p in personal_data if p.get('estado') == 'ACTIVO'])
        total_asistencias = len(asistencia_data)
        total_nomina = sum([float(p.get('salario', 0)) for p in personal_data if p.get('estado') == 'ACTIVO'])
        
        info_general = Paragraph(
            f"<b>Resumen:</b> {total_empleados} empleados | "
            f"{empleados_activos} activos | "
            f"{total_asistencias} registros de asistencia | "
            f"Nómina total: Bs. {total_nomina:,.2f}",
            self.styles['TextoNormal']
        )
        story.append(info_general)
        story.append(Spacer(1, 0.3*cm))
        
        # TABLA DE EMPLEADOS
        story.append(Paragraph("Listado de Personal", self.styles['Subtitulo']))
        story.append(Spacer(1, 0.2*cm))
        
        if personal_data:
            data = [['ID', 'Nombre', 'Cargo', 'Depto', 'Estado', 'Salario']]
            
            for empleado in personal_data[:50]:  # Limitar a 50
                nombre = empleado.get('nombre_completo', 'N/A')[:25]
                cargo = empleado.get('cargo', 'N/A')[:20]
                depto = empleado.get('departamento', 'N/A')[:15]
                estado = empleado.get('estado', 'N/A')[:10]
                salario = float(empleado.get('salario', 0))
                
                data.append([
                    str(empleado.get('id_empleado', 'N/A')),
                    nombre,
                    cargo,
                    depto,
                    estado,
                    f"Bs. {salario:,.2f}"
                ])
            
            tabla = Table(data, colWidths=[1.5*cm, 5*cm, 4*cm, 3*cm, 2*cm, 2.5*cm])
            tabla.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2d5a3d')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('ALIGN', (5, 0), (-1, -1), 'RIGHT'),
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
            story.append(Paragraph("No hay personal registrado", self.styles['TextoNormal']))
        
        story.append(PageBreak())
        
        # TABLA DE ASISTENCIA (últimos registros)
        story.append(Paragraph("Registros de Asistencia (Últimos 50)", self.styles['Subtitulo']))
        story.append(Spacer(1, 0.2*cm))
        
        if asistencia_data:
            data = [['ID', 'Empleado', 'Fecha', 'Estado', 'Entrada', 'Salida']]
            
            # Tomar últimos 50
            for asistencia in asistencia_data[-50:]:
                empleado = asistencia.get('nombre_empleado', 'N/A')[:25]
                fecha = asistencia.get('fecha', 'N/A')
                estado = asistencia.get('estado', 'N/A')
                entrada = asistencia.get('hora_entrada', 'N/A')
                salida = asistencia.get('hora_salida', 'N/A')
                
                data.append([
                    str(asistencia.get('id_asistencia', 'N/A')),
                    empleado,
                    fecha[:10] if fecha else 'N/A',
                    estado,
                    str(entrada) if entrada else 'N/A',
                    str(salida) if salida else 'N/A'
                ])
            
            tabla = Table(data, colWidths=[1.5*cm, 6*cm, 2.5*cm, 2.5*cm, 2*cm, 2*cm])
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
        
        # Gráfica 1: Personal por departamento
        grafica_depto = self._generar_grafica_personal_por_departamento(personal_data)
        if grafica_depto:
            img = Image(grafica_depto, width=16*cm, height=10*cm)
            story.append(img)
            desc = Paragraph(
                "Distribución de empleados por departamento",
                self.styles['TextoNormal']
            )
            story.append(desc)
            story.append(Spacer(1, 0.5*cm))
        
        # Gráfica 2: Asistencia por estado
        grafica_estado = self._generar_grafica_asistencia_por_estado(asistencia_data)
        if grafica_estado:
            img = Image(grafica_estado, width=16*cm, height=10*cm)
            story.append(img)
            desc = Paragraph(
                "Distribución de asistencias por estado (presente, tardanza, ausente)",
                self.styles['TextoNormal']
            )
            story.append(desc)
            story.append(Spacer(1, 0.5*cm))
        
        # Gráfica 3: Nómina por departamento
        grafica_nomina = self._generar_grafica_nomina_por_departamento(personal_data)
        if grafica_nomina:
            img = Image(grafica_nomina, width=16*cm, height=10*cm)
            story.append(img)
            desc = Paragraph(
                "Distribución de la nómina total por departamento",
                self.styles['TextoNormal']
            )
            story.append(desc)
            story.append(Spacer(1, 0.5*cm))
        
        # Gráfica 4: Evolución de asistencia
        grafica_evolucion = self._generar_grafica_evolucion_asistencia(asistencia_data)
        if grafica_evolucion:
            img = Image(grafica_evolucion, width=16*cm, height=9*cm)
            story.append(img)
            desc = Paragraph(
                "Evolución mensual de registros de asistencia",
                self.styles['TextoNormal']
            )
            story.append(desc)
        
        # Generar PDF
        doc.build(story, onFirstPage=self._agregar_header_footer, onLaterPages=self._agregar_header_footer)
        
        buffer.seek(0)
        return buffer.getvalue()
    
    def _generar_grafica_personal_por_departamento(self, personal_data):
        """Genera gráfica de personal por departamento"""
        try:
            departamentos = {}
            for empleado in personal_data:
                depto = empleado.get('departamento', 'Sin Departamento')
                departamentos[depto] = departamentos.get(depto, 0) + 1
            
            if not departamentos:
                return None
            
            fig, ax = plt.subplots(figsize=(8, 6))
            fig.patch.set_facecolor('#f8f9fa')
            
            deptos_list = list(departamentos.keys())
            cantidades = list(departamentos.values())
            colores = ['#2d5a3d', '#1e88e5', '#f57c00', '#c62828', '#6a1b9a']
            
            bars = ax.bar(deptos_list, cantidades, color=colores[:len(deptos_list)], edgecolor='white', linewidth=2)
            
            ax.set_title('👥 Personal por Departamento', fontsize=16, fontweight='bold', color='#2d5a3d', pad=20)
            ax.set_ylabel('Cantidad de Empleados', fontsize=12, fontweight='bold')
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
            print(f"Error generando gráfica de departamentos: {e}")
            return None
    
    def _generar_grafica_asistencia_por_estado(self, asistencia_data):
        """Genera gráfica de asistencia por estado"""
        try:
            estados = {}
            for asistencia in asistencia_data:
                estado = asistencia.get('estado', 'N/A')
                estados[estado] = estados.get(estado, 0) + 1
            
            if not estados:
                return None
            
            fig, ax = plt.subplots(figsize=(8, 6))
            fig.patch.set_facecolor('#f8f9fa')
            
            estados_list = list(estados.keys())
            cantidades = list(estados.values())
            
            # Colores específicos para estados
            color_map = {
                'presente': '#2d5a3d',
                'tardanza': '#f57c00',
                'ausente': '#d32f2f'
            }
            colores = [color_map.get(e.lower(), '#1e88e5') for e in estados_list]
            
            bars = ax.bar(estados_list, cantidades, color=colores, edgecolor='white', linewidth=2)
            
            ax.set_title('📊 Asistencia por Estado', fontsize=16, fontweight='bold', color='#2d5a3d', pad=20)
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
    
    def _generar_grafica_nomina_por_departamento(self, personal_data):
        """Genera gráfica de nómina por departamento"""
        try:
            departamentos = {}
            for empleado in personal_data:
                if empleado.get('estado') == 'ACTIVO':
                    depto = empleado.get('departamento', 'Sin Departamento')
                    salario = float(empleado.get('salario', 0))
                    if depto not in departamentos:
                        departamentos[depto] = 0
                    departamentos[depto] += salario
            
            if not departamentos:
                return None
            
            deptos_list = list(departamentos.keys())
            montos = list(departamentos.values())
            
            fig, ax = plt.subplots(figsize=(10, 6))
            fig.patch.set_facecolor('#f8f9fa')
            
            colors_gradient = plt.cm.Blues(np.linspace(0.3, 0.9, len(deptos_list)))
            bars = ax.barh(deptos_list, montos, color=colors_gradient)
            
            ax.set_xlabel('Monto Total (Bs)', fontsize=12, fontweight='bold')
            ax.set_title('💰 Nómina por Departamento', fontsize=16, fontweight='bold', color='#2d5a3d', pad=20)
            ax.grid(axis='x', alpha=0.3)
            
            for bar, monto in zip(bars, montos):
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
            print(f"Error generando gráfica de nómina: {e}")
            return None
    
    def _generar_grafica_evolucion_asistencia(self, asistencia_data):
        """Genera gráfica de evolución de asistencia"""
        try:
            meses = {}
            for asistencia in asistencia_data:
                fecha = asistencia.get('fecha')
                if not fecha:
                    continue
                
                try:
                    fecha_obj = datetime.fromisoformat(str(fecha))
                    mes = fecha_obj.strftime('%Y-%m')
                except:
                    continue
                
                if mes not in meses:
                    meses[mes] = 0
                meses[mes] += 1
            
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
            ax.set_ylabel('Registros de Asistencia', fontsize=12, fontweight='bold')
            ax.set_title('📈 Evolución Mensual de Asistencia', fontsize=16, fontweight='bold', color='#2d5a3d', pad=20)
            ax.grid(alpha=0.3)
            ax.tick_params(axis='x', rotation=45)
            
            for x, y in zip(fechas, valores):
                ax.text(x, y + max(valores) * 0.02, f'{int(y)}',
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
        canvas.drawString(cm, cm, f"Reporte de RR.HH. - Página {doc.page}")
        canvas.restoreState()
