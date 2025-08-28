from fastapi import APIRouter, Depends, HTTPException, Query
from use_cases.bi_personal import BIPersonalUseCase
from infrastructure.bi_personal_repository import BIPersonalRepository
from schemas.bi_personal import DashboardPersonalResponse
from fastapi.security import OAuth2PasswordBearer
import jwt
from config import SECRET_KEY, ALGORITHM
from typing import Optional

router = APIRouter(prefix="/bi", tags=["bi-personal"])

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")

def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Token inválido o expirado")

@router.get("/personal/dashboard", response_model=DashboardPersonalResponse)
def get_dashboard_personal(
    mes: Optional[int] = Query(None, description="Mes (1-12)", ge=1, le=12),
    anio: Optional[int] = Query(None, description="Año (ej: 2025)", ge=2000, le=2100),
    departamento: Optional[str] = Query(None, description="Filtrar por departamento"),
    cargo: Optional[int] = Query(None, description="Filtrar por cargo"),
    current_user=Depends(get_current_user)
):
    """Obtiene dashboard completo de personal con métricas de asistencia"""
    use_case = BIPersonalUseCase(BIPersonalRepository())
    return use_case.get_dashboard_personal(mes, anio, departamento, cargo)

@router.get("/personal/metricas-generales")
def get_metricas_generales_personal(
    departamento: Optional[str] = Query(None, description="Filtrar por departamento"),
    cargo: Optional[int] = Query(None, description="Filtrar por cargo"),
    current_user=Depends(get_current_user)
):
    """Obtiene métricas generales del personal (total, activos, inactivos, distribución)"""
    use_case = BIPersonalUseCase(BIPersonalRepository())
    return use_case.get_metricas_generales(departamento, cargo)

@router.get("/personal/metricas-asistencia")
def get_metricas_asistencia(
    mes: Optional[int] = Query(None, description="Mes (1-12)", ge=1, le=12),
    anio: Optional[int] = Query(None, description="Año (ej: 2025)", ge=2000, le=2100),
    departamento: Optional[str] = Query(None, description="Filtrar por departamento"),
    cargo: Optional[int] = Query(None, description="Filtrar por cargo"),
    current_user=Depends(get_current_user)
):
    """Obtiene métricas de asistencia (total, presentes, tardanzas, ausencias, porcentaje)"""
    use_case = BIPersonalUseCase(BIPersonalRepository())
    return use_case.get_metricas_asistencia(mes, anio, departamento, cargo)

@router.get("/personal/top-empleados")
def get_top_empleados_asistencia(
    mes: Optional[int] = Query(None, description="Mes (1-12)", ge=1, le=12),
    anio: Optional[int] = Query(None, description="Año (ej: 2025)", ge=2000, le=2100),
    departamento: Optional[str] = Query(None, description="Filtrar por departamento"),
    cargo: Optional[int] = Query(None, description="Filtrar por cargo"),
    current_user=Depends(get_current_user)
):
    """Obtiene top 10 empleados por asistencia y puntualidad"""
    use_case = BIPersonalUseCase(BIPersonalRepository())
    return use_case.get_top_empleados(mes, anio, departamento, cargo)

@router.get("/personal/asistencia-departamento")
def get_asistencia_por_departamento(
    mes: Optional[int] = Query(None, description="Mes (1-12)", ge=1, le=12),
    anio: Optional[int] = Query(None, description="Año (ej: 2025)", ge=2000, le=2100),
    current_user=Depends(get_current_user)
):
    """Obtiene asistencia agrupada por departamento"""
    use_case = BIPersonalUseCase(BIPersonalRepository())
    return use_case.get_asistencia_por_departamento(mes, anio)

@router.get("/personal/tendencias-mensuales")
def get_tendencias_mensuales(
    anio: int = Query(..., description="Año para obtener tendencias", ge=2000, le=2100),
    departamento: Optional[str] = Query(None, description="Filtrar por departamento"),
    cargo: Optional[int] = Query(None, description="Filtrar por cargo"),
    current_user=Depends(get_current_user)
):
    """Obtiene tendencias mensuales de asistencia para un año específico"""
    use_case = BIPersonalUseCase(BIPersonalRepository())
    return use_case.get_tendencias_mensuales(anio, departamento, cargo)


