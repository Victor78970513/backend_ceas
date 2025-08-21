from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import FileResponse, StreamingResponse
from use_cases.bi_administrativo import BIAdministrativoUseCase
from infrastructure.bi_administrativo_repository import BIAdministrativoRepository
from fastapi.security import OAuth2PasswordBearer
import jwt
from config import SECRET_KEY, ALGORITHM
from typing import Optional, List, Dict
import json
import io
import csv
from datetime import datetime, timedelta
import pandas as pd

router = APIRouter(prefix="/bi", tags=["bi-avanzado"])

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")

def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Token inválido o expirado")

# ===== REPORTES INTERACTIVOS =====

@router.get("/reportes/balance-mensual")
def get_balance_mensual_pdf(
    mes: int = Query(..., description="Mes (1-12)", ge=1, le=12),
    anio: int = Query(..., description="Año (ej: 2025)", ge=2000, le=2100),
    current_user=Depends(get_current_user)
):
    """Genera reporte PDF del balance mensual"""
    try:
        use_case = BIAdministrativoUseCase(BIAdministrativoRepository())
        
        # Obtener datos del mes
        dashboard_data = use_case.get_dashboard_completo(mes, anio)
        
        # Generar PDF (placeholder - implementar con librería PDF)
        pdf_content = generate_balance_pdf(dashboard_data, mes, anio)
        
        return StreamingResponse(
            io.BytesIO(pdf_content),
            media_type="application/pdf",
            headers={"Content-Disposition": f"attachment; filename=balance_mensual_{anio}_{mes:02d}.pdf"}
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generando reporte: {str(e)}")

@router.get("/reportes/socios-por-club")
def get_socios_por_club_report(
    club: Optional[int] = Query(None, description="Filtrar por club"),
    formato: str = Query("json", description="Formato: json, csv, excel"),
    current_user=Depends(get_current_user)
):
    """Genera reporte de socios por club en diferentes formatos"""
    try:
        use_case = BIAdministrativoUseCase(BIAdministrativoRepository())
        
        # Obtener datos
        if club:
            top_clubes = [c for c in use_case.get_top_clubes() if c["id_club"] == club]
        else:
            top_clubes = use_case.get_top_clubes()
        
        if formato.lower() == "csv":
            return generate_csv_response(top_clubes, "socios_por_club")
        elif formato.lower() == "excel":
            return generate_excel_response(top_clubes, "socios_por_club")
        else:
            return {"data": top_clubes, "formato": "json"}
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generando reporte: {str(e)}")

@router.get("/reportes/historial-pagos-socio/{id_socio}")
def get_historial_pagos_socio(
    id_socio: int,
    formato: str = Query("json", description="Formato: json, csv"),
    current_user=Depends(get_current_user)
):
    """Genera historial de pagos de un socio específico"""
    try:
        # Aquí implementarías la lógica para obtener historial de pagos
        # Por ahora retornamos datos de ejemplo
        historial = {
            "id_socio": id_socio,
            "nombre": "Socio Ejemplo",
            "pagos": [
                {"fecha": "2025-01-15", "monto": 5000, "estado": "COMPLETADO"},
                {"fecha": "2025-02-15", "monto": 5000, "estado": "PENDIENTE"}
            ]
        }
        
        if formato.lower() == "csv":
            return generate_csv_response([historial], f"historial_pagos_socio_{id_socio}")
        else:
            return historial
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generando historial: {str(e)}")

# ===== PANEL DE DRILL-DOWN =====

@router.get("/drill-down/financiero")
def get_drill_down_financiero(
    nivel: str = Query("categoria", description="Nivel: categoria, club, mes"),
    valor: Optional[str] = Query(None, description="Valor específico para filtrar"),
    current_user=Depends(get_current_user)
):
    """Panel de drill-down financiero con navegación por niveles"""
    try:
        use_case = BIAdministrativoUseCase(BIAdministrativoRepository())
        
        if nivel == "categoria":
            if valor:
                # Drill-down a categoría específica
                return get_drill_down_categoria(valor)
            else:
                # Vista general de categorías
                return get_vista_categorias()
        elif nivel == "club":
            if valor:
                # Drill-down a club específico
                return get_drill_down_club(int(valor))
            else:
                # Vista general de clubes
                return get_vista_clubes()
        elif nivel == "mes":
            if valor:
                # Drill-down a mes específico
                mes, anio = valor.split("-")
                return get_drill_down_mes(int(mes), int(anio))
            else:
                # Vista general de meses
                return get_vista_meses()
        else:
            raise HTTPException(status_code=400, detail="Nivel no válido")
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error en drill-down: {str(e)}")

@router.get("/drill-down/categoria/{categoria}")
def get_drill_down_categoria_detalle(
    categoria: str,
    current_user=Depends(get_current_user)
):
    """Drill-down detallado de una categoría financiera"""
    try:
        use_case = BIAdministrativoUseCase(BIAdministrativoRepository())
        
        # Obtener distribución por categoría
        distribucion = use_case.get_distribucion_financiera(tipo="INGRESO")
        
        # Filtrar por categoría específica
        categoria_data = [d for d in distribucion if d["categoria"].lower() == categoria.lower()]
        
        if not categoria_data:
            raise HTTPException(status_code=404, detail="Categoría no encontrada")
        
        # Obtener datos adicionales para drill-down
        drill_down_data = {
            "categoria": categoria,
            "resumen": categoria_data[0],
            "desglose_mensual": get_desglose_mensual_categoria(categoria),
            "desglose_por_club": get_desglose_club_categoria(categoria),
            "tendencias": get_tendencias_categoria(categoria)
        }
        
        return drill_down_data
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error en drill-down de categoría: {str(e)}")

# ===== DASHBOARDS ESPECIALIZADOS =====

@router.get("/dashboard/ejecutivo")
def get_dashboard_ejecutivo(
    current_user=Depends(get_current_user)
):
    """Dashboard ejecutivo con KPIs estratégicos y resumen financiero"""
    try:
        use_case = BIAdministrativoUseCase(BIAdministrativoRepository())
        
        # Obtener datos del mes actual
        from datetime import datetime
        now = datetime.now()
        
        dashboard_data = use_case.get_dashboard_completo(now.month, now.year)
        
        # Filtrar solo KPIs estratégicos
        kpis_estrategicos = [
            kpi for kpi in dashboard_data.kpis_principales 
            if any(palabra in kpi.nombre.lower() for palabra in 
                   ["crecimiento", "rentabilidad", "eficiencia"])
        ]
        
        return {
            "tipo": "dashboard_ejecutivo",
            "periodo": dashboard_data.periodo,
            "kpis_estrategicos": kpis_estrategicos,
            "resumen_financiero": {
                "balance_neto": dashboard_data.metricas_financieras.balance_neto,
                "margen_rentabilidad": dashboard_data.metricas_financieras.margen_rentabilidad,
                "flujo_caja": dashboard_data.metricas_financieras.flujo_caja
            },
            "tendencias_clave": get_tendencias_clave(),
            "alertas_criticas": dashboard_data.alertas_criticas[:5],  # Top 5 alertas
            "proyecciones": get_proyecciones_ejecutivas()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error obteniendo dashboard ejecutivo: {str(e)}")

@router.get("/dashboard/operativo")
def get_dashboard_operativo(
    current_user=Depends(get_current_user)
):
    """Dashboard operativo con métricas operativas y alertas en tiempo real"""
    try:
        use_case = BIAdministrativoUseCase(BIAdministrativoRepository())
        
        # Obtener datos operativos
        metricas_operativas = use_case.get_metricas_administrativas()
        alertas = use_case.get_alertas_criticas()
        
        return {
            "tipo": "dashboard_operativo",
            "timestamp": datetime.now().isoformat(),
            "metricas_operativas": metricas_operativas,
            "alertas_tiempo_real": alertas,
            "indicadores_proceso": get_indicadores_proceso(),
            "estado_sistema": get_estado_sistema(),
            "tareas_pendientes": get_tareas_pendientes()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error obteniendo dashboard operativo: {str(e)}")

@router.get("/dashboard/financiero")
def get_dashboard_financiero(
    current_user=Depends(get_current_user)
):
    """Dashboard financiero con flujo de caja, presupuestos y análisis de costos"""
    try:
        use_case = BIAdministrativoUseCase(BIAdministrativoRepository())
        
        # Obtener datos financieros
        metricas_financieras = use_case.get_metricas_financieras()
        distribucion_ingresos = use_case.get_distribucion_financiera(tipo="INGRESO")
        distribucion_egresos = use_case.get_distribucion_financiera(tipo="EGRESO")
        
        return {
            "tipo": "dashboard_financiero",
            "timestamp": datetime.now().isoformat(),
            "metricas_financieras": metricas_financieras,
            "distribucion_ingresos": distribucion_ingresos,
            "distribucion_egresos": distribucion_egresos,
            "flujo_caja": get_flujo_caja_detallado(),
            "presupuestos": get_presupuestos_vs_real(),
            "analisis_costos": get_analisis_costos(),
            "proyecciones_financieras": get_proyecciones_financieras()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error obteniendo dashboard financiero: {str(e)}")

@router.get("/dashboard/ventas")
def get_dashboard_ventas(
    current_user=Depends(get_current_user)
):
    """Dashboard de ventas con pipeline, conversiones y metas"""
    try:
        use_case = BIAdministrativoUseCase(BIAdministrativoRepository())
        
        # Obtener datos de ventas
        top_socios = use_case.get_top_socios()
        metricas_administrativas = use_case.get_metricas_administrativas()
        
        return {
            "tipo": "dashboard_ventas",
            "timestamp": datetime.now().isoformat(),
            "pipeline_ventas": get_pipeline_ventas(),
            "conversiones": get_metricas_conversion(),
            "metas": get_metas_ventas(),
            "top_socios": top_socios,
            "metricas_administrativas": metricas_administrativas,
            "analisis_tendencias": get_tendencias_ventas(),
            "oportunidades": get_oportunidades_venta()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error obteniendo dashboard de ventas: {str(e)}")

# ===== FUNCIONES AUXILIARES =====

def generate_balance_pdf(data, mes, anio):
    """Genera PDF del balance mensual (placeholder)"""
    # Aquí implementarías la generación real del PDF
    # Por ahora retornamos contenido de ejemplo
    return b"PDF placeholder content"

def generate_csv_response(data, filename):
    """Genera respuesta CSV"""
    output = io.StringIO()
    if data:
        writer = csv.DictWriter(output, fieldnames=data[0].keys())
        writer.writeheader()
        writer.writerows(data)
    
    output.seek(0)
    return StreamingResponse(
        io.BytesIO(output.getvalue().encode()),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename={filename}.csv"}
    )

def generate_excel_response(data, filename):
    """Genera respuesta Excel"""
    # Aquí implementarías la generación de Excel
    # Por ahora retornamos CSV
    return generate_csv_response(data, filename)

def get_drill_down_categoria(categoria):
    """Obtiene drill-down de categoría"""
    return {"categoria": categoria, "nivel": "detalle", "datos": []}

def get_vista_categorias():
    """Obtiene vista general de categorías"""
    return {"nivel": "categorias", "datos": []}

def get_drill_down_club(id_club):
    """Obtiene drill-down de club"""
    return {"club": id_club, "nivel": "detalle", "datos": []}

def get_vista_clubes():
    """Obtiene vista general de clubes"""
    return {"nivel": "clubes", "datos": []}

def get_drill_down_mes(mes, anio):
    """Obtiene drill-down de mes"""
    return {"mes": mes, "anio": anio, "nivel": "detalle", "datos": []}

def get_vista_meses():
    """Obtiene vista general de meses"""
    return {"nivel": "meses", "datos": []}

def get_desglose_mensual_categoria(categoria):
    """Obtiene desglose mensual de categoría"""
    return {"categoria": categoria, "desglose_mensual": []}

def get_desglose_club_categoria(categoria):
    """Obtiene desglose por club de categoría"""
    return {"categoria": categoria, "desglose_club": []}

def get_tendencias_categoria(categoria):
    """Obtiene tendencias de categoría"""
    return {"categoria": categoria, "tendencias": []}

def get_tendencias_clave():
    """Obtiene tendencias clave para ejecutivos"""
    return {"tendencias": []}

def get_proyecciones_ejecutivas():
    """Obtiene proyecciones ejecutivas"""
    return {"proyecciones": []}

def get_indicadores_proceso():
    """Obtiene indicadores de proceso"""
    return {"indicadores": []}

def get_estado_sistema():
    """Obtiene estado del sistema"""
    return {"estado": "operativo"}

def get_tareas_pendientes():
    """Obtiene tareas pendientes"""
    return {"tareas": []}

def get_flujo_caja_detallado():
    """Obtiene flujo de caja detallado"""
    return {"flujo_caja": []}

def get_presupuestos_vs_real():
    """Obtiene presupuestos vs real"""
    return {"presupuestos": []}

def get_analisis_costos():
    """Obtiene análisis de costos"""
    return {"costos": []}

def get_proyecciones_financieras():
    """Obtiene proyecciones financieras"""
    return {"proyecciones": []}

def get_pipeline_ventas():
    """Obtiene pipeline de ventas"""
    return {"pipeline": []}

def get_metricas_conversion():
    """Obtiene métricas de conversión"""
    return {"conversiones": []}

def get_metas_ventas():
    """Obtiene metas de ventas"""
    return {"metas": []}

def get_tendencias_ventas():
    """Obtiene tendencias de ventas"""
    return {"tendencias": []}

def get_oportunidades_venta():
    """Obtiene oportunidades de venta"""
    return {"oportunidades": []}

