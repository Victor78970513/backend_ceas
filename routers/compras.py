from fastapi import APIRouter, Depends, HTTPException
from schemas.compra import CompraRequest, CompraResponse, CompraUpdateRequest
from use_cases.compra import CompraUseCase
from infrastructure.compra_repository import CompraRepository
from fastapi.security import OAuth2PasswordBearer
from typing import List
import jwt
from config import SECRET_KEY, ALGORITHM

router = APIRouter(prefix="/compras", tags=["compras"])

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Token inválido o expirado")

@router.get("/", response_model=List[CompraResponse])
def list_compras(current_user=Depends(get_current_user)):
    use_case = CompraUseCase(CompraRepository())
    return use_case.list_compras()

@router.post("/", response_model=CompraResponse)
def create_compra(request: CompraRequest, current_user=Depends(get_current_user)):
    use_case = CompraUseCase(CompraRepository())
    return use_case.create_compra(request)

@router.get("/{compra_id}", response_model=CompraResponse)
def get_compra(compra_id: int, current_user=Depends(get_current_user)):
    use_case = CompraUseCase(CompraRepository())
    return use_case.get_compra(compra_id)

@router.put("/{compra_id}", response_model=CompraResponse)
def update_compra(compra_id: int, request: CompraUpdateRequest, current_user=Depends(get_current_user)):
    use_case = CompraUseCase(CompraRepository())
    return use_case.update_compra(compra_id, request)

@router.delete("/{compra_id}")
def delete_compra(compra_id: int, current_user=Depends(get_current_user)):
    use_case = CompraUseCase(CompraRepository())
    return use_case.delete_compra(compra_id) 