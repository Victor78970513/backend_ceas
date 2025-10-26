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

class ReporteContableService:
    """
    Servicio para generar reportes contables híbridos
    Utiliza datos operativos para simular estados financieros formales
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

    def generar_pdf_contable(self, fecha_inicio=None, fecha_fin=None):
        """
        Genera un reporte contable híbrido completo
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
        titulo = Paragraph("📊 REPORTE CONTABLE", self.styles['Titulo'])
        story.append(titulo)
        
        subtitulo = Paragraph(
            f"Club de Emprendedores y Accionistas<br/>"
            f"Del {fecha_inicio or 'Inicio'} al {fecha_fin or datetime.now().strftime('%Y-%m-%d')}",
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
        
        # Obtener datos contables
        datos = self._obtener_datos_contables(fecha_inicio, fecha_fin)
        
        # 1. ESTADO DE RESULTADOS
        story.append(Paragraph("ESTADO DE RESULTADOS", self.styles['Subtitulo']))
        story.append(Spacer(1, 0.2*cm))
        
        estado_resultados = self._generar_estado_resultados(datos)
        if estado_resultados:
            story.append(estado_resultados)
        
        story.append(PageBreak())
        
        # 2. BALANCE GENERAL
        story.append(Paragraph("BALANCE GENERAL", self.styles['Subtitulo']))
        
        # Nota importante sobre limitaciones
        nota_balance = Paragraph(
            "<b>NOTA IMPORTANTE:</b> Este Balance General es estimado y utiliza los datos operativos "
            "disponibles. No refleja saldos reales de cuentas bancarias ni incluye registros contables formales. "
            "El Patrimonio se calcula como residual (Activos - Pasivos).",
            self.styles['TextoNormal']
        )
        story.append(nota_balance)
        story.append(Spacer(1, 0.2*cm))
        
        balance_general = self._generar_balance_general(datos)
        if balance_general:
            story.append(balance_general)
        
        story.append(PageBreak())
        
        # 3. FLUJO DE EFECTIVO
        story.append(Paragraph("FLUJO DE EFECTIVO", self.styles['Subtitulo']))
        story.append(Spacer(1, 0.2*cm))
        
        flujo_efectivo = self._generar_flujo_efectivo(datos)
        if flujo_efectivo:
            story.append(flujo_efectivo)
        
        story.append(PageBreak())
        
        # 4. ANÁLISIS FINANCIERO
        story.append(Paragraph("ANÁLISIS FINANCIERO", self.styles['Subtitulo']))
        story.append(Spacer(1, 0.2*cm))
        
        # Gráficas de análisis
        grafica_margen = self._generar_grafica_margen(datos)
        if grafica_margen:
            img = Image(grafica_margen, width=16*cm, height=10*cm)
            story.append(img)
            story.append(Spacer(1, 0.3*cm))
        
        grafica_tendencia = self._generar_grafica_tendencia_financiera(datos)
        if grafica_tendencia:
            img = Image(grafica_tendencia, width=16*cm, height=10*cm)
            story.append(img)
        
        # Generar PDF
        doc.build(story, onFirstPage=self._agregar_header_footer, onLaterPages=self._agregar_header_footer)
        
        buffer.seek(0)
        return buffer.getvalue()
    
    def _obtener_datos_contables(self, fecha_inicio, fecha_fin):
        """Obtiene todos los datos contables de la BD"""
        try:
            conn = psycopg2.connect(DATABASE_URL)
            cursor = conn.cursor()
            
            datos = {}
            
            # Ingresos (de movimientos financieros)
            cursor.execute("""
                SELECT 
                    COALESCE(SUM(monto), 0) as total_ingresos,
                    COUNT(*) as cantidad_ingresos
                FROM movimiento_financiero
                WHERE tipo_movimiento = 'INGRESO'
                AND estado = 'confirmado'
            """)
            datos['ingresos'] = cursor.fetchone()
            
            # Egresos (de movimientos financieros)
            cursor.execute("""
                SELECT 
                    COALESCE(SUM(monto), 0) as total_egresos,
                    COUNT(*) as cantidad_egresos
                FROM movimiento_financiero
                WHERE tipo_movimiento = 'EGRESO'
                AND estado = 'confirmado'
            """)
            datos['egresos'] = cursor.fetchone()
            
            # Pagos de acciones (ingresos)
            cursor.execute("""
                SELECT 
                    COALESCE(SUM(monto), 0) as total_pagos_acciones,
                    COUNT(*) as cantidad_pagos
                FROM pago_accion
                WHERE estado_pago = 2
            """)
            datos['pagos_acciones'] = cursor.fetchone()
            
            # Compras (egresos)
            cursor.execute("""
                SELECT 
                    COALESCE(SUM(monto_total), 0) as total_compras,
                    COUNT(*) as cantidad_compras
                FROM compras
                WHERE estado IN ('completado', 'pagado')
            """)
            datos['compras'] = cursor.fetchone()
            
            # Salarios (egresos)
            cursor.execute("""
                SELECT 
                    COALESCE(SUM(salario), 0) as total_salarios,
                    COUNT(*) as cantidad_empleados
                FROM personal
                WHERE estado = TRUE
            """)
            datos['salarios'] = cursor.fetchone()
            
            # Inventario (valor)
            cursor.execute("""
                SELECT 
                    COALESCE(SUM(cantidad_en_stock * precio_unitario), 0) as valor_inventario,
                    COUNT(*) as cantidad_productos
                FROM inventario
                WHERE cantidad_en_stock > 0
            """)
            datos['inventario'] = cursor.fetchone()
            
            # Cuotas pendientes (pasivos)
            cursor.execute("""
                SELECT 
                    COALESCE(SUM(saldo_pendiente), 0) as total_cuotas_pendientes,
                    COUNT(*) as cantidad_cuotas
                FROM accion
                WHERE saldo_pendiente > 0
            """)
            datos['cuotas_pendientes'] = cursor.fetchone()
            
            # Movimientos mensuales
            cursor.execute("""
                SELECT 
                    TO_CHAR(fecha, 'YYYY-MM') as mes,
                    SUM(CASE WHEN tipo_movimiento = 'INGRESO' THEN monto ELSE 0 END) as ingresos,
                    SUM(CASE WHEN tipo_movimiento = 'EGRESO' THEN monto ELSE 0 END) as egresos
                FROM movimiento_financiero
                WHERE estado = 'confirmado'
                GROUP BY TO_CHAR(fecha, 'YYYY-MM')
                ORDER BY mes DESC
                LIMIT 12
            """)
            datos['tendencia_mensual'] = cursor.fetchall()
            
            cursor.close()
            conn.close()
            
            return datos
            
        except Exception as e:
            print(f"Error obteniendo datos contables: {e}")
            return {}
    
    def _generar_estado_resultados(self, datos):
        """Genera el Estado de Resultados"""
        try:
            total_ingresos = float(datos.get('ingresos', [0])[0]) + float(datos.get('pagos_acciones', [0])[0])
            total_egresos = float(datos.get('egresos', [0])[0]) + float(datos.get('compras', [0])[0]) + float(datos.get('salarios', [0])[0])
            utilidad_neta = total_ingresos - total_egresos
            margen_utilidad = (utilidad_neta / total_ingresos * 100) if total_ingresos > 0 else 0
            
            # Datos de la tabla
            data = [
                ['CONCEPTO', 'MONTO (Bs.)'],
                ['', ''],
                ['<b>INGRESOS:</b>', ''],
                ['Movimientos financieros', f"Bs. {datos.get('ingresos', [0])[0]:,.2f}"],
                ['Pagos de acciones', f"Bs. {datos.get('pagos_acciones', [0])[0]:,.2f}"],
                ['<b>TOTAL INGRESOS</b>', f"<b>Bs. {total_ingresos:,.2f}</b>"],
                ['', ''],
                ['<b>EGRESOS:</b>', ''],
                ['Movimientos financieros', f"Bs. {datos.get('egresos', [0])[0]:,.2f}"],
                ['Compras a proveedores', f"Bs. {datos.get('compras', [0])[0]:,.2f}"],
                ['Salarios de personal', f"Bs. {datos.get('salarios', [0])[0]:,.2f}"],
                ['<b>TOTAL EGRESOS</b>', f"<b>Bs. {total_egresos:,.2f}</b>"],
                ['', ''],
                ['<b>UTILIDAD NETA</b>', f"<b>Bs. {utilidad_neta:,.2f}</b>"],
                ['', ''],
                ['Margen de Utilidad', f"{margen_utilidad:.2f}%"],
            ]
            
            tabla = Table(data, colWidths=[12*cm, 4*cm])
            tabla.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2d5a3d')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('ALIGN', (1, 0), (-1, -1), 'RIGHT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 11),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('TOPPADDING', (0, 0), (-1, 0), 12),
                ('FONTSIZE', (0, 1), (-1, -1), 10),
                ('GRID', (0, 0), (-1, -1), 1, colors.grey),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f0f0f0')]),
            ]))
            
            return tabla
            
        except Exception as e:
            print(f"Error generando estado de resultados: {e}")
            return None
    
    def _generar_balance_general(self, datos):
        """Genera el Balance General con los datos disponibles"""
        try:
            # ============================================================
            # ACTIVOS
            # ============================================================
            
            # 1. Inventario (valor real del stock)
            valor_inventario = float(datos.get('inventario', [0])[0])
            
            # 2. Flujo de efectivo neto (diferencia entre ingresos y egresos)
            total_ingresos = float(datos.get('ingresos', [0])[0]) + float(datos.get('pagos_acciones', [0])[0])
            total_egresos = float(datos.get('egresos', [0])[0]) + float(datos.get('compras', [0])[0]) + float(datos.get('salarios', [0])[0])
            flujo_efectivo_neto = total_ingresos - total_egresos
            
            # NOTA: Este es el flujo neto, NO el saldo real de caja
            # Para un balance real necesitaríamos registros de cuentas bancarias
            
            # Total de Activos
            total_activos = valor_inventario + max(0, flujo_efectivo_neto)
            
            # ============================================================
            # PASIVOS
            # ============================================================
            
            # 1. Cuotas pendientes de socios
            cuotas_pendientes = float(datos.get('cuotas_pendientes', [0])[0])
            
            # 2. Compras pendientes de pago (estimado: compras no pagadas)
            # En una implementación real, necesitaríamos un campo "estado_pago" en compras
            total_pasivos = cuotas_pendientes
            
            # ============================================================
            # PATRIMONIO (Calculado como residual)
            # ============================================================
            # IMPORTANTE: El Patrimonio se calcula como la diferencia entre
            # Activos y Pasivos. En contabilidad real, el Patrimonio debería
            # incluir: Capital Social + Utilidades Acumuladas - Dividendos
            patrimonio = total_activos - total_pasivos
            
            # Datos de la tabla
            data = [
                ['CONCEPTO', 'MONTO (Bs.)'],
                ['', ''],
                ['<b>ACTIVOS:</b>', ''],
                ['Inventario (valor del stock)', f"Bs. {valor_inventario:,.2f}"],
                ['Flujo de Efectivo Neto (*)', f"Bs. {max(0, flujo_efectivo_neto):,.2f}"],
                ['<b>TOTAL ACTIVOS</b>', f"<b>Bs. {total_activos:,.2f}</b>"],
                ['', ''],
                ['<b>PASIVOS:</b>', ''],
                ['Cuotas pendientes de socios', f"Bs. {cuotas_pendientes:,.2f}"],
                ['<b>TOTAL PASIVOS</b>', f"<b>Bs. {total_pasivos:,.2f}</b>"],
                ['', ''],
                ['<b>PATRIMONIO (Calculado como residual)</b>', f"<b>Bs. {patrimonio:,.2f}</b>"],
                ['', ''],
                ['<i>(*) Flujo neto de efectivo. No refleja el saldo real</i>', ''],
                ['<i>   de cuentas bancarias.</i>', ''],
            ]
            
            tabla = Table(data, colWidths=[12*cm, 4*cm])
            tabla.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2d5a3d')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('ALIGN', (1, 0), (-1, -1), 'RIGHT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 11),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('TOPPADDING', (0, 0), (-1, 0), 12),
                ('FONTSIZE', (0, 1), (-1, -1), 10),
                ('GRID', (0, 0), (-1, -1), 1, colors.grey),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f0f0f0')]),
            ]))
            
            return tabla
            
        except Exception as e:
            print(f"Error generando balance general: {e}")
            return None
    
    def _generar_flujo_efectivo(self, datos):
        """Genera el Flujo de Efectivo"""
        try:
            total_ingresos = float(datos.get('ingresos', [0])[0]) + float(datos.get('pagos_acciones', [0])[0])
            total_egresos = float(datos.get('egresos', [0])[0]) + float(datos.get('compras', [0])[0]) + float(datos.get('salarios', [0])[0])
            saldo_neto = total_ingresos - total_egresos
            
            # Datos de la tabla
            data = [
                ['CONCEPTO', 'MONTO (Bs.)'],
                ['', ''],
                ['<b>ENTRADAS DE EFECTIVO:</b>', ''],
                ['Movimientos financieros', f"Bs. {datos.get('ingresos', [0])[0]:,.2f}"],
                ['Pagos de acciones', f"Bs. {datos.get('pagos_acciones', [0])[0]:,.2f}"],
                ['<b>TOTAL ENTRADAS</b>', f"<b>Bs. {total_ingresos:,.2f}</b>"],
                ['', ''],
                ['<b>SALIDAS DE EFECTIVO:</b>', ''],
                ['Movimientos financieros', f"Bs. {datos.get('egresos', [0])[0]:,.2f}"],
                ['Compras a proveedores', f"Bs. {datos.get('compras', [0])[0]:,.2f}"],
                ['Salarios de personal', f"Bs. {datos.get('salarios', [0])[0]:,.2f}"],
                ['<b>TOTAL SALIDAS</b>', f"<b>Bs. {total_egresos:,.2f}</b>"],
                ['', ''],
                ['<b>SALDO NETO DE EFECTIVO</b>', f"<b>Bs. {saldo_neto:,.2f}</b>"],
            ]
            
            tabla = Table(data, colWidths=[12*cm, 4*cm])
            tabla.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2d5a3d')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('ALIGN', (1, 0), (-1, -1), 'RIGHT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 11),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('TOPPADDING', (0, 0), (-1, 0), 12),
                ('FONTSIZE', (0, 1), (-1, -1), 10),
                ('GRID', (0, 0), (-1, -1), 1, colors.grey),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f0f0f0')]),
            ]))
            
            return tabla
            
        except Exception as e:
            print(f"Error generando flujo de efectivo: {e}")
            return None
    
    def _generar_grafica_margen(self, datos):
        """Genera gráfica de margen de utilidad"""
        try:
            total_ingresos = float(datos.get('ingresos', [0])[0]) + float(datos.get('pagos_acciones', [0])[0])
            total_egresos = float(datos.get('egresos', [0])[0]) + float(datos.get('compras', [0])[0]) + float(datos.get('salarios', [0])[0])
            utilidad_neta = total_ingresos - total_egresos
            
            fig, ax = plt.subplots(figsize=(8, 6))
            fig.patch.set_facecolor('#f8f9fa')
            
            categorias = ['Ingresos', 'Egresos', 'Utilidad Neta']
            valores = [total_ingresos, total_egresos, max(0, utilidad_neta)]
            colores = ['#2d5a3d', '#d32f2f', '#1e88e5']
            
            bars = ax.bar(categorias, valores, color=colores, edgecolor='white', linewidth=2)
            
            ax.set_title('💰 Análisis de Resultados', fontsize=16, fontweight='bold', color='#2d5a3d', pad=20)
            ax.set_ylabel('Monto (Bs)', fontsize=12, fontweight='bold')
            ax.grid(axis='y', alpha=0.3)
            
            for i, (bar, valor) in enumerate(zip(bars, valores)):
                height = bar.get_height()
                ax.text(bar.get_x() + bar.get_width()/2., height,
                       f'Bs. {valor:,.0f}',
                       ha='center', va='bottom', fontsize=11, fontweight='bold')
            
            plt.tight_layout()
            
            buffer = BytesIO()
            plt.savefig(buffer, format='png', dpi=150, bbox_inches='tight')
            buffer.seek(0)
            plt.close()
            
            return buffer
            
        except Exception as e:
            print(f"Error generando gráfica de margen: {e}")
            return None
    
    def _generar_grafica_tendencia_financiera(self, datos):
        """Genera gráfica de tendencia financiera mensual"""
        try:
            tendencia = datos.get('tendencia_mensual', [])
            
            if not tendencia:
                return None
            
            meses = [row[0] for row in reversed(tendencia)]
            ingresos = [float(row[1]) for row in reversed(tendencia)]
            egresos = [float(row[2]) for row in reversed(tendencia)]
            
            fig, ax = plt.subplots(figsize=(10, 6))
            fig.patch.set_facecolor('#f8f9fa')
            
            x = np.arange(len(meses))
            width = 0.35
            
            bars1 = ax.bar(x - width/2, ingresos, width, label='Ingresos', color='#2d5a3d', alpha=0.8)
            bars2 = ax.bar(x + width/2, egresos, width, label='Egresos', color='#d32f2f', alpha=0.8)
            
            ax.set_xlabel('Mes', fontsize=12, fontweight='bold')
            ax.set_ylabel('Monto (Bs)', fontsize=12, fontweight='bold')
            ax.set_title('📈 Tendencia Financiera Mensual', fontsize=16, fontweight='bold', color='#2d5a3d', pad=20)
            ax.set_xticks(x)
            ax.set_xticklabels(meses, rotation=45, ha='right')
            ax.legend()
            ax.grid(axis='y', alpha=0.3)
            
            plt.tight_layout()
            
            buffer = BytesIO()
            plt.savefig(buffer, format='png', dpi=150, bbox_inches='tight')
            buffer.seek(0)
            plt.close()
            
            return buffer
            
        except Exception as e:
            print(f"Error generando gráfica de tendencia: {e}")
            return None
    
    def _agregar_header_footer(self, canvas, doc):
        """Agrega encabezado y pie de página"""
        canvas.saveState()
        canvas.setFont('Helvetica', 9)
        canvas.drawString(cm, cm, f"Reporte Contable - Página {doc.page}")
        canvas.restoreState()
