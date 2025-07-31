from infrastructure.reserva_repository import ReservaRepository
from schemas.reserva import ReservaRequest, ReservaResponse, ReservaUpdateRequest
from fastapi import HTTPException
from typing import List, Optional

class ReservaUseCase:
    def __init__(self, reserva_repository: ReservaRepository):
        self.reserva_repository = reserva_repository

    def list_reservas(self, id_evento: Optional[int] = None, id_socio: Optional[int] = None) -> List[ReservaResponse]:
        reservas = self.reserva_repository.list_reservas(id_evento=id_evento, id_socio=id_socio)
        return [ReservaResponse(**r.__dict__) for r in reservas]

    def get_reserva(self, reserva_id: int) -> ReservaResponse:
        r = self.reserva_repository.get_reserva(reserva_id)
        if not r:
            raise HTTPException(status_code=404, detail="Reserva no encontrada")
        return ReservaResponse(**r.__dict__)

    def create_reserva(self, data: ReservaRequest) -> ReservaResponse:
        r = self.reserva_repository.create_reserva(data)
        return ReservaResponse(**r.__dict__)

    def update_reserva(self, reserva_id: int, data: ReservaUpdateRequest) -> ReservaResponse:
        r = self.reserva_repository.update_reserva(reserva_id, data)
        if not r:
            raise HTTPException(status_code=404, detail="Reserva no encontrada")
        return ReservaResponse(**r.__dict__)

    def delete_reserva(self, reserva_id: int) -> dict:
        success = self.reserva_repository.delete_reserva(reserva_id)
        if not success:
            raise HTTPException(status_code=404, detail="Reserva no encontrada")
        return {"detail": "Reserva eliminada correctamente"} 