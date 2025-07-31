from dataclasses import dataclass
from typing import Optional

@dataclass
class Evento:
    id_evento: int
    nombre_evento: str
    descripcion: Optional[str]
    fecha: str
    hora: str
    id_club: int
    estado: str 