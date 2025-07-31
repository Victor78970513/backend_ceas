from pydantic import BaseModel
from typing import Optional

class ProductoInventarioRequest(BaseModel):
    nombre_producto: str
    descripcion: Optional[str] = None
    cantidad_en_stock: int
    precio_unitario: float
    id_club: int

class ProductoInventarioResponse(BaseModel):
    id_producto: int
    nombre_producto: str
    descripcion: Optional[str] = None
    cantidad_en_stock: int
    precio_unitario: float
    id_club: int

class ProductoInventarioUpdateRequest(BaseModel):
    nombre_producto: Optional[str]
    descripcion: Optional[str]
    cantidad_en_stock: Optional[int]
    precio_unitario: Optional[float]
    id_club: Optional[int] 