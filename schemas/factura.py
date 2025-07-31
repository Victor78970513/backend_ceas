from pydantic import BaseModel
from typing import Optional

class FacturaRequest(BaseModel):
    id_socio: int
    monto_total: float
    estado: str

class FacturaResponse(BaseModel):
    id_factura: int
    id_socio: int
    fecha_de_emision: Optional[str] = None
    monto_total: float
    estado: str

class FacturaUpdateRequest(BaseModel):
    id_socio: Optional[int]
    monto_total: Optional[float]
    estado: Optional[str] 