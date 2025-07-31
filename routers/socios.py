from fastapi import APIRouter, Depends, HTTPException
from schemas.socio import SocioRequest, SocioResponse, SocioUpdateRequest
from use_cases.socio import SocioUseCase
from infrastructure.socio_repository import SocioRepository
from fastapi.security import OAuth2PasswordBearer
from typing import List
import jwt
from config import SECRET_KEY, ALGORITHM

router = APIRouter(prefix="/socios", tags=["socios"])

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Token inválido o expirado")

@router.get("/", response_model=List[SocioResponse])
def list_socios(current_user=Depends(get_current_user)):
    use_case = SocioUseCase(SocioRepository())
    return use_case.list_socios()

@router.post("/", response_model=SocioResponse)
def create_socio(request: SocioRequest, current_user=Depends(get_current_user)):
    use_case = SocioUseCase(SocioRepository())
    return use_case.create_socio(request)

@router.get("/{socio_id}", response_model=SocioResponse)
def get_socio(socio_id: int, current_user=Depends(get_current_user)):
    use_case = SocioUseCase(SocioRepository())
    return use_case.get_socio(socio_id)

@router.put("/{socio_id}", response_model=SocioResponse)
def update_socio(socio_id: int, request: SocioUpdateRequest, current_user=Depends(get_current_user)):
    use_case = SocioUseCase(SocioRepository())
    return use_case.update_socio(socio_id, request)

@router.delete("/{socio_id}")
def delete_socio(socio_id: int, current_user=Depends(get_current_user)):
    use_case = SocioUseCase(SocioRepository())
    return use_case.delete_socio(socio_id)

@router.get("/{socio_id}/acciones")
def get_acciones(socio_id: int, current_user=Depends(get_current_user)):
    use_case = SocioUseCase(SocioRepository())
    return use_case.get_acciones(socio_id)

@router.get("/{socio_id}/historial-pagos")
def get_historial_pagos(socio_id: int, current_user=Depends(get_current_user)):
    use_case = SocioUseCase(SocioRepository())
    return use_case.get_historial_pagos(socio_id) 