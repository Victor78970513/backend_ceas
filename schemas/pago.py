from pydantic import BaseModel
from typing import Optional

class PagoRequest(BaseModel):
    id_accion: int
    monto: float
    tipo_pago: int
    estado_pago: int
    observaciones: Optional[str] = None

class PagoResponse(BaseModel):
    id_pago: int
    id_accion: int
    fecha_de_pago: Optional[str] = None
    monto: float
    tipo_pago: int
    estado_pago: int
    observaciones: Optional[str] = None

class PagoUpdateRequest(BaseModel):
    monto: Optional[float]
    tipo_pago: Optional[int]
    estado_pago: Optional[int]
    observaciones: Optional[str]

class PagoEstadoRequest(BaseModel):
    estado_pago: int 