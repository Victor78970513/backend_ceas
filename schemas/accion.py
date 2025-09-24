from pydantic import BaseModel
from typing import Optional, Dict, Any

class AccionRequest(BaseModel):
    id_club: int
    id_socio: int
    modalidad_pago: int
    estado_accion: int
    certificado_pdf: Optional[str] = None
    certificado_cifrado: bool = False
    saldo_pendiente: Optional[float] = None
    tipo_accion: Optional[str] = None
    
    # Nuevos campos para venta de acciones
    cantidad_acciones: Optional[int] = 1
    precio_unitario: Optional[float] = 0.00
    total_pago: Optional[float] = 0.00
    metodo_pago: Optional[str] = "efectivo"

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
    
    # Nuevos campos para venta de acciones
    cantidad_acciones: Optional[int] = 1
    precio_unitario: Optional[float] = 0.00
    total_pago: Optional[float] = 0.00
    metodo_pago: Optional[str] = "efectivo"
    qr_data: Optional[str] = None
    fecha_venta: Optional[str] = None
    comprobante_path: Optional[str] = None
    fecha_comprobante: Optional[str] = None

# Schemas para Stripe
class StripePaymentRequest(BaseModel):
    id_socio: int
    cantidad_acciones: int
    precio_unitario: float
    total_pago: float
    metodo_pago: str = "stripe"
    modalidad_pago: int
    tipo_accion: str

class StripePaymentResponse(BaseModel):
    payment_intent_id: str
    client_secret: str
    amount: int
    currency: str
    status: str
    metadata: Dict[str, Any]
    description: str
    qr_data: Optional[Dict[str, Any]] = None
    metodo_pago: Optional[str] = None

class StripeWebhookResponse(BaseModel):
    event_type: str
    payment_intent_id: str
    status: str
    amount: Optional[int] = None
    currency: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    action: Optional[str] = None

# Schemas para MercadoPago
class MercadoPagoPaymentRequest(BaseModel):
    id_socio: int
    cantidad_acciones: int
    precio_unitario: float
    total_pago: float
    metodo_pago: str = "mercadopago"
    modalidad_pago: int
    tipo_accion: str

class MercadoPagoPaymentResponse(BaseModel):
    preference_id: str
    init_point: str
    sandbox_init_point: str
    status: str
    amount: float
    currency: str
    external_reference: str
    metadata: Dict[str, Any]
    qr_code: str
    checkout_url: str

class MercadoPagoWebhookResponse(BaseModel):
    event_type: str
    payment_id: Optional[str] = None
    preference_id: Optional[str] = None
    status: str
    external_reference: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    action: Optional[str] = None

# Schemas para PayPal
class PayPalPaymentRequest(BaseModel):
    id_socio: int
    cantidad_acciones: int
    precio_unitario: float
    total_pago: float
    metodo_pago: str = "paypal"
    modalidad_pago: int
    tipo_accion: str

class PayPalPaymentResponse(BaseModel):
    payment_id: str
    state: str
    intent: str
    amount: Dict[str, Any]
    approval_url: str
    external_reference: str
    metadata: Dict[str, Any]

class PayPalExecuteRequest(BaseModel):
    payment_id: str
    payer_id: str

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
    
    # Nuevos campos para venta de acciones
    cantidad_acciones: Optional[int]
    precio_unitario: Optional[float]
    total_pago: Optional[float]
    metodo_pago: Optional[str]
    qr_data: Optional[str]
    fecha_venta: Optional[str]
    comprobante_path: Optional[str]
    fecha_comprobante: Optional[str]

class DescifrarCertificadoRequest(BaseModel):
    password: str

class CertificadoCifradoResponse(BaseModel):
    pdf_cifrado: bytes
    password: str
    salt: str
    password_hash: str
    fecha_cifrado: str 