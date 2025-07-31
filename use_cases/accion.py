from infrastructure.accion_repository import AccionRepository
from schemas.accion import AccionRequest, AccionResponse, AccionUpdateRequest
from fastapi import HTTPException
from typing import List

class AccionUseCase:
    def __init__(self, accion_repository: AccionRepository):
        self.accion_repository = accion_repository

    def list_acciones(self) -> List[AccionResponse]:
        acciones = self.accion_repository.list_acciones()
        return [AccionResponse(**accion.__dict__) for accion in acciones]

    def get_accion(self, accion_id: int) -> AccionResponse:
        accion = self.accion_repository.get_accion(accion_id)
        if not accion:
            raise HTTPException(status_code=404, detail="Acción no encontrada")
        return AccionResponse(**accion.__dict__)

    def create_accion(self, data: AccionRequest) -> AccionResponse:
        accion = self.accion_repository.create_accion(data)
        return AccionResponse(**accion.__dict__)

    def update_accion(self, accion_id: int, data: AccionUpdateRequest) -> AccionResponse:
        accion = self.accion_repository.update_accion(accion_id, data)
        if not accion:
            raise HTTPException(status_code=404, detail="Acción no encontrada")
        return AccionResponse(**accion.__dict__)

    def delete_accion(self, accion_id: int) -> dict:
        success = self.accion_repository.delete_accion(accion_id)
        if not success:
            raise HTTPException(status_code=404, detail="Acción no encontrada")
        return {"detail": "Acción eliminada correctamente"}

    def generar_certificado(self, accion_id: int):
        # Placeholder
        return {"detail": "Certificado generado (placeholder)"}

    def ver_certificado(self, accion_id: int):
        # Placeholder
        return {"detail": "Descarga de certificado (placeholder)"}

    def cifrar_certificado(self, accion_id: int):
        # Placeholder
        return {"detail": "Certificado cifrado (placeholder)"}

    def get_pagos(self, accion_id: int):
        # Placeholder
        return [] 