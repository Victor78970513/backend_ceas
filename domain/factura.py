from dataclasses import dataclass
from typing import Optional

@dataclass
class Factura:
    id_factura: int
    id_socio: int
    fecha_de_emision: Optional[str]
    monto_total: float
    estado: str 