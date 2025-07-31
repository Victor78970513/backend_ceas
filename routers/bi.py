from fastapi import APIRouter, Depends, HTTPException
from use_cases.bi import BIUseCase
from fastapi.security import OAuth2PasswordBearer
import jwt
from config import SECRET_KEY, ALGORITHM

router = APIRouter(prefix="/bi", tags=["bi"])

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Token inválido o expirado")

@router.get("/dashboard")
def get_dashboard(current_user=Depends(get_current_user)):
    use_case = BIUseCase()
    return use_case.get_dashboard()

@router.get("/reportes")
def get_reportes(current_user=Depends(get_current_user)):
    use_case = BIUseCase()
    return use_case.get_reportes()

@router.get("/metricas")
def get_metricas(current_user=Depends(get_current_user)):
    use_case = BIUseCase()
    return use_case.get_metricas()

@router.get("/descargas")
def get_descargas(current_user=Depends(get_current_user)):
    use_case = BIUseCase()
    return use_case.get_descargas() 