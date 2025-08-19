from fastapi import APIRouter, Depends, HTTPException, Query
from use_cases.bi import BIUseCase
from infrastructure.bi_repository import BIRepository
from schemas.bi import DashboardFinancieroResponse
from fastapi.security import OAuth2PasswordBearer
import jwt
from config import SECRET_KEY, ALGORITHM
from typing import Optional

router = APIRouter(prefix="/bi", tags=["bi"])

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")

def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Token inválido o expirado")

@router.get("/finanzas-resumen", response_model=DashboardFinancieroResponse)
def get_finanzas_resumen(
    mes: Optional[int] = Query(None, description="Mes (1-12)", ge=1, le=12),
    anio: Optional[int] = Query(None, description="Año (ej: 2025)", ge=2000, le=2100),
    current_user=Depends(get_current_user)
):
    """Obtiene resumen financiero con métricas agregadas para cards de información rápida"""
    use_case = BIUseCase(BIRepository())
    return use_case.get_dashboard_financiero(mes, anio)

@router.get("/reportes")
def get_reportes(current_user=Depends(get_current_user)):
    use_case = BIUseCase(BIRepository())
    return use_case.get_reportes()

@router.get("/metricas")
def get_metricas(current_user=Depends(get_current_user)):
    use_case = BIUseCase(BIRepository())
    return use_case.get_metricas()

@router.get("/descargas")
def get_descargas(current_user=Depends(get_current_user)):
    use_case = BIUseCase(BIRepository())
    return use_case.get_descargas() 