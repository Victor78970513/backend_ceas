from fastapi import APIRouter, Depends, HTTPException
from schemas.factura import FacturaRequest, FacturaResponse, FacturaUpdateRequest
from use_cases.factura import FacturaUseCase
from infrastructure.factura_repository import FacturaRepository
from fastapi.security import OAuth2PasswordBearer
from typing import List
import jwt
from config import SECRET_KEY, ALGORITHM

router = APIRouter(prefix="/facturacion", tags=["facturacion"])

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")

def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Token inválido o expirado")

@router.get("/", response_model=List[FacturaResponse])
def list_facturas(current_user=Depends(get_current_user)):
    use_case = FacturaUseCase(FacturaRepository())
    return use_case.list_facturas()

@router.post("/", response_model=FacturaResponse)
def create_factura(request: FacturaRequest, current_user=Depends(get_current_user)):
    use_case = FacturaUseCase(FacturaRepository())
    return use_case.create_factura(request)

@router.get("/{factura_id}", response_model=FacturaResponse)
def get_factura(factura_id: int, current_user=Depends(get_current_user)):
    use_case = FacturaUseCase(FacturaRepository())
    return use_case.get_factura(factura_id)

@router.put("/{factura_id}", response_model=FacturaResponse)
def update_factura(factura_id: int, request: FacturaUpdateRequest, current_user=Depends(get_current_user)):
    use_case = FacturaUseCase(FacturaRepository())
    return use_case.update_factura(factura_id, request)

@router.delete("/{factura_id}")
def delete_factura(factura_id: int, current_user=Depends(get_current_user)):
    use_case = FacturaUseCase(FacturaRepository())
    return use_case.delete_factura(factura_id) 