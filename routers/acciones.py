from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import Response
from schemas.accion import AccionRequest, AccionResponse, AccionUpdateRequest, AccionResponseCompleta, DescifrarCertificadoRequest
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
def generar_certificado(accion_id: int):
    """Genera certificado cifrado sin requerir autenticación"""
    use_case = AccionUseCase(AccionRepository())
    result = use_case.generar_certificado(accion_id)
    
    # El PDF ahora viene cifrado con contraseña
    if isinstance(result, dict) and 'pdf_cifrado' in result:
        # PDF cifrado - retornar PDF directo con contraseña en headers
        pdf_content = result["pdf_cifrado"]
        password = result["password"]
        filename = f"certificado_accion_{accion_id}_cifrado.pdf"
        
        return Response(
            content=pdf_content,
            media_type="application/pdf",
            headers={
                "Content-Disposition": f"attachment; filename={filename}",
                "Content-Length": str(len(pdf_content)),
                "X-PDF-Password": password,
                "X-PDF-Encrypted": "true",
                "X-PDF-Filename": filename
            }
        )
    else:
        # PDF sin cifrar (fallback)
        pdf_content = result
        filename = f"certificado_accion_{accion_id}.pdf"
        
        return Response(
            content=pdf_content,
            media_type="application/pdf",
            headers={
                "Content-Disposition": f"attachment; filename={filename}",
                "Content-Length": str(len(pdf_content))
            }
        )

@router.post("/descifrar-pdf")
def descifrar_pdf_directo(request: dict, current_user=Depends(get_current_user)):
    """Descifra un PDF directamente enviado en la request"""
    try:
        from infrastructure.pdf_service import PDFService
        import base64
        
        # Obtener PDF cifrado y contraseña de la request
        pdf_cifrado_base64 = request.get('pdf_cifrado_base64')
        password = request.get('password')
        
        if not pdf_cifrado_base64 or not password:
            raise HTTPException(status_code=400, detail="Se requiere pdf_cifrado_base64 y password")
        
        # Decodificar PDF de base64
        pdf_cifrado = base64.b64decode(pdf_cifrado_base64)
        
        # Descifrar usando el servicio
        pdf_service = PDFService()
        pdf_descifrado = pdf_service.descifrar_pdf(pdf_cifrado, password)
        
        if pdf_descifrado:
            filename = "certificado_descifrado.pdf"
            return Response(
                content=pdf_descifrado,
                media_type="application/pdf",
                headers={
                    "Content-Disposition": f"attachment; filename={filename}",
                    "Content-Length": str(len(pdf_descifrado)),
                    "X-PDF-Encrypted": "false"
                }
            )
        else:
            raise HTTPException(status_code=400, detail="No se pudo descifrar el PDF")
            
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error descifrando PDF: {str(e)}")

@router.post("/{accion_id}/descifrar-certificado")
def descifrar_certificado(accion_id: int, request: DescifrarCertificadoRequest, current_user=Depends(get_current_user)):
    """Descifra un certificado PDF con la contraseña proporcionada"""
    use_case = AccionUseCase(AccionRepository())
    result = use_case.descifrar_certificado(accion_id, request.password)
    
    if result:
        filename = f"certificado_accion_{accion_id}_descifrado.pdf"
        return Response(
            content=result,
            media_type="application/pdf",
            headers={
                "Content-Disposition": f"attachment; filename={filename}",
                "Content-Length": str(len(result)),
                "X-PDF-Encrypted": "false"
            }
        )
    else:
        raise HTTPException(status_code=400, detail="Contraseña incorrecta o PDF no encontrado")

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