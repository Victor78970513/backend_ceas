from pydantic import BaseModel
from typing import List, Optional
from decimal import Decimal

class MetricaAsistencia(BaseModel):
    total_registros: int
    asistencias_completas: int
    tardanzas: int
    ausencias: int
    porcentaje_asistencia: float
    promedio_horas_trabajadas: Optional[float]

class MetricaPersonal(BaseModel):
    total_personal: int
    personal_activo: int
    personal_inactivo: int
    personal_por_departamento: dict
    personal_por_cargo: dict

class AsistenciaPorEmpleado(BaseModel):
    id_personal: int
    nombre_empleado: str
    total_asistencias: int
    tardanzas: int
    ausencias: int
    porcentaje_asistencia: float
    promedio_horas_trabajadas: Optional[float]

class AsistenciaPorDepartamento(BaseModel):
    departamento: str
    total_empleados: int
    promedio_asistencia: float
    total_tardanzas: int
    total_ausencias: int

class DashboardPersonalResponse(BaseModel):
    periodo: str
    metricas_generales: MetricaPersonal
    metricas_asistencia: MetricaAsistencia
    top_empleados_asistencia: List[AsistenciaPorEmpleado]
    asistencia_por_departamento: List[AsistenciaPorDepartamento]
    tendencias_mensuales: dict

class FiltroPeriodoPersonal(BaseModel):
    mes: Optional[int] = None  # 1-12
    anio: Optional[int] = None  # 2025
    departamento: Optional[str] = None
    cargo: Optional[int] = None

