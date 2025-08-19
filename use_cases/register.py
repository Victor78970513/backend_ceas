from infrastructure.user_repository import UserRepository
from infrastructure.security import hash_password, create_access_token
from schemas.user import UserRegisterRequest, UserLoginResponse
from fastapi import HTTPException

class RegisterUseCase:
    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository

    def register(self, register_data: UserRegisterRequest) -> UserLoginResponse:
        # Verificar que el nombre de usuario no exista
        if self.user_repository.get_by_username(register_data.nombre_usuario):
            raise HTTPException(status_code=400, detail="El nombre de usuario ya existe")
        
        # Verificar que el correo electrónico no exista
        if self.user_repository.get_by_email(register_data.correo_electronico):
            raise HTTPException(status_code=400, detail="El correo electrónico ya está registrado")
        
        hashed_password = hash_password(register_data.contrasena)
        user = self.user_repository.create_user(
            nombre_usuario=register_data.nombre_usuario,
            contrasena_hash=hashed_password,
            rol=register_data.rol,
            estado=register_data.estado,
            id_club=register_data.id_club,
            correo_electronico=register_data.correo_electronico
        )
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
            correo_electronico=user.correo_electronico
        ) 