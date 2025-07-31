from infrastructure.inventario_repository import InventarioRepository
from schemas.inventario import ProductoInventarioRequest, ProductoInventarioResponse, ProductoInventarioUpdateRequest
from fastapi import HTTPException
from typing import List

class InventarioUseCase:
    def __init__(self, inventario_repository: InventarioRepository):
        self.inventario_repository = inventario_repository

    def list_productos(self) -> List[ProductoInventarioResponse]:
        productos = self.inventario_repository.list_productos()
        return [ProductoInventarioResponse(**p.__dict__) for p in productos]

    def get_producto(self, producto_id: int) -> ProductoInventarioResponse:
        p = self.inventario_repository.get_producto(producto_id)
        if not p:
            raise HTTPException(status_code=404, detail="Producto no encontrado")
        return ProductoInventarioResponse(**p.__dict__)

    def create_producto(self, data: ProductoInventarioRequest) -> ProductoInventarioResponse:
        p = self.inventario_repository.create_producto(data)
        return ProductoInventarioResponse(**p.__dict__)

    def update_producto(self, producto_id: int, data: ProductoInventarioUpdateRequest) -> ProductoInventarioResponse:
        p = self.inventario_repository.update_producto(producto_id, data)
        if not p:
            raise HTTPException(status_code=404, detail="Producto no encontrado")
        return ProductoInventarioResponse(**p.__dict__)

    def delete_producto(self, producto_id: int) -> dict:
        success = self.inventario_repository.delete_producto(producto_id)
        if not success:
            raise HTTPException(status_code=404, detail="Producto no encontrado")
        return {"detail": "Producto eliminado correctamente"} 