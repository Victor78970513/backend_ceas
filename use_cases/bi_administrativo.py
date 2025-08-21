from infrastructure.bi_administrativo_repository import BIAdministrativoRepository
from schemas.bi_administrativo import DashboardAdministrativoFinanciero, FiltroBI
from typing import Optional, Dict, List

class BIAdministrativoUseCase:
    def __init__(self, bi_administrativo_repository: BIAdministrativoRepository):
        self.bi_administrativo_repository = bi_administrativo_repository

    def get_dashboard_completo(self, mes: Optional[int] = None, anio: Optional[int] = None,
                              club: Optional[int] = None) -> DashboardAdministrativoFinanciero:
        """Obtiene dashboard completo administrativo y financiero"""
        dashboard_data = self.bi_administrativo_repository.get_dashboard_completo(mes, anio, club)
        return DashboardAdministrativoFinanciero(**dashboard_data)

    def get_metricas_financieras(self, mes: Optional[int] = None, anio: Optional[int] = None,
                                club: Optional[int] = None) -> Dict:
        """Obtiene solo métricas financieras"""
        dashboard_data = self.bi_administrativo_repository.get_dashboard_completo(mes, anio, club)
        return dashboard_data["metricas_financieras"]

    def get_metricas_administrativas(self, mes: Optional[int] = None, anio: Optional[int] = None,
                                    club: Optional[int] = None) -> Dict:
        """Obtiene solo métricas administrativas"""
        dashboard_data = self.bi_administrativo_repository.get_dashboard_completo(mes, anio, club)
        return dashboard_data["metricas_administrativas"]

    def get_top_clubes(self, mes: Optional[int] = None, anio: Optional[int] = None,
                      club: Optional[int] = None) -> List[Dict]:
        """Obtiene top clubes por rendimiento"""
        dashboard_data = self.bi_administrativo_repository.get_dashboard_completo(mes, anio, club)
        return dashboard_data["top_clubes"]

    def get_top_socios(self, mes: Optional[int] = None, anio: Optional[int] = None,
                      club: Optional[int] = None) -> List[Dict]:
        """Obtiene top socios por inversión"""
        dashboard_data = self.bi_administrativo_repository.get_dashboard_completo(mes, anio, club)
        return dashboard_data["top_socios"]

    def get_distribucion_financiera(self, mes: Optional[int] = None, anio: Optional[int] = None,
                                  club: Optional[int] = None, tipo: str = "INGRESO") -> List[Dict]:
        """Obtiene distribución financiera por tipo (INGRESO/EGRESO)"""
        dashboard_data = self.bi_administrativo_repository.get_dashboard_completo(mes, anio, club)
        if tipo.upper() == "INGRESO":
            return dashboard_data["distribucion_ingresos"]
        else:
            return dashboard_data["distribucion_egresos"]

    def get_kpis_principales(self, mes: Optional[int] = None, anio: Optional[int] = None,
                            club: Optional[int] = None) -> List[Dict]:
        """Obtiene KPIs principales del negocio"""
        dashboard_data = self.bi_administrativo_repository.get_dashboard_completo(mes, anio, club)
        return dashboard_data["kpis_principales"]

    def get_tendencias_mensuales(self, anio: Optional[int] = None, club: Optional[int] = None) -> Dict:
        """Obtiene tendencias mensuales del año"""
        dashboard_data = self.bi_administrativo_repository.get_dashboard_completo(None, anio, club)
        return dashboard_data["tendencias_mensuales"]

    def get_alertas_criticas(self, mes: Optional[int] = None, anio: Optional[int] = None,
                            club: Optional[int] = None) -> List[str]:
        """Obtiene alertas críticas del sistema"""
        dashboard_data = self.bi_administrativo_repository.get_dashboard_completo(mes, anio, club)
        return dashboard_data["alertas_criticas"]

    def get_movimientos_financieros_detallados(self, dias: int = 90, club: Optional[int] = None) -> Dict:
        """Obtiene movimientos financieros detallados día a día para gráficas de alta resolución"""
        return self.bi_administrativo_repository.get_movimientos_financieros_detallados(dias, club)

