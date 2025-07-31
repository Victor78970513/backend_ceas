from infrastructure.compra_repository import CompraRepository
from schemas.compra import CompraRequest, CompraResponse, CompraUpdateRequest
from fastapi import HTTPException
from typing import List

class CompraUseCase:
    def __init__(self, compra_repository: CompraRepository):
        self.compra_repository = compra_repository

    def list_compras(self) -> List[CompraResponse]:
        compras = self.compra_repository.list_compras()
        return [CompraResponse(**c.__dict__) for c in compras]

    def get_compra(self, compra_id: int) -> CompraResponse:
        c = self.compra_repository.get_compra(compra_id)
        if not c:
            raise HTTPException(status_code=404, detail="Compra no encontrada")
        return CompraResponse(**c.__dict__)

    def create_compra(self, data: CompraRequest) -> CompraResponse:
        c = self.compra_repository.create_compra(data)
        return CompraResponse(**c.__dict__)

    def update_compra(self, compra_id: int, data: CompraUpdateRequest) -> CompraResponse:
        c = self.compra_repository.update_compra(compra_id, data)
        if not c:
            raise HTTPException(status_code=404, detail="Compra no encontrada")
        return CompraResponse(**c.__dict__)

    def delete_compra(self, compra_id: int) -> dict:
        success = self.compra_repository.delete_compra(compra_id)
        if not success:
            raise HTTPException(status_code=404, detail="Compra no encontrada")
        return {"detail": "Compra eliminada correctamente"} 