from pydantic import BaseModel
from typing import Optional

class CompraRequest(BaseModel):
    id_proveedor: int
    monto_total: float
    estado: str
    numero_factura: Optional[str] = None
    observaciones: Optional[str] = None

class CompraResponse(BaseModel):
    id_compra: int
    id_proveedor: int
    fecha_de_compra: Optional[str] = None
    monto_total: float
    estado: str
    numero_factura: Optional[str] = None
    observaciones: Optional[str] = None
    proveedor: Optional[str] = None
    categoria_proveedor: Optional[str] = None

class CompraUpdateRequest(BaseModel):
    id_proveedor: Optional[int]
    monto_total: Optional[float]
    estado: Optional[str]
    numero_factura: Optional[str]
    observaciones: Optional[str] 