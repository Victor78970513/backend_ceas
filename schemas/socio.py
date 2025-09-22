from pydantic import BaseModel
from typing import Optional

class SocioRequest(BaseModel):
    id_club: int
    nombres: str
    apellidos: str
    ci_nit: str
    telefono: str
    correo_electronico: str
    direccion: str
    estado: int
    fecha_nacimiento: Optional[str] = None
    tipo_membresia: Optional[str] = None
    id_usuario: Optional[int] = None  # Para asociar con usuario existente

class SocioResponse(BaseModel):
    id_socio: int
    id_club: int
    nombres: str
    apellidos: str
    ci_nit: str
    telefono: str
    correo_electronico: str
    direccion: str
    estado: int
    fecha_de_registro: Optional[str] = None
    fecha_nacimiento: Optional[str] = None
    tipo_membresia: Optional[str] = None
    id_usuario: Optional[int] = None  # Usuario asociado

class SocioUpdateRequest(BaseModel):
    id_club: Optional[int]
    nombres: Optional[str]
    apellidos: Optional[str]
    ci_nit: Optional[str]
    telefono: Optional[str]
    correo_electronico: Optional[str]
    direccion: Optional[str]
    estado: Optional[int]
    fecha_nacimiento: Optional[str]
    tipo_membresia: Optional[str]
    id_usuario: Optional[int]  # Para actualizar asociación con usuario 