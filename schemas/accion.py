from pydantic import BaseModel
from typing import Optional

class AccionRequest(BaseModel):
    id_club: int
    id_socio: int
    modalidad_pago: int
    estado_accion: int
    certificado_pdf: Optional[str] = None
    certificado_cifrado: bool = False
    saldo_pendiente: Optional[float] = None
    tipo_accion: Optional[str] = None

class AccionResponse(BaseModel):
    id_accion: int
    id_club: int
    id_socio: int
    modalidad_pago: int
    estado_accion: int
    certificado_pdf: Optional[str] = None
    certificado_cifrado: bool
    fecha_emision_certificado: Optional[str] = None
    saldo_pendiente: Optional[float] = None
    tipo_accion: Optional[str] = None

class AccionUpdateRequest(BaseModel):
    id_club: Optional[int]
    id_socio: Optional[int]
    modalidad_pago: Optional[int]
    estado_accion: Optional[int]
    certificado_pdf: Optional[str]
    certificado_cifrado: Optional[bool]
    saldo_pendiente: Optional[float]
    tipo_accion: Optional[str] 