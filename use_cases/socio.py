from infrastructure.socio_repository import SocioRepository
from schemas.socio import SocioRequest, SocioResponse, SocioUpdateRequest
from fastapi import HTTPException
from typing import List

class SocioUseCase:
    def __init__(self, socio_repository: SocioRepository):
        self.socio_repository = socio_repository

    def list_socios(self) -> List[SocioResponse]:
        socios = self.socio_repository.list_socios()
        return [SocioResponse(**socio.__dict__) for socio in socios]

    def get_socio(self, socio_id: int) -> SocioResponse:
        socio = self.socio_repository.get_socio(socio_id)
        if not socio:
            raise HTTPException(status_code=404, detail="Socio no encontrado")
        return SocioResponse(**socio.__dict__)

    def create_socio(self, data: SocioRequest) -> SocioResponse:
        socio = self.socio_repository.create_socio(data)
        return SocioResponse(**socio.__dict__)

    def update_socio(self, socio_id: int, data: SocioUpdateRequest) -> SocioResponse:
        socio = self.socio_repository.update_socio(socio_id, data)
        if not socio:
            raise HTTPException(status_code=404, detail="Socio no encontrado")
        return SocioResponse(**socio.__dict__)

    def delete_socio(self, socio_id: int) -> dict:
        success = self.socio_repository.delete_socio(socio_id)
        if not success:
            raise HTTPException(status_code=404, detail="Socio no encontrado")
        return {"detail": "Socio eliminado correctamente"}

    def get_acciones(self, socio_id: int):
        # Placeholder: lógica real se implementará en el módulo de acciones
        return []

    def get_historial_pagos(self, socio_id: int):
        # Placeholder: lógica real se implementará en el módulo de pagos
        return [] 