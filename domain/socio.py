from dataclasses import dataclass
from typing import Optional

@dataclass
class Socio:
    id_socio: int
    id_club: int
    nombres: str
    apellidos: str
    ci_nit: str
    telefono: str
    correo_electronico: str
    direccion: str
    estado: int
    fecha_de_registro: Optional[str] = None
    fecha_nacimiento: Optional[str] = None
    tipo_membresia: Optional[str] = None
    id_usuario: Optional[int] = None  # Relación con usuario para login 