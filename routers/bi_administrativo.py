from fastapi import APIRouter, Depends, HTTPException, Query
from use_cases.bi_administrativo import BIAdministrativoUseCase
from infrastructure.bi_administrativo_repository import BIAdministrativoRepository
from schemas.bi_administrativo import DashboardAdministrativoFinanciero
from fastapi.security import OAuth2PasswordBearer
import jwt
from config import SECRET_KEY, ALGORITHM
from typing import Optional, List, Dict

router = APIRouter(prefix="/bi", tags=["bi-administrativo"])

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")

def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Token inválido o expirado")

@router.get("/administrativo/dashboard", response_model=DashboardAdministrativoFinanciero)
def get_dashboard_administrativo(
    mes: Optional[int] = Query(None, description="Mes (1-12)", ge=1, le=12),
    anio: Optional[int] = Query(None, description="Año (ej: 2025)", ge=2000, le=2100),
    club: Optional[int] = Query(None, description="Filtrar por club"),
    current_user=Depends(get_current_user)
):
    """Obtiene dashboard completo administrativo y financiero con métricas agregadas"""
    use_case = BIAdministrativoUseCase(BIAdministrativoRepository())
    return use_case.get_dashboard_completo(mes, anio, club)

@router.get("/administrativo/metricas-financieras")
def get_metricas_financieras(
    mes: Optional[int] = Query(None, description="Mes (1-12)", ge=1, le=12),
    anio: Optional[int] = Query(None, description="Año (ej: 2025)", ge=2000, le=2100),
    club: Optional[int] = Query(None, description="Filtrar por club"),
    current_user=Depends(get_current_user)
):
    """Obtiene métricas financieras principales (ingresos, egresos, balance, rentabilidad)"""
    use_case = BIAdministrativoUseCase(BIAdministrativoRepository())
    return use_case.get_metricas_financieras(mes, anio, club)

@router.get("/administrativo/metricas-administrativas")
def get_metricas_administrativas(
    mes: Optional[int] = Query(None, description="Mes (1-12)", ge=1, le=12),
    anio: Optional[int] = Query(None, description="Año (ej: 2025)", ge=2000, le=2100),
    club: Optional[int] = Query(None, description="Filtrar por club"),
    current_user=Depends(get_current_user)
):
    """Obtiene métricas administrativas (socios, retención, eficiencia operativa)"""
    use_case = BIAdministrativoUseCase(BIAdministrativoRepository())
    return use_case.get_metricas_administrativas(mes, anio, club)

@router.get("/administrativo/top-clubes")
def get_top_clubes(
    mes: Optional[int] = Query(None, description="Mes (1-12)", ge=1, le=12),
    anio: Optional[int] = Query(None, description="Año (ej: 2025)", ge=2000, le=2100),
    current_user=Depends(get_current_user)
):
    """Obtiene top 10 clubes por rendimiento financiero y operativo"""
    use_case = BIAdministrativoUseCase(BIAdministrativoRepository())
    return use_case.get_top_clubes(mes, anio)

@router.get("/administrativo/top-socios")
def get_top_socios(
    mes: Optional[int] = Query(None, description="Mes (1-12)", ge=1, le=12),
    anio: Optional[int] = Query(None, description="Año (ej: 2025)", ge=2000, le=2100),
    club: Optional[int] = Query(None, description="Filtrar por club"),
    current_user=Depends(get_current_user)
):
    """Obtiene top 10 socios por inversión total y antigüedad"""
    use_case = BIAdministrativoUseCase(BIAdministrativoRepository())
    return use_case.get_top_socios(mes, anio, club)

