from pydantic import BaseModel
from typing import Optional

class MovimientoFinancieroRequest(BaseModel):
    id_club: int
    tipo_movimiento: str
    descripcion: str
    monto: float
    estado: str
    referencia_relacionada: Optional[str] = None
    metodo_pago: Optional[str] = None

class MovimientoFinancieroResponse(BaseModel):
    id_movimiento: int
    id_club: int
    tipo_movimiento: str
    descripcion: str
    monto: float
    fecha: Optional[str] = None
    estado: str
    referencia_relacionada: Optional[str] = None
    metodo_pago: Optional[str] = None

class MovimientoFinancieroUpdateRequest(BaseModel):
    tipo_movimiento: Optional[str]
    descripcion: Optional[str]
    monto: Optional[float]
    estado: Optional[str]
    referencia_relacionada: Optional[str]
    metodo_pago: Optional[str] 