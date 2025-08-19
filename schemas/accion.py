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
    tipo_accion: Optional[str] = None
    socio_titular: Optional[str] = None

class EstadoAccionInfo(BaseModel):
    id: int
    nombre: str

class EstadoPagosInfo(BaseModel):
    estado_pago: str
    porcentaje_pagado: float
    saldo_pendiente: float
    pagos_restantes: int
    precio_renovacion: float
    total_pagado: float
    pagos_realizados: int

class ModalidadPagoInfo(BaseModel):
    descripcion: str
    meses_de_gracia: int
    porcentaje_renovacion_inicial: float
    porcentaje_renovacion_mensual: float
    costo_renovacion_estandar: float
    cantidad_cuotas: int

class AccionResponseCompleta(BaseModel):
    id_accion: int
    id_club: int
    id_socio: int
    modalidad_pago: int
    estado_accion: int
    certificado_pdf: Optional[str] = None
    certificado_cifrado: bool
    fecha_emision_certificado: Optional[str] = None
    tipo_accion: Optional[str] = None
    socio_titular: Optional[str] = None
    estado_accion_info: EstadoAccionInfo
    estado_pagos: EstadoPagosInfo
    modalidad_pago_info: ModalidadPagoInfo

class AccionUpdateRequest(BaseModel):
    id_club: Optional[int]
    id_socio: Optional[int]
    modalidad_pago: Optional[int]
    estado_accion: Optional[int]
    certificado_pdf: Optional[str]
    certificado_cifrado: Optional[bool]
    saldo_pendiente: Optional[float]
    tipo_accion: Optional[str] 