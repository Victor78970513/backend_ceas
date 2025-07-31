from dataclasses import dataclass
from typing import Optional

@dataclass
class Personal:
    id_personal: int
    id_club: int
    nombres: str
    apellidos: str
    cargo: int
    fecha_ingreso: Optional[str]
    salario: float 