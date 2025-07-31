from dataclasses import dataclass
from typing import Optional

@dataclass
class ProductoInventario:
    id_producto: int
    nombre_producto: str
    descripcion: Optional[str]
    cantidad_en_stock: int
    precio_unitario: float
    id_club: int 