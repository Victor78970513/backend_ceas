from dataclasses import dataclass
from typing import Optional

@dataclass
class LogSistema:
    id_log: int
    id_usuario: int
    accion_realizada: str
    fecha_y_hora: Optional[str]
    modulo_o_tabla_afectada: str
    id_afectado: Optional[int]
    descripcion_detallada: Optional[str] 