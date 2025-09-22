from fastapi import APIRouter, Depends, HTTPException
from schemas.socio import SocioResponse
from infrastructure.socio_repository import SocioRepository
from fastapi.security import OAuth2PasswordBearer
from typing import Optional
import jwt
from config import SECRET_KEY, ALGORITHM

router = APIRouter(prefix="/socio-profile", tags=["socio-profile"])

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")

def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Token inválido o expirado")

@router.get("/me", response_model=SocioResponse)
def get_my_socio_profile(current_user=Depends(get_current_user)):
    """
    Obtiene el perfil del socio asociado al usuario logueado
    Solo funciona si el usuario tiene un perfil de socio asociado
    """
    user_id = current_user.get("id_usuario")
    if not user_id:
        raise HTTPException(status_code=400, detail="ID de usuario no encontrado en el token")
    
    socio_repository = SocioRepository()
    socio = socio_repository.get_socio_by_usuario_id(user_id)
    
    if not socio:
        raise HTTPException(
            status_code=404, 
            detail="No se encontró un perfil de socio asociado a este usuario. Solo los usuarios con perfil de socio pueden acceder a este endpoint."
        )
    
    return SocioResponse(**socio.__dict__)

@router.get("/check")
def check_socio_profile(current_user=Depends(get_current_user)):
    """
    Verifica si el usuario logueado tiene un perfil de socio asociado
    Retorna información básica sobre si existe la relación
    """
    user_id = current_user.get("id_usuario")
    if not user_id:
        raise HTTPException(status_code=400, detail="ID de usuario no encontrado en el token")
    
    socio_repository = SocioRepository()
    socio = socio_repository.get_socio_by_usuario_id(user_id)
    
    return {
        "has_socio_profile": socio is not None,
        "user_id": user_id,
        "user_role": current_user.get("rol"),
        "socio_id": socio.id_socio if socio else None,
        "message": "Perfil de socio encontrado" if socio else "Usuario sin perfil de socio"
    }
