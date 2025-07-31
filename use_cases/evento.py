from infrastructure.evento_repository import EventoRepository
from schemas.evento import EventoRequest, EventoResponse, EventoUpdateRequest
from fastapi import HTTPException
from typing import List

class EventoUseCase:
    def __init__(self, evento_repository: EventoRepository):
        self.evento_repository = evento_repository

    def list_eventos(self) -> List[EventoResponse]:
        eventos = self.evento_repository.list_eventos()
        return [EventoResponse(**e.__dict__) for e in eventos]

    def get_evento(self, evento_id: int) -> EventoResponse:
        e = self.evento_repository.get_evento(evento_id)
        if not e:
            raise HTTPException(status_code=404, detail="Evento no encontrado")
        return EventoResponse(**e.__dict__)

    def create_evento(self, data: EventoRequest) -> EventoResponse:
        e = self.evento_repository.create_evento(data)
        return EventoResponse(**e.__dict__)

    def update_evento(self, evento_id: int, data: EventoUpdateRequest) -> EventoResponse:
        e = self.evento_repository.update_evento(evento_id, data)
        if not e:
            raise HTTPException(status_code=404, detail="Evento no encontrado")
        return EventoResponse(**e.__dict__)

    def delete_evento(self, evento_id: int) -> dict:
        success = self.evento_repository.delete_evento(evento_id)
        if not success:
            raise HTTPException(status_code=404, detail="Evento no encontrado")
        return {"detail": "Evento eliminado correctamente"} 