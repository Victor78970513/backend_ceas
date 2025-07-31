from infrastructure.factura_repository import FacturaRepository
from schemas.factura import FacturaRequest, FacturaResponse, FacturaUpdateRequest
from fastapi import HTTPException
from typing import List

class FacturaUseCase:
    def __init__(self, factura_repository: FacturaRepository):
        self.factura_repository = factura_repository

    def list_facturas(self) -> List[FacturaResponse]:
        facturas = self.factura_repository.list_facturas()
        return [FacturaResponse(**f.__dict__) for f in facturas]

    def get_factura(self, factura_id: int) -> FacturaResponse:
        f = self.factura_repository.get_factura(factura_id)
        if not f:
            raise HTTPException(status_code=404, detail="Factura no encontrada")
        return FacturaResponse(**f.__dict__)

    def create_factura(self, data: FacturaRequest) -> FacturaResponse:
        f = self.factura_repository.create_factura(data)
        return FacturaResponse(**f.__dict__)

    def update_factura(self, factura_id: int, data: FacturaUpdateRequest) -> FacturaResponse:
        f = self.factura_repository.update_factura(factura_id, data)
        if not f:
            raise HTTPException(status_code=404, detail="Factura no encontrada")
        return FacturaResponse(**f.__dict__)

    def delete_factura(self, factura_id: int) -> dict:
        success = self.factura_repository.delete_factura(factura_id)
        if not success:
            raise HTTPException(status_code=404, detail="Factura no encontrada")
        return {"detail": "Factura eliminada correctamente"} 