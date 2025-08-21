from pydantic import BaseModel
from typing import List, Optional, Dict
from decimal import Decimal

# ===== MÉTRICAS FINANCIERAS =====
class MetricaFinanciera(BaseModel):
    ingresos_totales: Decimal
    egresos_totales: Decimal
    balance_neto: Decimal
    margen_rentabilidad: float
    flujo_caja: Decimal
    proyeccion_mensual: Decimal

class AnalisisClub(BaseModel):
    id_club: int
    nombre_club: str
    ingresos: Decimal
    egresos: Decimal
    balance: Decimal
    rentabilidad: float
    socios_activos: int
    acciones_vendidas: int

class DistribucionFinanciera(BaseModel):
    categoria: str
    monto: Decimal
    porcentaje: float
    tendencia: str  # "creciente", "decreciente", "estable"

# ===== MÉTRICAS ADMINISTRATIVAS =====
class MetricaAdministrativa(BaseModel):
    total_socios: int
    socios_activos: int
    socios_inactivos: int
    tasa_retencion: float
    crecimiento_mensual: float
    eficiencia_operativa: float

class AnalisisSocio(BaseModel):
    id_socio: int
    nombre_completo: str
    club_principal: str
    acciones_compradas: int
    total_invertido: Decimal
    estado_pagos: str
    antiguedad_meses: int

class AnalisisAccion(BaseModel):
    id_accion: int
    tipo_accion: str
    precio_venta: Decimal
    estado_pago: str
    tiempo_pago_dias: int
    rentabilidad_esperada: float

# ===== KPIs DE NEGOCIO =====
class KPINegocio(BaseModel):
    nombre: str
    valor_actual: float
    valor_anterior: float
    cambio_porcentual: float
    meta: float
    estado: str  # "excelente", "bueno", "regular", "crítico"

class TendenciaTemporal(BaseModel):
    periodo: str
    valor: float
    cambio_anterior: float
    proyeccion: float

# ===== DASHBOARD PRINCIPAL =====
class DashboardAdministrativoFinanciero(BaseModel):
    periodo: str
    metricas_financieras: MetricaFinanciera
    metricas_administrativas: MetricaAdministrativa
    top_clubes: List[AnalisisClub]
    top_socios: List[AnalisisSocio]
    distribucion_ingresos: List[DistribucionFinanciera]
    distribucion_egresos: List[DistribucionFinanciera]
    kpis_principales: List[KPINegocio]
    tendencias_mensuales: Dict[str, TendenciaTemporal]
    alertas_criticas: List[str]

class FiltroBI(BaseModel):
    mes: Optional[int] = None  # 1-12
    anio: Optional[int] = None  # 2025
    club: Optional[int] = None
    categoria_financiera: Optional[str] = None
    tipo_analisis: Optional[str] = None  # "financiero", "administrativo", "ambos"

