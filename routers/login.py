from fastapi import APIRouter, Depends
from schemas.user import UserLoginRequest, UserLoginResponse, UserRegisterRequest
from use_cases.login import LoginUseCase
from use_cases.register import RegisterUseCase
from infrastructure.user_repository import UserRepository
from fastapi.security import OAuth2PasswordBearer
from fastapi import HTTPException
import jwt
from config import SECRET_KEY, ALGORITHM

router = APIRouter()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")

def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Token inválido o expirado")

@router.post("/login", response_model=UserLoginResponse)
def login(request: UserLoginRequest):
    use_case = LoginUseCase(UserRepository())
    return use_case.login(request)

@router.post("/register", response_model=UserLoginResponse)
def register(request: UserRegisterRequest):
    use_case = RegisterUseCase(UserRepository())
    return use_case.register(request)

@router.get("/verify", response_model=UserLoginResponse)
def verify_token(current_user=Depends(get_current_user)):
    """Verifica si el token JWT es válido y retorna la misma respuesta que el login"""
    user_repository = UserRepository()
    user = user_repository.get_user(current_user.get("id_usuario"))
    
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    
    # Obtener socio_id si el usuario es un socio (rol = 4)
    socio_id = None
    if user.rol == 4:  # Rol de socio
        try:
            from infrastructure.socio_repository import SocioRepository
            socio_repository = SocioRepository()
            socio = socio_repository.get_socio_by_usuario_id(user.id_usuario)
            if socio:
                socio_id = socio.id_socio
        except Exception as e:
            # Si hay error obteniendo el socio, continuar sin socio_id
            import logging
            logging.warning(f"No se pudo obtener socio_id para usuario {user.id_usuario}: {str(e)}")
    
    # Generar nuevo token
    from infrastructure.security import create_access_token
    new_token = create_access_token({
        "sub": user.nombre_usuario,
        "id_usuario": user.id_usuario,
        "rol": user.rol,
        "id_club": user.id_club
    })
    
    return UserLoginResponse(
        access_token=new_token,
        nombre_usuario=user.nombre_usuario,
        rol=user.rol,
        id_usuario=user.id_usuario,
        id_club=user.id_club,
        correo_electronico=user.correo_electronico,
        socio_id=socio_id
    )

@router.get("/me")
def get_current_user_info(current_user=Depends(get_current_user)):
    """Obtiene información del usuario actual"""
    user_repository = UserRepository()
    user = user_repository.get_user(current_user.get("id_usuario"))
    
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    
    return {
        "id_usuario": user.id_usuario,
        "nombre_usuario": user.nombre_usuario,
        "rol": user.rol,
        "estado": user.estado,
        "id_club": user.id_club,
        "correo_electronico": user.correo_electronico,
        "ultimo_acceso": user.ultimo_acceso
    } 