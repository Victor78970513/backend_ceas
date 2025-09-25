from infrastructure.personal_repository import PersonalRepository
from schemas.personal import PersonalRequest, PersonalResponse, PersonalUpdateRequest
from fastapi import HTTPException
from typing import List

class PersonalUseCase:
    def __init__(self, personal_repository: PersonalRepository):
        self.personal_repository = personal_repository

    def list_personal(self) -> List[PersonalResponse]:
        personal = self.personal_repository.list_personal()
        return [self._transform_to_response(p) for p in personal]

    def get_personal(self, personal_id: int) -> PersonalResponse:
        p = self.personal_repository.get_personal(personal_id)
        if not p:
            raise HTTPException(status_code=404, detail="Personal no encontrado")
        return self._transform_to_response(p)

    def create_personal(self, data: PersonalRequest) -> PersonalResponse:
        p = self.personal_repository.create_personal(data)
        return self._transform_to_response(p)

    def update_personal(self, personal_id: int, data: PersonalUpdateRequest) -> PersonalResponse:
        p = self.personal_repository.update_personal(personal_id, data)
        if not p:
            raise HTTPException(status_code=404, detail="Personal no encontrado")
        return self._transform_to_response(p)

    def delete_personal(self, personal_id: int) -> dict:
        success = self.personal_repository.delete_personal(personal_id)
        if not success:
            raise HTTPException(status_code=404, detail="Personal no encontrado")
        return {"detail": "Personal eliminado correctamente"}
    
    def _transform_to_response(self, personal) -> PersonalResponse:
        """Transforma los datos del personal al formato requerido"""
        # Obtener el nombre del cargo
        nombre_cargo = getattr(personal, 'nombre_cargo', f'Cargo {personal.cargo}')
        
        # Combinar nombres y apellidos
        nombre_completo = f"{personal.nombres} {personal.apellidos}"
        
        # Convertir estado booleano a string
        estado_str = "ACTIVO" if personal.estado else "INACTIVO"
        
        return PersonalResponse(
            id_empleado=personal.id_personal,
            nombre_completo=nombre_completo,
            cargo=nombre_cargo,
            departamento=personal.departamento or "Sin departamento",
            estado=estado_str,
            email=personal.correo,
            telefono=None,  # No tenemos teléfono en la BD actual
            fecha_contratacion=personal.fecha_ingreso,
            salario=personal.salario,
            foto=None  # No tenemos foto en la BD actual
        ) 