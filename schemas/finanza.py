from pydantic import BaseModel
from typing import Optional
from decimal import Decimal

class MovimientoFinancieroRequest(BaseModel):
    id_club: int
    tipo_movimiento: str
    descripcion: str
    monto: Decimal
    estado: str
    referencia_relacionada: Optional[str] = None
    metodo_pago: Optional[str] = None

class MovimientoFinancieroResponse(BaseModel):
    id_movimiento: int
    id_club: int
    tipo_movimiento: str
    descripcion: str
    monto: Decimal
    fecha: Optional[str] = None
    estado: str
    referencia_relacionada: Optional[str] = None
    metodo_pago: Optional[str] = None
    # Nuevos campos para el frontend
    nombre_club: Optional[str] = None
    categoria: Optional[str] = None
    nombre_socio: Optional[str] = None
    nombre_proveedor: Optional[str] = None
    numero_comprobante: Optional[str] = None

class MovimientoFinancieroUpdateRequest(BaseModel):
    tipo_movimiento: Optional[str]
    descripcion: Optional[str]
    monto: Optional[Decimal]
    estado: Optional[str]
    referencia_relacionada: Optional[str]
    metodo_pago: Optional[str] 