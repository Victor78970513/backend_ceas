from infrastructure.bi_repository import BIRepository
from schemas.bi import DashboardFinancieroResponse, FiltroPeriodo
from typing import Optional

class BIUseCase:
    def __init__(self, bi_repository: BIRepository):
        self.bi_repository = bi_repository

    def get_dashboard_financiero(self, mes: Optional[int] = None, anio: Optional[int] = None) -> DashboardFinancieroResponse:
        """Obtiene dashboard financiero con métricas agregadas"""
        dashboard_data = self.bi_repository.get_dashboard_financiero(mes, anio)
        return DashboardFinancieroResponse(**dashboard_data)

    def get_dashboard(self):
        """Obtiene dashboard general (método legacy)"""
        return self.get_dashboard_financiero()
    
    def get_finanzas_resumen(self, mes: Optional[int] = None, anio: Optional[int] = None):
        """Obtiene resumen financiero para cards de información rápida"""
        return self.get_dashboard_financiero(mes, anio)

    def get_reportes(self):
        # Placeholder: lógica real de reportes
        return {"reportes": "Reportes interactivos (placeholder)"}

    def get_metricas(self):
        # Placeholder: lógica real de métricas
        return {"metricas": "KPI del club (placeholder)"}

    def get_descargas(self):
        # Placeholder: lógica real de descargas
        return {"descargas": "Exportar reportes (placeholder)"} 