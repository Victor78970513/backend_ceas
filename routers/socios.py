from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse
from schemas.socio import SocioRequest, SocioResponse, SocioUpdateRequest
from use_cases.socio import SocioUseCase
from infrastructure.socio_repository import SocioRepository
from infrastructure.reporte_socios_service import ReporteSociosService
from fastapi.security import OAuth2PasswordBearer
from typing import List
import jwt
from config import SECRET_KEY, ALGORITHM
from io import BytesIO
from datetime import datetime

router = APIRouter(prefix="/socios", tags=["socios"])

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")

def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Token inválido o expirado")

@router.get("/", response_model=List[SocioResponse])
def list_socios(current_user=Depends(get_current_user)):
    use_case = SocioUseCase(SocioRepository())
    return use_case.list_socios()

@router.post("/", response_model=SocioResponse)
def create_socio(request: SocioRequest, current_user=Depends(get_current_user)):
    use_case = SocioUseCase(SocioRepository())
    return use_case.create_socio(request)

@router.get("/{socio_id}", response_model=SocioResponse)
def get_socio(socio_id: int, current_user=Depends(get_current_user)):
    use_case = SocioUseCase(SocioRepository())
    return use_case.get_socio(socio_id)

@router.put("/{socio_id}", response_model=SocioResponse)
def update_socio(socio_id: int, request: SocioUpdateRequest, current_user=Depends(get_current_user)):
    use_case = SocioUseCase(SocioRepository())
    return use_case.update_socio(socio_id, request)

@router.delete("/{socio_id}")
def delete_socio(socio_id: int, current_user=Depends(get_current_user)):
    use_case = SocioUseCase(SocioRepository())
    return use_case.delete_socio(socio_id)

@router.get("/{socio_id}/acciones")
def get_acciones(socio_id: int, current_user=Depends(get_current_user)):
    try:
        use_case = SocioUseCase(SocioRepository())
        return use_case.get_acciones(socio_id)
    except Exception as e:
        import logging
        logging.error(f"Error en get_acciones para socio {socio_id}: {str(e)}")
        import traceback
        logging.error(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")

@router.get("/{socio_id}/acciones-test")
def get_acciones_test(socio_id: int, current_user=Depends(get_current_user)):
    """Endpoint de prueba simple"""
    return {"message": "Endpoint funcionando", "socio_id": socio_id, "acciones": []}

@router.get("/{socio_id}/historial-pagos")
def get_historial_pagos(socio_id: int, current_user=Depends(get_current_user)):
    use_case = SocioUseCase(SocioRepository())
    return use_case.get_historial_pagos(socio_id)

@router.get("/reporte/descargar")
def descargar_reporte_socios(current_user=Depends(get_current_user)):
    """
    Genera y descarga un reporte de socios en formato PDF con gráficas profesionales
    """
    try:
        # Obtener todos los socios
        use_case = SocioUseCase(SocioRepository())
        socios = use_case.list_socios()
        
        # Obtener cantidad de acciones por socio
        from sqlalchemy.orm import Session
        from sqlalchemy import text
        from config import SessionLocal
        
        db: Session = SessionLocal()
        accion_counts = {}
        try:
            result = db.execute(text("""
                SELECT id_socio, COUNT(*) as cantidad
                FROM accion
                GROUP BY id_socio
            """)).fetchall()
            for row in result:
                accion_counts[row[0]] = row[1]
        finally:
            db.close()
        
        # Convertir a diccionarios para el servicio de reportes
        socios_data = []
        for socio in socios:
            # Obtener fecha_ingreso de forma segura
            fecha_ingreso = None
            if hasattr(socio, 'fecha_ingreso') and socio.fecha_ingreso:
                if hasattr(socio.fecha_ingreso, 'strftime'):
                    fecha_ingreso = socio.fecha_ingreso.strftime('%d/%m/%Y')
                else:
                    fecha_ingreso = str(socio.fecha_ingreso)
            
            # Determinar estado correctamente (1=Activo, 2=Inactivo)
            if hasattr(socio, 'estado'):
                if socio.estado == 1:
                    estado_str = 'Activo'
                elif socio.estado == 2:
                    estado_str = 'Inactivo'
                else:
                    estado_str = 'Desconocido'
            else:
                estado_str = 'Sin estado'
            
            socios_data.append({
                'id_socio': socio.id_socio,
                'nombres': socio.nombres,
                'apellidos': socio.apellidos,
                'correo_electronico': socio.correo_electronico,
                'telefono': socio.telefono if hasattr(socio, 'telefono') else None,
                'direccion': socio.direccion if hasattr(socio, 'direccion') else None,
                'fecha_ingreso': fecha_ingreso,
                'estado': estado_str,
                'cantidad_acciones': accion_counts.get(socio.id_socio, 0)
            })
        
        # Generar PDF con gráficas
        reporte_service = ReporteSociosService()
        pdf_data = reporte_service.generar_pdf_socios(socios_data)
        
        fecha_str = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"reporte_socios_{fecha_str}.pdf"
        
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