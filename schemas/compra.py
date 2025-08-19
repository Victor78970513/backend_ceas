from pydantic import BaseModel
from typing import Optional

class CompraRequest(BaseModel):
    id_proveedor: int
    monto_total: float
    estado: str
    fecha_de_entrega: Optional[str] = None
    cantidad_items: int

class CompraResponse(BaseModel):
    id_compra: int
    id_proveedor: int
    fecha_de_compra: Optional[str] = None
    monto_total: float
    estado: str
    fecha_de_entrega: Optional[str] = None
    cantidad_items: int
    categoria: Optional[str] = None
    proveedor: Optional[str] = None

class CompraUpdateRequest(BaseModel):
    id_proveedor: Optional[int]
    monto_total: Optional[float]
    estado: Optional[str]
    fecha_de_entrega: Optional[str]
    cantidad_items: Optional[int] 