from infrastructure.pago_repository import PagoRepository
from schemas.pago import PagoRequest, PagoResponse, PagoUpdateRequest, PagoEstadoRequest
from fastapi import HTTPException
from typing import List

class PagoUseCase:
    def __init__(self, pago_repository: PagoRepository):
        self.pago_repository = pago_repository

    def list_pagos(self) -> List[PagoResponse]:
        pagos = self.pago_repository.list_pagos()
        return [PagoResponse(**pago.__dict__) for pago in pagos]

    def get_pago(self, pago_id: int) -> PagoResponse:
        pago = self.pago_repository.get_pago(pago_id)
        if not pago:
            raise HTTPException(status_code=404, detail="Pago no encontrado")
        return PagoResponse(**pago.__dict__)

    def create_pago(self, data: PagoRequest) -> PagoResponse:
        pago = self.pago_repository.create_pago(data)
        return PagoResponse(**pago.__dict__)

    def update_pago(self, pago_id: int, data: PagoUpdateRequest) -> PagoResponse:
        pago = self.pago_repository.update_pago(pago_id, data)
        if not pago:
            raise HTTPException(status_code=404, detail="Pago no encontrado")
        return PagoResponse(**pago.__dict__)

    def cambiar_estado(self, pago_id: int, data: PagoEstadoRequest) -> PagoResponse:
        pago = self.pago_repository.cambiar_estado(pago_id, data)
        if not pago:
            raise HTTPException(status_code=404, detail="Pago no encontrado")
        return PagoResponse(**pago.__dict__)

    def delete_pago(self, pago_id: int) -> dict:
        success = self.pago_repository.delete_pago(pago_id)
        if not success:
            raise HTTPException(status_code=404, detail="Pago no encontrado")
        return {"detail": "Pago eliminado correctamente"} 