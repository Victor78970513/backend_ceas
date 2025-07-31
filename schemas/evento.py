from pydantic import BaseModel
from typing import Optional

class EventoRequest(BaseModel):
    nombre_evento: str
    descripcion: Optional[str] = None
    fecha: str
    hora: str
    id_club: int
    estado: str

class EventoResponse(BaseModel):
    id_evento: int
    nombre_evento: str
    descripcion: Optional[str] = None
    fecha: str
    hora: str
    id_club: int
    estado: str

class EventoUpdateRequest(BaseModel):
    nombre_evento: Optional[str]
    descripcion: Optional[str]
    fecha: Optional[str]
    hora: Optional[str]
    id_club: Optional[int]
    estado: Optional[str] 