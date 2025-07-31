from infrastructure.finanza_repository import FinanzaRepository
from schemas.finanza import MovimientoFinancieroRequest, MovimientoFinancieroResponse, MovimientoFinancieroUpdateRequest
from fastapi import HTTPException
from typing import List

class FinanzaUseCase:
    def __init__(self, finanza_repository: FinanzaRepository):
        self.finanza_repository = finanza_repository

    def list_movimientos(self) -> List[MovimientoFinancieroResponse]:
        movimientos = self.finanza_repository.list_movimientos()
        return [MovimientoFinancieroResponse(**m.__dict__) for m in movimientos]

    def get_movimiento(self, movimiento_id: int) -> MovimientoFinancieroResponse:
        m = self.finanza_repository.get_movimiento(movimiento_id)
        if not m:
            raise HTTPException(status_code=404, detail="Movimiento no encontrado")
        return MovimientoFinancieroResponse(**m.__dict__)

    def create_movimiento(self, data: MovimientoFinancieroRequest) -> MovimientoFinancieroResponse:
        m = self.finanza_repository.create_movimiento(data)
        return MovimientoFinancieroResponse(**m.__dict__)

    def update_movimiento(self, movimiento_id: int, data: MovimientoFinancieroUpdateRequest) -> MovimientoFinancieroResponse:
        m = self.finanza_repository.update_movimiento(movimiento_id, data)
        if not m:
            raise HTTPException(status_code=404, detail="Movimiento no encontrado")
        return MovimientoFinancieroResponse(**m.__dict__)

    def delete_movimiento(self, movimiento_id: int) -> dict:
        success = self.finanza_repository.delete_movimiento(movimiento_id)
        if not success:
            raise HTTPException(status_code=404, detail="Movimiento no encontrado")
        return {"detail": "Movimiento eliminado correctamente"}

    def get_reportes(self):
        # Placeholder para reportes financieros
        return {"detail": "Reportes financieros (placeholder)"} 