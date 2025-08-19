from fastapi import APIRouter, Depends, HTTPException
from schemas.proveedor import ProveedorRequest, ProveedorResponse, ProveedorUpdateRequest
from use_cases.proveedor import ProveedorUseCase
from infrastructure.proveedor_repository import ProveedorRepository
from fastapi.security import OAuth2PasswordBearer
from typing import List
import jwt
from config import SECRET_KEY, ALGORITHM

router = APIRouter(prefix="/proveedores", tags=["proveedores"])

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")

def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Token inválido o expirado")

@router.get("/", response_model=List[ProveedorResponse])
def list_proveedores(current_user=Depends(get_current_user)):
    use_case = ProveedorUseCase(ProveedorRepository())
    return use_case.list_proveedores()

@router.post("/", response_model=ProveedorResponse)
def create_proveedor(request: ProveedorRequest, current_user=Depends(get_current_user)):
    use_case = ProveedorUseCase(ProveedorRepository())
    return use_case.create_proveedor(request)

@router.get("/{proveedor_id}", response_model=ProveedorResponse)
def get_proveedor(proveedor_id: int, current_user=Depends(get_current_user)):
    use_case = ProveedorUseCase(ProveedorRepository())
    return use_case.get_proveedor(proveedor_id)

@router.put("/{proveedor_id}", response_model=ProveedorResponse)
def update_proveedor(proveedor_id: int, request: ProveedorUpdateRequest, current_user=Depends(get_current_user)):
    use_case = ProveedorUseCase(ProveedorRepository())
    return use_case.update_proveedor(proveedor_id, request)

@router.delete("/{proveedor_id}")
def delete_proveedor(proveedor_id: int, current_user=Depends(get_current_user)):
    use_case = ProveedorUseCase(ProveedorRepository())
    return use_case.delete_proveedor(proveedor_id) 