from infrastructure.bi_personal_repository import BIPersonalRepository
from schemas.bi_personal import DashboardPersonalResponse, FiltroPeriodoPersonal
from typing import Optional

class BIPersonalUseCase:
    def __init__(self, bi_personal_repository: BIPersonalRepository):
        self.bi_personal_repository = bi_personal_repository

    def get_dashboard_personal(self, mes: Optional[int] = None, anio: Optional[int] = None,
                              departamento: Optional[str] = None, cargo: Optional[int] = None) -> DashboardPersonalResponse:
        """Obtiene dashboard de personal con métricas agregadas"""
        dashboard_data = self.bi_personal_repository.get_dashboard_personal(mes, anio, departamento, cargo)
        return DashboardPersonalResponse(**dashboard_data)

    def get_metricas_generales(self, departamento: Optional[str] = None, cargo: Optional[int] = None):
        """Obtiene métricas generales del personal"""
        dashboard_data = self.bi_personal_repository.get_dashboard_personal(departamento=departamento, cargo=cargo)
        return dashboard_data["metricas_generales"]

    def get_metricas_asistencia(self, mes: Optional[int] = None, anio: Optional[int] = None,
                               departamento: Optional[str] = None, cargo: Optional[int] = None):
        """Obtiene métricas de asistencia"""
        dashboard_data = self.bi_personal_repository.get_dashboard_personal(mes, anio, departamento, cargo)
        return dashboard_data["metricas_asistencia"]

    def get_top_empleados(self, mes: Optional[int] = None, anio: Optional[int] = None,
                         departamento: Optional[str] = None, cargo: Optional[int] = None):
        """Obtiene top empleados por asistencia"""
        dashboard_data = self.bi_personal_repository.get_dashboard_personal(mes, anio, departamento, cargo)
        return dashboard_data["top_empleados_asistencia"]

    def get_asistencia_por_departamento(self, mes: Optional[int] = None, anio: Optional[int] = None):
        """Obtiene asistencia agrupada por departamento"""
        dashboard_data = self.bi_personal_repository.get_dashboard_personal(mes, anio)
        return dashboard_data["asistencia_por_departamento"]

    def get_tendencias_mensuales(self, anio: int, departamento: Optional[str] = None, cargo: Optional[int] = None):
        """Obtiene tendencias mensuales de asistencia"""
        dashboard_data = self.bi_personal_repository.get_dashboard_personal(anio=anio, departamento=departamento, cargo=cargo)
        return dashboard_data["tendencias_mensuales"]

