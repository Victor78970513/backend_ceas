from infrastructure.asistencia_repository import AsistenciaRepository
from schemas.asistencia import AsistenciaRequest, AsistenciaResponse, AsistenciaUpdateRequest
from fastapi import HTTPException
from typing import List

class AsistenciaUseCase:
    def __init__(self, asistencia_repository: AsistenciaRepository):
        self.asistencia_repository = asistencia_repository

    def list_asistencias(self) -> List[AsistenciaResponse]:
        asistencias = self.asistencia_repository.list_asistencias()
        return [AsistenciaResponse(**a.__dict__) for a in asistencias]

    def get_asistencia_personal(self, id_personal: int) -> List[AsistenciaResponse]:
        asistencias = self.asistencia_repository.get_asistencia_personal(id_personal)
        return [AsistenciaResponse(**a.__dict__) for a in asistencias]

    def create_asistencia(self, data: AsistenciaRequest) -> AsistenciaResponse:
        a = self.asistencia_repository.create_asistencia(data)
        return AsistenciaResponse(**a.__dict__)

    def update_asistencia(self, asistencia_id: int, data: AsistenciaUpdateRequest) -> AsistenciaResponse:
        a = self.asistencia_repository.update_asistencia(asistencia_id, data)
        if not a:
            raise HTTPException(status_code=404, detail="Asistencia no encontrada")
        return AsistenciaResponse(**a.__dict__) 