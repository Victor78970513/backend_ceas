from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from config import SECRET_KEY, ALGORITHM
import jwt
from sqlalchemy import text
from config import SessionLocal

router = APIRouter(prefix="/catalogos", tags=["catalogos"])

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")

def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Token inválido o expirado")

def fetch_catalog(query):
    db = SessionLocal()
    try:
        result = db.execute(text(query)).fetchall()
        return [dict(row) for row in result]
    finally:
        db.close()

@router.get("/estados-pago")
def get_estados_pago(current_user=Depends(get_current_user)):
    return fetch_catalog("SELECT id_estado_pago, descripcion FROM estado_pago")

@router.get("/modalidades-pago")
def get_modalidades_pago(current_user=Depends(get_current_user)):
    return fetch_catalog("SELECT id_modalidad_pago, descripcion, meses_de_gracia, porcentaje_renovacion_inicial, porcentaje_renovacion_mensual, costo_renovacion_estandar FROM modalidadpago")

@router.get("/estados-accion")
def get_estados_accion(current_user=Depends(get_current_user)):
    return fetch_catalog("SELECT id_estado_accion, nombre_estado_accion FROM estado_accion")

@router.get("/roles")
def get_roles(current_user=Depends(get_current_user)):
    return fetch_catalog("SELECT id_rol, nombre_rol FROM roles")

@router.get("/cargos")
def get_cargos(current_user=Depends(get_current_user)):
    return fetch_catalog("SELECT id_cargo, nombre_cargo FROM cargos")

@router.get("/clubes")
def get_clubes(current_user=Depends(get_current_user)):
    return fetch_catalog("SELECT id_club, nombre_club FROM club") 