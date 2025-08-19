from pydantic import BaseModel
from typing import Optional

class PersonalRequest(BaseModel):
    id_club: int
    nombres: str
    apellidos: str
    cargo: int
    salario: float
    correo: Optional[str] = None
    departamento: Optional[str] = None
    estado: bool = True

class PersonalResponse(BaseModel):
    id_personal: int
    id_club: int
    nombres: str
    apellidos: str
    cargo: int
    fecha_ingreso: Optional[str] = None
    salario: float
    correo: Optional[str] = None
    departamento: Optional[str] = None
    estado: bool
    nombre_cargo: Optional[str] = None

class PersonalUpdateRequest(BaseModel):
    id_club: Optional[int]
    nombres: Optional[str]
    apellidos: Optional[str]
    cargo: Optional[int]
    salario: Optional[float]
    correo: Optional[str]
    departamento: Optional[str]
    estado: Optional[bool] 