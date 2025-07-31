from pydantic import BaseModel
from typing import Optional

class ReservaRequest(BaseModel):
    id_socio: int
    id_evento: int
    estado: str

class ReservaResponse(BaseModel):
    id_reserva: int
    id_socio: int
    id_evento: int
    fecha_de_reserva: Optional[str] = None
    estado: str

class ReservaUpdateRequest(BaseModel):
    id_socio: Optional[int]
    id_evento: Optional[int]
    estado: Optional[str] 