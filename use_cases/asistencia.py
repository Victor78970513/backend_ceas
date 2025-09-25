from infrastructure.asistencia_repository import AsistenciaRepository
from schemas.asistencia import AsistenciaRequest, AsistenciaResponse, AsistenciaUpdateRequest
from fastapi import HTTPException
from typing import List

class AsistenciaUseCase:
    def __init__(self, asistencia_repository: AsistenciaRepository):
        self.asistencia_repository = asistencia_repository

    def list_asistencias(self) -> List[AsistenciaResponse]:
        asistencias = self.asistencia_repository.list_asistencias()
        return [self._transform_to_response(a) for a in asistencias]

    def get_asistencia_personal(self, id_personal: int) -> List[AsistenciaResponse]:
        asistencias = self.asistencia_repository.get_asistencia_personal(id_personal)
        return [self._transform_to_response(a) for a in asistencias]

    def create_asistencia(self, data: AsistenciaRequest) -> AsistenciaResponse:
        a = self.asistencia_repository.create_asistencia(data)
        return self._transform_to_response(a)

    def update_asistencia(self, asistencia_id: int, data: AsistenciaUpdateRequest) -> AsistenciaResponse:
        a = self.asistencia_repository.update_asistencia(asistencia_id, data)
        if not a:
            raise HTTPException(status_code=404, detail="Asistencia no encontrada")
        return self._transform_to_response(a)
    
    def _transform_to_response(self, asistencia) -> AsistenciaResponse:
        """Transforma los datos de asistencia al formato requerido"""
        # Obtener el nombre del empleado
        nombre_empleado = getattr(asistencia, 'nombre_empleado', f'Empleado {asistencia.id_personal}')
        
        # Formatear fecha
        fecha_str = str(asistencia.fecha) if asistencia.fecha else None
        
        # Formatear horas
        hora_entrada = str(asistencia.hora_ingreso) if asistencia.hora_ingreso else None
        hora_salida = str(asistencia.hora_salida) if asistencia.hora_salida else None
        
        # Determinar estado basado en las horas
        estado = asistencia.estado or "presente"
        if not asistencia.hora_ingreso and not asistencia.hora_salida:
            estado = "ausente"
        elif asistencia.hora_ingreso:
            # Convertir string a time para comparar
            try:
                if isinstance(asistencia.hora_ingreso, str):
                    from datetime import time
                    hora_parts = asistencia.hora_ingreso.split(':')
                    hora_obj = time(int(hora_parts[0]), int(hora_parts[1]))
                else:
                    hora_obj = asistencia.hora_ingreso
                
                # Si tiene hora de entrada, verificar si es tardanza (después de las 9:00)
                if hora_obj.hour > 9 or (hora_obj.hour == 9 and hora_obj.minute > 0):
                    estado = "tardanza"
                else:
                    estado = "presente"
            except:
                # Si hay error en la conversión, usar el estado original
                pass
        
        return AsistenciaResponse(
            id_asistencia=asistencia.id_asistencia,
            id_empleado=asistencia.id_personal,
            nombre_empleado=nombre_empleado,
            fecha=fecha_str,
            estado=estado,
            hora_entrada=hora_entrada,
            hora_salida=hora_salida,
            observaciones=asistencia.observaciones
        ) 