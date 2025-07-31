from dataclasses import dataclass
from typing import Optional

@dataclass
class Reserva:
    id_reserva: int
    id_socio: int
    id_evento: int
    fecha_de_reserva: Optional[str]
    estado: str 