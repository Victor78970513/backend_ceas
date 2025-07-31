from fastapi import APIRouter, Depends, HTTPException, Query
from schemas.reserva import ReservaRequest, ReservaResponse, ReservaUpdateRequest
from use_cases.reserva import ReservaUseCase
from infrastructure.reserva_repository import ReservaRepository
from fastapi.security import OAuth2PasswordBearer
from typing import List, Optional
import jwt
from config import SECRET_KEY, ALGORITHM

router = APIRouter(prefix="/reservas", tags=["reservas"])

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Token inválido o expirado")

@router.get("/", response_model=List[ReservaResponse])
def list_reservas(
    id_evento: Optional[int] = Query(None),
    id_socio: Optional[int] = Query(None),
    current_user=Depends(get_current_user)
):
    use_case = ReservaUseCase(ReservaRepository())
    return use_case.list_reservas(id_evento=id_evento, id_socio=id_socio)

@router.post("/", response_model=ReservaResponse)
def create_reserva(request: ReservaRequest, current_user=Depends(get_current_user)):
    use_case = ReservaUseCase(ReservaRepository())
    return use_case.create_reserva(request)

@router.get("/{reserva_id}", response_model=ReservaResponse)
def get_reserva(reserva_id: int, current_user=Depends(get_current_user)):
    use_case = ReservaUseCase(ReservaRepository())
    return use_case.get_reserva(reserva_id)

@router.put("/{reserva_id}", response_model=ReservaResponse)
def update_reserva(reserva_id: int, request: ReservaUpdateRequest, current_user=Depends(get_current_user)):
    use_case = ReservaUseCase(ReservaRepository())
    return use_case.update_reserva(reserva_id, request)

@router.delete("/{reserva_id}")
def delete_reserva(reserva_id: int, current_user=Depends(get_current_user)):
    use_case = ReservaUseCase(ReservaRepository())
    return use_case.delete_reserva(reserva_id) 