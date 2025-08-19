from fastapi import APIRouter, Depends, HTTPException
from schemas.user import UserResponse, UserRegisterRequest, UserUpdateRequest, UserDeleteResponse
from use_cases.user import UserUseCase
from infrastructure.user_repository import UserRepository
from fastapi.security import OAuth2PasswordBearer
from typing import List
import jwt
from config import SECRET_KEY, ALGORITHM

router = APIRouter(prefix="/usuarios", tags=["usuarios"])

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")

def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Token inválido o expirado")

@router.get("/", response_model=List[UserResponse])
def list_users(current_user=Depends(get_current_user)):
    use_case = UserUseCase(UserRepository())
    return use_case.list_users()

@router.post("/", response_model=UserResponse)
def register_user(request: UserRegisterRequest, current_user=Depends(get_current_user)):
    # Reutiliza el caso de uso de registro
    from use_cases.register import RegisterUseCase
    use_case = RegisterUseCase(UserRepository())
    return use_case.register(request)

@router.get("/{user_id}", response_model=UserResponse)
def get_user(user_id: int, current_user=Depends(get_current_user)):
    use_case = UserUseCase(UserRepository())
    return use_case.get_user(user_id)

@router.put("/{user_id}", response_model=UserResponse)
def update_user(user_id: int, request: UserUpdateRequest, current_user=Depends(get_current_user)):
    use_case = UserUseCase(UserRepository())
    return use_case.update_user(user_id, request)

@router.delete("/{user_id}", response_model=UserDeleteResponse)
def delete_user(user_id: int, current_user=Depends(get_current_user)):
    use_case = UserUseCase(UserRepository())
    return use_case.delete_user(user_id) 