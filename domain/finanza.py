from dataclasses import dataclass
from typing import Optional
from decimal import Decimal

@dataclass
class MovimientoFinanciero:
    id_movimiento: int
    id_club: int
    tipo_movimiento: str
    descripcion: str
    monto: Decimal
    fecha: Optional[str]
    estado: str
    referencia_relacionada: Optional[str]
    metodo_pago: Optional[str]
    # Campos adicionales para el frontend
    nombre_club: Optional[str] = None
    categoria: Optional[str] = None
    nombre_socio: Optional[str] = None
    nombre_proveedor: Optional[str] = None
    numero_comprobante: Optional[str] = None 