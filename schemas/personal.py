from pydantic import BaseModel
from typing import Optional

class PersonalRequest(BaseModel):
    id_club: int
    nombres: str
    apellidos: str
    cargo: int
    salario: float

class PersonalResponse(BaseModel):
    id_personal: int
    id_club: int
    nombres: str
    apellidos: str
    cargo: int
    fecha_ingreso: Optional[str] = None
    salario: float

class PersonalUpdateRequest(BaseModel):
    id_club: Optional[int]
    nombres: Optional[str]
    apellidos: Optional[str]
    cargo: Optional[int]
    salario: Optional[float] 