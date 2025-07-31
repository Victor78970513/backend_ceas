from infrastructure.personal_repository import PersonalRepository
from schemas.personal import PersonalRequest, PersonalResponse, PersonalUpdateRequest
from fastapi import HTTPException
from typing import List

class PersonalUseCase:
    def __init__(self, personal_repository: PersonalRepository):
        self.personal_repository = personal_repository

    def list_personal(self) -> List[PersonalResponse]:
        personal = self.personal_repository.list_personal()
        return [PersonalResponse(**p.__dict__) for p in personal]

    def get_personal(self, personal_id: int) -> PersonalResponse:
        p = self.personal_repository.get_personal(personal_id)
        if not p:
            raise HTTPException(status_code=404, detail="Personal no encontrado")
        return PersonalResponse(**p.__dict__)

    def create_personal(self, data: PersonalRequest) -> PersonalResponse:
        p = self.personal_repository.create_personal(data)
        return PersonalResponse(**p.__dict__)

    def update_personal(self, personal_id: int, data: PersonalUpdateRequest) -> PersonalResponse:
        p = self.personal_repository.update_personal(personal_id, data)
        if not p:
            raise HTTPException(status_code=404, detail="Personal no encontrado")
        return PersonalResponse(**p.__dict__)

    def delete_personal(self, personal_id: int) -> dict:
        success = self.personal_repository.delete_personal(personal_id)
        if not success:
            raise HTTPException(status_code=404, detail="Personal no encontrado")
        return {"detail": "Personal eliminado correctamente"} 