from dataclasses import dataclass
from typing import Optional

@dataclass
class Compra:
    id_compra: int
    id_proveedor: int
    fecha_de_compra: Optional[str]
    monto_total: float
    estado: str
    numero_factura: Optional[str] = None
    observaciones: Optional[str] = None
    proveedor: Optional[str] = None
    categoria_proveedor: Optional[str] = None 