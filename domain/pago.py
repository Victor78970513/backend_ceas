from dataclasses import dataclass
from typing import Optional

@dataclass
class Pago:
    id_pago: int
    id_accion: int
    fecha_de_pago: Optional[str]
    monto: float
    tipo_pago: int
    estado_pago: int
    observaciones: Optional[str] 