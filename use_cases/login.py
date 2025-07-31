from infrastructure.user_repository import UserRepository
from infrastructure.security import verify_password, create_access_token
from domain.user import User
from schemas.user import UserLoginRequest, UserLoginResponse
from fastapi import HTTPException

class LoginUseCase:
    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository

    def login(self, login_data: UserLoginRequest) -> UserLoginResponse:
        user: User = self.user_repository.get_by_username(login_data.nombre_usuario)
        if not user or not verify_password(login_data.contrasena, user.contrasena_hash):
            raise HTTPException(status_code=401, detail="Credenciales incorrectas")
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
            id_club=user.id_club
        ) 