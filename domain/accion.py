from dataclasses import dataclass
from typing import Optional

@dataclass
class Accion:
    id_accion: int
    id_club: int
    id_socio: int
    modalidad_pago: int
    estado_accion: int
    certificado_pdf: Optional[str]
    certificado_cifrado: bool
    fecha_emision_certificado: Optional[str]
    tipo_accion: Optional[str]
    socio_titular: Optional[str] = None 