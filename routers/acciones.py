from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import Response
from schemas.accion import AccionRequest, AccionResponse, AccionUpdateRequest, AccionResponseCompleta
from use_cases.accion import AccionUseCase
from infrastructure.accion_repository import AccionRepository
from fastapi.security import OAuth2PasswordBearer
from typing import List
import jwt
from config import SECRET_KEY, ALGORITHM
import base64

router = APIRouter(prefix="/acciones", tags=["acciones"])

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")

def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Token inválido o expirado")

@router.get("/", response_model=List[AccionResponseCompleta])
def list_acciones(current_user=Depends(get_current_user)):
    use_case = AccionUseCase(AccionRepository())
    return use_case.list_acciones()

@router.post("/", response_model=AccionResponse)
def create_accion(request: AccionRequest, current_user=Depends(get_current_user)):
    use_case = AccionUseCase(AccionRepository())
    return use_case.create_accion(request)

@router.get("/{accion_id}", response_model=AccionResponse)
def get_accion(accion_id: int, current_user=Depends(get_current_user)):
    use_case = AccionUseCase(AccionRepository())
    return use_case.get_accion(accion_id)

@router.put("/{accion_id}", response_model=AccionResponse)
def update_accion(accion_id: int, request: AccionUpdateRequest, current_user=Depends(get_current_user)):
    use_case = AccionUseCase(AccionRepository())
    return use_case.update_accion(accion_id, request)

@router.delete("/{accion_id}")
def delete_accion(accion_id: int, current_user=Depends(get_current_user)):
    use_case = AccionUseCase(AccionRepository())
    return use_case.delete_accion(accion_id)

@router.post("/{accion_id}/generar-certificado")
def generar_certificado(accion_id: int, current_user=Depends(get_current_user)):
    use_case = AccionUseCase(AccionRepository())
    result = use_case.generar_certificado(accion_id)
    
    # Retornar PDF como archivo descargable
    pdf_content = result["pdf_content"]
    filename = result["filename"]
    
    return Response(
        content=pdf_content,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f"attachment; filename={filename}",
            "Content-Length": str(len(pdf_content))
        }
    )

@router.get("/{accion_id}/ver-certificado")
def ver_certificado(accion_id: int, current_user=Depends(get_current_user)):
    use_case = AccionUseCase(AccionRepository())
    return use_case.ver_certificado(accion_id)

@router.patch("/{accion_id}/cifrar-certificado")
def cifrar_certificado(accion_id: int, current_user=Depends(get_current_user)):
    use_case = AccionUseCase(AccionRepository())
    return use_case.cifrar_certificado(accion_id)

@router.get("/{accion_id}/pagos")
def get_pagos(accion_id: int, current_user=Depends(get_current_user)):
    use_case = AccionUseCase(AccionRepository())
    return use_case.get_pagos(accion_id)

@router.get("/estado-pagos-resumen")
def list_acciones_con_estado_pagos(current_user=Depends(get_current_user)):
    use_case = AccionUseCase(AccionRepository())
    return use_case.list_acciones_con_estado_pagos()

@router.get("/{accion_id}/estado-pagos")
def get_estado_pagos(accion_id: int, current_user=Depends(get_current_user)):
    use_case = AccionUseCase(AccionRepository())
    return use_case.get_estado_pagos(accion_id) 