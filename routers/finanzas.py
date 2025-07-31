from fastapi import APIRouter, Depends, HTTPException
from schemas.finanza import MovimientoFinancieroRequest, MovimientoFinancieroResponse, MovimientoFinancieroUpdateRequest
from use_cases.finanza import FinanzaUseCase
from infrastructure.finanza_repository import FinanzaRepository
from fastapi.security import OAuth2PasswordBearer
from typing import List
import jwt
from config import SECRET_KEY, ALGORITHM

router = APIRouter(prefix="/finanzas", tags=["finanzas"])

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Token inválido o expirado")

@router.get("/movimientos", response_model=List[MovimientoFinancieroResponse])
def list_movimientos(current_user=Depends(get_current_user)):
    use_case = FinanzaUseCase(FinanzaRepository())
    return use_case.list_movimientos()

@router.post("/movimientos", response_model=MovimientoFinancieroResponse)
def create_movimiento(request: MovimientoFinancieroRequest, current_user=Depends(get_current_user)):
    use_case = FinanzaUseCase(FinanzaRepository())
    return use_case.create_movimiento(request)

@router.get("/movimientos/{movimiento_id}", response_model=MovimientoFinancieroResponse)
def get_movimiento(movimiento_id: int, current_user=Depends(get_current_user)):
    use_case = FinanzaUseCase(FinanzaRepository())
    return use_case.get_movimiento(movimiento_id)

@router.put("/movimientos/{movimiento_id}", response_model=MovimientoFinancieroResponse)
def update_movimiento(movimiento_id: int, request: MovimientoFinancieroUpdateRequest, current_user=Depends(get_current_user)):
    use_case = FinanzaUseCase(FinanzaRepository())
    return use_case.update_movimiento(movimiento_id, request)

@router.delete("/movimientos/{movimiento_id}")
def delete_movimiento(movimiento_id: int, current_user=Depends(get_current_user)):
    use_case = FinanzaUseCase(FinanzaRepository())
    return use_case.delete_movimiento(movimiento_id)

@router.get("/reportes")
def get_reportes(current_user=Depends(get_current_user)):
    use_case = FinanzaUseCase(FinanzaRepository())
    return use_case.get_reportes() 