from fastapi import APIRouter, Depends
from schemas.user import UserLoginRequest, UserLoginResponse, UserRegisterRequest
from use_cases.login import LoginUseCase
from use_cases.register import RegisterUseCase
from infrastructure.user_repository import UserRepository

router = APIRouter()

@router.post("/login", response_model=UserLoginResponse)
def login(request: UserLoginRequest):
    use_case = LoginUseCase(UserRepository())
    return use_case.login(request)

@router.post("/register", response_model=UserLoginResponse)
def register(request: UserRegisterRequest):
    use_case = RegisterUseCase(UserRepository())
    return use_case.register(request) 