from fastapi import APIRouter, Depends, HTTPException
from schemas.personal import PersonalRequest, PersonalResponse, PersonalUpdateRequest
from use_cases.personal import PersonalUseCase
from infrastructure.personal_repository import PersonalRepository
from fastapi.security import OAuth2PasswordBearer
from typing import List
import jwt
from config import SECRET_KEY, ALGORITHM

router = APIRouter(prefix="/personal", tags=["personal"])

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

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