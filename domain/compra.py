from dataclasses import dataclass
from typing import Optional

@dataclass
class Compra:
    id_compra: int
    id_proveedor: int
    fecha_de_compra: Optional[str]
    monto_total: float
    estado: str 