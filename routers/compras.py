from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from schemas.compra import CompraRequest, CompraResponse, CompraUpdateRequest
from use_cases.compra import CompraUseCase
from infrastructure.compra_repository import CompraRepository
from infrastructure.reporte_compras_service import ReporteComprasService
from infrastructure.proveedor_repository import ProveedorRepository
from use_cases.proveedor import ProveedorUseCase
from fastapi.security import OAuth2PasswordBearer
from typing import List
import jwt
from config import SECRET_KEY, ALGORITHM
from datetime import datetime
from io import BytesIO

router = APIRouter(prefix="/compras", tags=["compras"])

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")

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

@router.get("/reporte/descargar")
def descargar_reporte_compras(current_user=Depends(get_current_user)):
    """
    Genera y descarga un reporte de compras y proveedores en formato PDF con gráficas profesionales
    """
    try:
        # Obtener todas las compras
        compra_use_case = CompraUseCase(CompraRepository())
        compras = compra_use_case.list_compras()
        
        # Obtener todos los proveedores
        proveedor_use_case = ProveedorUseCase(ProveedorRepository())
        proveedores = proveedor_use_case.list_proveedores()
        
        # Preparar datos para el reporte
        compras_data = []
        for compra in compras:
            compras_data.append({
                'id_compra': compra.id_compra,
                'fecha_de_compra': compra.fecha_de_compra,
                'monto_total': float(compra.monto_total),
                'estado': compra.estado,
                'proveedor': compra.proveedor,
                'categoria_proveedor': compra.categoria_proveedor
            })
        
        proveedores_data = []
        for proveedor in proveedores:
            proveedores_data.append({
                'id_proveedor': proveedor.id_proveedor,
                'nombre_proveedor': proveedor.nombre_proveedor,
                'contacto': proveedor.contacto,
                'telefono': proveedor.telefono,
                'categoria': proveedor.categoria,
                'estado': proveedor.estado
            })
        
        # Generar PDF con gráficas
        reporte_service = ReporteComprasService()
        pdf_data = reporte_service.generar_pdf_compras(compras_data, proveedores_data)
        
        fecha_str = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"reporte_compras_{fecha_str}.pdf"
        
        # Retornar archivo para descarga
        return StreamingResponse(
            BytesIO(pdf_data),
            media_type="application/pdf",
            headers={
                "Content-Disposition": f"attachment; filename={filename}"
            }
        )
        
    except Exception as e:
        import traceback
        import logging
        logging.error(f"Error al generar reporte de compras: {str(e)}")
        logging.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Error al generar reporte: {str(e)}") 