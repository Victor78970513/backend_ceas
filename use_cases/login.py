from infrastructure.user_repository import UserRepository
from infrastructure.security import verify_password, create_access_token
from domain.user import User
from schemas.user import UserLoginRequest, UserLoginResponse
from fastapi import HTTPException

class LoginUseCase:
    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository

    def login(self, login_data: UserLoginRequest) -> UserLoginResponse:
        user: User = self.user_repository.get_by_email(login_data.correo_electronico)
        if not user or not verify_password(login_data.contrasena, user.contrasena_hash):
            raise HTTPException(status_code=401, detail="Credenciales incorrectas")
        
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
        
        token = create_access_token({
            "sub": user.nombre_usuario,
            "id_usuario": user.id_usuario,
            "rol": user.rol,
            "id_club": user.id_club
        })
        
        return UserLoginResponse(
            access_token=token,
            nombre_usuario=user.nombre_usuario,
            rol=user.rol,
            id_usuario=user.id_usuario,
            id_club=user.id_club,
            correo_electronico=user.correo_electronico,
            socio_id=socio_id
        ) 