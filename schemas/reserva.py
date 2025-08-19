from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class ReservaRequest(BaseModel):
    id_evento: int
    id_socio: int
    fecha_reserva: datetime
    estado: str
    notas: Optional[str] = None

class ReservaResponse(BaseModel):
    id_reserva: int
    id_evento: int
    id_socio: int
    fecha_reserva: str
    estado: str
    notas: Optional[str] = None
    fecha_creacion: str

class ReservaUpdateRequest(BaseModel):
    id_evento: Optional[int] = None
    id_socio: Optional[int] = None
    fecha_reserva: Optional[datetime] = None
    estado: Optional[str] = None
    notas: Optional[str] = None

class ReservaDeleteResponse(BaseModel):
    detail: str




