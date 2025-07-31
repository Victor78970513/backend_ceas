from fastapi import APIRouter, Depends, HTTPException
from schemas.asistencia import AsistenciaRequest, AsistenciaResponse, AsistenciaUpdateRequest
from use_cases.asistencia import AsistenciaUseCase
from infrastructure.asistencia_repository import AsistenciaRepository
from fastapi.security import OAuth2PasswordBearer
from typing import List
import jwt
from config import SECRET_KEY, ALGORITHM

router = APIRouter(prefix="/asistencia", tags=["asistencia"])

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Token inválido o expirado")

@router.get("/", response_model=List[AsistenciaResponse])
def list_asistencias(current_user=Depends(get_current_user)):
    use_case = AsistenciaUseCase(AsistenciaRepository())
    return use_case.list_asistencias()

@router.post("/", response_model=AsistenciaResponse)
def create_asistencia(request: AsistenciaRequest, current_user=Depends(get_current_user)):
    use_case = AsistenciaUseCase(AsistenciaRepository())
    return use_case.create_asistencia(request)

@router.get("/{id_personal}", response_model=List[AsistenciaResponse])
def get_asistencia_personal(id_personal: int, current_user=Depends(get_current_user)):
    use_case = AsistenciaUseCase(AsistenciaRepository())
    return use_case.get_asistencia_personal(id_personal) 