@router.get("/administrativo/distribucion-financiera")
def get_distribucion_financiera(
    mes: Optional[int] = Query(None, description="Mes (1-12)", ge=1, le=12),
    anio: Optional[int] = Query(None, description="Año (ej: 2025)", ge=2000, le=2100),
    club: Optional[int] = Query(None, description="Filtrar por club"),
    current_user=Depends(get_current_user)
):
    """Obtiene distribución financiera completa por categorías (Ingresos y Egresos)"""
    use_case = BIAdministrativoUseCase(BIAdministrativoRepository())
    
    # Obtener ambas distribuciones
    distribucion_ingresos = use_case.get_distribucion_financiera(mes, anio, club, "INGRESO")
    distribucion_egresos = use_case.get_distribucion_financiera(mes, anio, club, "EGRESO")
    
    return {
        "ingresos": distribucion_ingresos,
        "egresos": distribucion_egresos,
        "resumen": {
            "total_ingresos": sum(item["monto"] for item in distribucion_ingresos),
            "total_egresos": sum(item["monto"] for item in distribucion_egresos),
            "balance": sum(item["monto"] for item in distribucion_ingresos) - sum(item["monto"] for item in distribucion_egresos)
        }
    }

@router.get("/administrativo/kpis")
def get_kpis_principales(
    mes: Optional[int] = Query(None, description="Mes (1-12)", ge=1, le=12),
    anio: Optional[int] = Query(None, description="Año (ej: 2025)", ge=2000, le=2100),
    club: Optional[int] = Query(None, description="Filtrar por club"),
    current_user=Depends(get_current_user)
):
    """Obtiene KPIs principales del negocio (conversión, rentabilidad, eficiencia)"""
    use_case = BIAdministrativoUseCase(BIAdministrativoRepository())
    return use_case.get_kpis_principales(mes, anio, club)

@router.get("/administrativo/tendencias")
def get_tendencias_mensuales(
    anio: Optional[int] = Query(None, description="Año (ej: 2025)", ge=2000, le=2100),
    club: Optional[int] = Query(None, description="Filtrar por club"),
    current_user=Depends(get_current_user)
):
    """Obtiene tendencias mensuales del año para análisis temporal"""
    use_case = BIAdministrativoUseCase(BIAdministrativoRepository())
    return use_case.get_tendencias_mensuales(anio, club)

@router.get("/administrativo/movimientos-financieros-detallados")
def get_movimientos_financieros_detallados(
    dias: Optional[int] = Query(90, description="Días hacia atrás (default: 90)", ge=7, le=365),
    club: Optional[int] = Query(None, description="Filtrar por club"),
    current_user=Depends(get_current_user)
):
    """Obtiene movimientos financieros detallados día a día para gráficas de alta resolución"""
    use_case = BIAdministrativoUseCase(BIAdministrativoRepository())
    return use_case.get_movimientos_financieros_detallados(dias, club)

@router.get("/administrativo/alertas")
def get_alertas_criticas(
    mes: Optional[int] = Query(None, description="Mes (1-12)", ge=1, le=12),
    anio: Optional[int] = Query(None, description="Año (ej: 2025)", ge=2000, le=2100),
    club: Optional[int] = Query(None, description="Filtrar por club"),
    current_user=Depends(get_current_user)
):
    """Obtiene alertas críticas del sistema (balance negativo, socios inactivos, pagos pendientes)"""
    use_case = BIAdministrativoUseCase(BIAdministrativoRepository())
    return use_case.get_alertas_criticas(mes, anio, club)

@router.get("/administrativo/resumen-rapido")
def get_resumen_rapido(
    current_user=Depends(get_current_user)
):
    """Obtiene resumen rápido de métricas clave para dashboard principal"""
    use_case = BIAdministrativoUseCase(BIAdministrativoRepository())
    
    # Obtener datos del mes actual
    from datetime import datetime
    now = datetime.now()
    
    metricas_financieras = use_case.get_metricas_financieras(now.month, now.year)
    metricas_administrativas = use_case.get_metricas_administrativas(now.month, now.year)
    alertas = use_case.get_alertas_criticas(now.month, now.year)
    
    return {
        "periodo_actual": f"{now.year:04d}-{now.month:02d}",
        "balance_neto": metricas_financieras["balance_neto"],
        "margen_rentabilidad": metricas_financieras["margen_rentabilidad"],
        "total_socios": metricas_administrativas["total_socios"],
        "tasa_retencion": metricas_administrativas["tasa_retencion"],
        "alertas_activas": len(alertas),
        "estado_general": "excelente" if metricas_financieras["balance_neto"] > 0 and metricas_administrativas["tasa_retencion"] > 80 else "bueno" if metricas_financieras["balance_neto"] > 0 else "requiere_atencion"
    }
