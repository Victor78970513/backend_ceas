from pydantic import BaseModel
from typing import Optional

class AsistenciaRequest(BaseModel):
    id_personal: int
    fecha: str
    hora_ingreso: str
    hora_salida: Optional[str] = None
    observaciones: Optional[str] = None

class AsistenciaResponse(BaseModel):
    id_asistencia: int
    id_personal: int
    fecha: str
    hora_ingreso: str
    hora_salida: Optional[str] = None
    observaciones: Optional[str] = None

class AsistenciaUpdateRequest(BaseModel):
    hora_salida: Optional[str]
    observaciones: Optional[str] 