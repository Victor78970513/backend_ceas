from dataclasses import dataclass
from typing import Optional

@dataclass
class Asistencia:
    id_asistencia: int
    id_personal: int
    fecha: str
    hora_ingreso: str
    hora_salida: Optional[str]
    observaciones: Optional[str] 