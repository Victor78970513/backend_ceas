from pydantic import BaseModel
from typing import List, Dict, Optional
from decimal import Decimal

class MetricaCategoria(BaseModel):
    categoria: str
    monto: Decimal

class MetricasGenerales(BaseModel):
    ingresos: Decimal
    egresos: Decimal
    balance: Decimal
    movimientos: int

class DistribucionClub(BaseModel):
    ingresos: Decimal
    egresos: Decimal
    balance: Decimal

class TopCategorias(BaseModel):
    ingresos: List[MetricaCategoria]
    egresos: List[MetricaCategoria]

# Eliminamos esta clase que no se necesita

class DashboardFinancieroResponse(BaseModel):
    periodo: str
    metricas_generales: MetricasGenerales
    distribucion_por_club: Dict[str, DistribucionClub]
    top_categorias: TopCategorias

class FiltroPeriodo(BaseModel):
    mes: Optional[int] = None  # 1-12
    anio: Optional[int] = None  # 2025
    periodo: Optional[str] = None  # "2025-08" formato
