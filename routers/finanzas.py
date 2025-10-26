from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from schemas.finanza import MovimientoFinancieroRequest, MovimientoFinancieroResponse, MovimientoFinancieroUpdateRequest
from use_cases.finanza import FinanzaUseCase
from infrastructure.finanza_repository import FinanzaRepository
from infrastructure.reporte_finanzas_service import ReporteFinanzasService
from infrastructure.reporte_contable_service import ReporteContableService
from fastapi.security import OAuth2PasswordBearer
from typing import List
import jwt
from config import SECRET_KEY, ALGORITHM
from datetime import datetime
from io import BytesIO

router = APIRouter(prefix="/finanzas", tags=["finanzas"])

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")

def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Token inválido o expirado")

@router.get("/movimientos", response_model=List[MovimientoFinancieroResponse])
def list_movimientos(current_user=Depends(get_current_user)):
    use_case = FinanzaUseCase(FinanzaRepository())
    return use_case.list_movimientos()

@router.post("/movimientos", response_model=MovimientoFinancieroResponse)
def create_movimiento(request: MovimientoFinancieroRequest, current_user=Depends(get_current_user)):
    use_case = FinanzaUseCase(FinanzaRepository())
    return use_case.create_movimiento(request)

@router.get("/movimientos/{movimiento_id}", response_model=MovimientoFinancieroResponse)
def get_movimiento(movimiento_id: int, current_user=Depends(get_current_user)):
    use_case = FinanzaUseCase(FinanzaRepository())
    return use_case.get_movimiento(movimiento_id)

@router.put("/movimientos/{movimiento_id}", response_model=MovimientoFinancieroResponse)
def update_movimiento(movimiento_id: int, request: MovimientoFinancieroUpdateRequest, current_user=Depends(get_current_user)):
    use_case = FinanzaUseCase(FinanzaRepository())
    return use_case.update_movimiento(movimiento_id, request)

@router.delete("/movimientos/{movimiento_id}")
def delete_movimiento(movimiento_id: int, current_user=Depends(get_current_user)):
    use_case = FinanzaUseCase(FinanzaRepository())
    return use_case.delete_movimiento(movimiento_id)

@router.get("/reportes")
def get_reportes(current_user=Depends(get_current_user)):
    use_case = FinanzaUseCase(FinanzaRepository())
    return use_case.get_reportes()

@router.get("/reporte/descargar")
def descargar_reporte_finanzas(current_user=Depends(get_current_user)):
    """
    Genera y descarga un reporte de finanzas en formato PDF con gráficas profesionales
    """
    try:
        # Obtener todos los movimientos
        use_case = FinanzaUseCase(FinanzaRepository())
        movimientos = use_case.list_movimientos()
        
        # Preparar datos para el reporte
        movimientos_data = []
        for mov in movimientos:
            movimientos_data.append({
                'id_movimiento': mov.id_movimiento,
                'tipo_movimiento': mov.tipo_movimiento,
                'descripcion': mov.descripcion,
                'monto': float(mov.monto),
                'fecha': mov.fecha,
                'estado': mov.estado,
                'metodo_pago': mov.metodo_pago,
                'categoria': mov.categoria
            })
        
        # Generar PDF con gráficas
        reporte_service = ReporteFinanzasService()
        pdf_data = reporte_service.generar_pdf_finanzas(movimientos_data)
        
        fecha_str = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"reporte_finanzas_{fecha_str}.pdf"
        
        # Retornar archivo para descarga
        return StreamingResponse(
            BytesIO(pdf_data),
            media_type="application/pdf",
            headers={
                "Content-Disposition": f"attachment; filename={filename}"
            }
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al generar reporte: {str(e)}")

@router.get("/reporte/contable")
def descargar_reporte_contable(current_user=Depends(get_current_user)):
    """
    Genera y descarga un reporte contable formal en formato PDF
    Incluye Estado de Resultados, Balance General, Flujo de Efectivo y análisis financiero
    """
    try:
        # Generar PDF contable
        reporte_service = ReporteContableService()
        pdf_data = reporte_service.generar_pdf_contable()
        
        fecha_str = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"reporte_contable_{fecha_str}.pdf"
        
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
        logging.error(f"Error al generar reporte contable: {str(e)}")
        logging.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Error al generar reporte contable: {str(e)}") 