from dataclasses import dataclass
from typing import Optional

@dataclass
class Proveedor:
    id_proveedor: int
    nombre_proveedor: str
    contacto: Optional[str]
    telefono: Optional[str]
    correo_electronico: Optional[str]
    direccion: Optional[str]
    nit: Optional[str]
    estado: bool
    categoria: Optional[str] = None 