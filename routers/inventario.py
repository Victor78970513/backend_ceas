from fastapi import APIRouter, Depends, HTTPException
from schemas.inventario import ProductoInventarioRequest, ProductoInventarioResponse, ProductoInventarioUpdateRequest
from use_cases.inventario import InventarioUseCase
from infrastructure.inventario_repository import InventarioRepository
from fastapi.security import OAuth2PasswordBearer
from typing import List
import jwt
from config import SECRET_KEY, ALGORITHM

router = APIRouter(prefix="/inventario", tags=["inventario"])

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Token inválido o expirado")

@router.get("/", response_model=List[ProductoInventarioResponse])
def list_productos(current_user=Depends(get_current_user)):
    use_case = InventarioUseCase(InventarioRepository())
    return use_case.list_productos()

@router.post("/", response_model=ProductoInventarioResponse)
def create_producto(request: ProductoInventarioRequest, current_user=Depends(get_current_user)):
    use_case = InventarioUseCase(InventarioRepository())
    return use_case.create_producto(request)

@router.get("/{producto_id}", response_model=ProductoInventarioResponse)
def get_producto(producto_id: int, current_user=Depends(get_current_user)):
    use_case = InventarioUseCase(InventarioRepository())
    return use_case.get_producto(producto_id)

@router.put("/{producto_id}", response_model=ProductoInventarioResponse)
def update_producto(producto_id: int, request: ProductoInventarioUpdateRequest, current_user=Depends(get_current_user)):
    use_case = InventarioUseCase(InventarioRepository())
    return use_case.update_producto(producto_id, request)

@router.delete("/{producto_id}")
def delete_producto(producto_id: int, current_user=Depends(get_current_user)):
    use_case = InventarioUseCase(InventarioRepository())
    return use_case.delete_producto(producto_id) 