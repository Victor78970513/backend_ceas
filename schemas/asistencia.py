from pydantic import BaseModel
from typing import Optional

class AsistenciaRequest(BaseModel):
    id_personal: int
    fecha: str
    hora_ingreso: Optional[str] = None
    hora_salida: Optional[str] = None
    observaciones: Optional[str] = None
    estado: Optional[str] = None

class AsistenciaResponse(BaseModel):
    id_asistencia: int
    id_personal: int
    fecha: str
    hora_ingreso: Optional[str] = None
    hora_salida: Optional[str] = None
    observaciones: Optional[str] = None
    estado: Optional[str] = None
    nombre_empleado: Optional[str] = None

class AsistenciaUpdateRequest(BaseModel):
    hora_salida: Optional[str]
    observaciones: Optional[str]
    estado: Optional[str] 