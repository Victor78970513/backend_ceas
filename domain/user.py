from dataclasses import dataclass
from typing import Optional

@dataclass
class User:
    id_usuario: int
    nombre_usuario: str
    contrasena_hash: str
    rol: int
    estado: str
    id_club: int
    ultimo_acceso: Optional[str] = None 