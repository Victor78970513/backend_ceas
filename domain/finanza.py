from dataclasses import dataclass
from typing import Optional

@dataclass
class MovimientoFinanciero:
    id_movimiento: int
    id_club: int
    tipo_movimiento: str
    descripcion: str
    monto: float
    fecha: Optional[str]
    estado: str
    referencia_relacionada: Optional[str]
    metodo_pago: Optional[str] 