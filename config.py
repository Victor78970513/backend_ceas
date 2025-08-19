from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

DATABASE_URL = "postgresql://wiscocho:admin@localhost:5432/ceas_bd"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_bd():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Variables globales para JWT y otros settings
SECRET_KEY = "double_dog123"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 1440  # 1 día (24 horas * 60 minutos)
