from infrastructure.user_repository import UserRepository
from schemas.user import UserResponse, UserUpdateRequest, UserDeleteResponse
from fastapi import HTTPException
from typing import List

class UserUseCase:
    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository

    def list_users(self) -> List[UserResponse]:
        users = self.user_repository.list_users()
        return [UserResponse(**user.__dict__) for user in users]

    def get_user(self, user_id: int) -> UserResponse:
        user = self.user_repository.get_user(user_id)
        if not user:
            raise HTTPException(status_code=404, detail="Usuario no encontrado")
        return UserResponse(**user.__dict__)

    def update_user(self, user_id: int, data: UserUpdateRequest) -> UserResponse:
        user = self.user_repository.update_user(user_id, data)
        if not user:
            raise HTTPException(status_code=404, detail="Usuario no encontrado")
        return UserResponse(**user.__dict__)

    def delete_user(self, user_id: int) -> UserDeleteResponse:
        success = self.user_repository.delete_user(user_id)
        if not success:
            raise HTTPException(status_code=404, detail="Usuario no encontrado")
        return UserDeleteResponse(detail="Usuario eliminado correctamente") 