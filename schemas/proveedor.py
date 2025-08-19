from pydantic import BaseModel
from typing import Optional

class ProveedorRequest(BaseModel):
    nombre_proveedor: str
    contacto: Optional[str] = None
    telefono: Optional[str] = None
    correo_electronico: Optional[str] = None
    direccion: Optional[str] = None
    estado: bool = True
    productos_servicios: Optional[str] = None

class ProveedorResponse(BaseModel):
    id_proveedor: int
    nombre_proveedor: str
    contacto: Optional[str] = None
    telefono: Optional[str] = None
    correo_electronico: Optional[str] = None
    direccion: Optional[str] = None
    estado: bool
    productos_servicios: Optional[str] = None

class ProveedorUpdateRequest(BaseModel):
    nombre_proveedor: Optional[str]
    contacto: Optional[str]
    telefono: Optional[str]
    correo_electronico: Optional[str]
    direccion: Optional[str]
    estado: Optional[bool]
    productos_servicios: Optional[str] 