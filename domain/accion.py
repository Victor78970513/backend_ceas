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
    
    # Nuevos campos para venta de acciones
    cantidad_acciones: Optional[int] = 1
    precio_unitario: Optional[float] = 0.00
    total_pago: Optional[float] = 0.00
    metodo_pago: Optional[str] = "efectivo"
    qr_data: Optional[str] = None
    fecha_venta: Optional[str] = None
    comprobante_path: Optional[str] = None
    fecha_comprobante: Optional[str] = None 