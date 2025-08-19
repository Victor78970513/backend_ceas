from fastapi import APIRouter, Depends, HTTPException
from schemas.log import LogSistemaResponse
from use_cases.log import LogUseCase
from infrastructure.log_repository import LogRepository
from fastapi.security import OAuth2PasswordBearer
from typing import List
import jwt
from config import SECRET_KEY, ALGORITHM

router = APIRouter(prefix="/logs", tags=["logs"])

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")

def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Token inválido o expirado")

@router.get("/", response_model=List[LogSistemaResponse])
def list_logs(current_user=Depends(get_current_user)):
    use_case = LogUseCase(LogRepository())
    return use_case.list_logs()

@router.get("/{log_id}", response_model=LogSistemaResponse)
def get_log(log_id: int, current_user=Depends(get_current_user)):
    use_case = LogUseCase(LogRepository())
    return use_case.get_log(log_id) 