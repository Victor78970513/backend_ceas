from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from schemas.personal import PersonalRequest, PersonalResponse, PersonalUpdateRequest
from use_cases.personal import PersonalUseCase
from infrastructure.personal_repository import PersonalRepository
from use_cases.asistencia import AsistenciaUseCase
from infrastructure.asistencia_repository import AsistenciaRepository
from infrastructure.reporte_rrhh_service import ReporteRRHHService
from fastapi.security import OAuth2PasswordBearer
from typing import List
import jwt
from config import SECRET_KEY, ALGORITHM
from datetime import datetime
from io import BytesIO

router = APIRouter(prefix="/personal", tags=["personal"])

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")

def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Token inválido o expirado")

@router.get("/", response_model=List[PersonalResponse])
def list_personal(current_user=Depends(get_current_user)):
    use_case = PersonalUseCase(PersonalRepository())
    return use_case.list_personal()

@router.post("/", response_model=PersonalResponse)
def create_personal(request: PersonalRequest, current_user=Depends(get_current_user)):
    use_case = PersonalUseCase(PersonalRepository())
    return use_case.create_personal(request)

@router.get("/{personal_id}", response_model=PersonalResponse)
def get_personal(personal_id: int, current_user=Depends(get_current_user)):
    use_case = PersonalUseCase(PersonalRepository())
    return use_case.get_personal(personal_id)

@router.put("/{personal_id}", response_model=PersonalResponse)
def update_personal(personal_id: int, request: PersonalUpdateRequest, current_user=Depends(get_current_user)):
    use_case = PersonalUseCase(PersonalRepository())
    return use_case.update_personal(personal_id, request)

@router.delete("/{personal_id}")
def delete_personal(personal_id: int, current_user=Depends(get_current_user)):
    use_case = PersonalUseCase(PersonalRepository())
    return use_case.delete_personal(personal_id)

@router.get("/reporte/descargar")
def descargar_reporte_rrhh(current_user=Depends(get_current_user)):
    """
    Genera y descarga un reporte de recursos humanos en formato PDF con gráficas profesionales
    """
    try:
        # Obtener todo el personal
        personal_use_case = PersonalUseCase(PersonalRepository())
        personal_list = personal_use_case.list_personal()
        
        # Obtener todas las asistencias
        asistencia_use_case = AsistenciaUseCase(AsistenciaRepository())
        asistencias = asistencia_use_case.list_asistencias()
        
        # Preparar datos para el reporte
        personal_data = []
        for empleado in personal_list:
            personal_data.append({
                'id_empleado': empleado.id_empleado,
                'nombre_completo': empleado.nombre_completo,
                'cargo': empleado.cargo,
                'departamento': empleado.departamento,
                'estado': empleado.estado,
                'salario': float(empleado.salario)
            })
        
        asistencia_data = []
        for asistencia in asistencias:
            asistencia_data.append({
                'id_asistencia': asistencia.id_asistencia,
                'nombre_empleado': asistencia.nombre_empleado,
                'fecha': asistencia.fecha,
                'estado': asistencia.estado,
                'hora_entrada': asistencia.hora_entrada,
                'hora_salida': asistencia.hora_salida
            })
        
        # Generar PDF con gráficas
        reporte_service = ReporteRRHHService()
        pdf_data = reporte_service.generar_pdf_rrhh(personal_data, asistencia_data)
        
        fecha_str = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"reporte_rrhh_{fecha_str}.pdf"
        
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
        logging.error(f"Error al generar reporte de RR.HH.: {str(e)}")
        logging.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Error al generar reporte: {str(e)}") 