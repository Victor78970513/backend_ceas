from fastapi import APIRouter, Depends, HTTPException
from schemas.evento import EventoRequest, EventoResponse, EventoUpdateRequest
from use_cases.evento import EventoUseCase
from infrastructure.evento_repository import EventoRepository
from fastapi.security import OAuth2PasswordBearer
from typing import List
import jwt
from config import SECRET_KEY, ALGORITHM

router = APIRouter(prefix="/eventos", tags=["eventos"])

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Token inválido o expirado")

@router.get("/", response_model=List[EventoResponse])
def list_eventos(current_user=Depends(get_current_user)):
    use_case = EventoUseCase(EventoRepository())
    return use_case.list_eventos()

@router.post("/", response_model=EventoResponse)
def create_evento(request: EventoRequest, current_user=Depends(get_current_user)):
    use_case = EventoUseCase(EventoRepository())
    return use_case.create_evento(request)

@router.get("/{evento_id}", response_model=EventoResponse)
def get_evento(evento_id: int, current_user=Depends(get_current_user)):
    use_case = EventoUseCase(EventoRepository())
    return use_case.get_evento(evento_id)

@router.put("/{evento_id}", response_model=EventoResponse)
def update_evento(evento_id: int, request: EventoUpdateRequest, current_user=Depends(get_current_user)):
    use_case = EventoUseCase(EventoRepository())
    return use_case.update_evento(evento_id, request)

@router.delete("/{evento_id}")
def delete_evento(evento_id: int, current_user=Depends(get_current_user)):
    use_case = EventoUseCase(EventoRepository())
    return use_case.delete_evento(evento_id) 