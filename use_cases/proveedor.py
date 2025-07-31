from infrastructure.proveedor_repository import ProveedorRepository
from schemas.proveedor import ProveedorRequest, ProveedorResponse, ProveedorUpdateRequest
from fastapi import HTTPException
from typing import List

class ProveedorUseCase:
    def __init__(self, proveedor_repository: ProveedorRepository):
        self.proveedor_repository = proveedor_repository

    def list_proveedores(self) -> List[ProveedorResponse]:
        proveedores = self.proveedor_repository.list_proveedores()
        return [ProveedorResponse(**p.__dict__) for p in proveedores]

    def get_proveedor(self, proveedor_id: int) -> ProveedorResponse:
        p = self.proveedor_repository.get_proveedor(proveedor_id)
        if not p:
            raise HTTPException(status_code=404, detail="Proveedor no encontrado")
        return ProveedorResponse(**p.__dict__)

    def create_proveedor(self, data: ProveedorRequest) -> ProveedorResponse:
        p = self.proveedor_repository.create_proveedor(data)
        return ProveedorResponse(**p.__dict__)

    def update_proveedor(self, proveedor_id: int, data: ProveedorUpdateRequest) -> ProveedorResponse:
        p = self.proveedor_repository.update_proveedor(proveedor_id, data)
        if not p:
            raise HTTPException(status_code=404, detail="Proveedor no encontrado")
        return ProveedorResponse(**p.__dict__)

    def delete_proveedor(self, proveedor_id: int) -> dict:
        success = self.proveedor_repository.delete_proveedor(proveedor_id)
        if not success:
            raise HTTPException(status_code=404, detail="Proveedor no encontrado")
        return {"detail": "Proveedor eliminado correctamente"} 