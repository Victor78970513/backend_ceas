from pydantic import BaseModel
from typing import Optional

class UserLoginRequest(BaseModel):
    correo_electronico: str
    contrasena: str

class UserLoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    nombre_usuario: str
    rol: int
    id_usuario: int
    id_club: int
    correo_electronico: str

class UserRegisterRequest(BaseModel):
    nombre_usuario: str
    contrasena: str
    rol: int
    estado: str
    id_club: int
    correo_electronico: str

class UserResponse(BaseModel):
    id_usuario: int
    nombre_usuario: str
    rol: int
    estado: str
    id_club: int
    correo_electronico: str
    ultimo_acceso: Optional[str] = None

class UserUpdateRequest(BaseModel):
    nombre_usuario: Optional[str]
    contrasena: Optional[str]
    rol: Optional[int]
    estado: Optional[str]
    id_club: Optional[int]
    correo_electronico: Optional[str]

class UserDeleteResponse(BaseModel):
    detail: str 