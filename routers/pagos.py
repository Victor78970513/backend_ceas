from fastapi import APIRouter, Depends, HTTPException
from schemas.pago import PagoRequest, PagoResponse, PagoUpdateRequest, PagoEstadoRequest
from use_cases.pago import PagoUseCase
from infrastructure.pago_repository import PagoRepository
from fastapi.security import OAuth2PasswordBearer
from typing import List
import jwt
from config import SECRET_KEY, ALGORITHM

router = APIRouter(prefix="/pagos", tags=["pagos"])

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Token inválido o expirado")

@router.get("/", response_model=List[PagoResponse])
def list_pagos(current_user=Depends(get_current_user)):
    use_case = PagoUseCase(PagoRepository())
    return use_case.list_pagos()

@router.post("/", response_model=PagoResponse)
def create_pago(request: PagoRequest, current_user=Depends(get_current_user)):
    use_case = PagoUseCase(PagoRepository())
    return use_case.create_pago(request)

@router.get("/{pago_id}", response_model=PagoResponse)
def get_pago(pago_id: int, current_user=Depends(get_current_user)):
    use_case = PagoUseCase(PagoRepository())
    return use_case.get_pago(pago_id)

@router.put("/{pago_id}", response_model=PagoResponse)
def update_pago(pago_id: int, request: PagoUpdateRequest, current_user=Depends(get_current_user)):
    use_case = PagoUseCase(PagoRepository())
    return use_case.update_pago(pago_id, request)

@router.patch("/{pago_id}/cambiar-estado", response_model=PagoResponse)
def cambiar_estado(pago_id: int, request: PagoEstadoRequest, current_user=Depends(get_current_user)):
    use_case = PagoUseCase(PagoRepository())
    return use_case.cambiar_estado(pago_id, request)

@router.delete("/{pago_id}")
def delete_pago(pago_id: int, current_user=Depends(get_current_user)):
    use_case = PagoUseCase(PagoRepository())
    return use_case.delete_pago(pago_id) 