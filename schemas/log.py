from pydantic import BaseModel
from typing import Optional

class LogSistemaRequest(BaseModel):
    id_usuario: int
    accion_realizada: str
    modulo_o_tabla_afectada: str
    id_afectado: Optional[int] = None
    descripcion_detallada: Optional[str] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None

class LogSistemaResponse(BaseModel):
    id_log: int
    id_usuario: int
    accion_realizada: str
    fecha_y_hora: Optional[str] = None
    modulo_o_tabla_afectada: str
    id_afectado: Optional[int] = None
    descripcion_detallada: Optional[str] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None 