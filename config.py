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

# Configuración de PayPal (MÁS FÁCIL)
PAYPAL_CLIENT_ID = "TU_CLIENT_ID_REAL_AQUI"  # Cambiar por tu client ID real
PAYPAL_CLIENT_SECRET = "TU_CLIENT_SECRET_REAL_AQUI"  # Cambiar por tu client secret real
PAYPAL_MODE = "sandbox"  # Para pruebas, cambiar a "live" para producción

# Configuración de MercadoPago (Alternativa)
MERCADOPAGO_ACCESS_TOKEN = "TEST-TU_ACCESS_TOKEN_AQUI"  # Cambiar por tu token real
MERCADOPAGO_PUBLIC_KEY = "TEST-TU_PUBLIC_KEY_AQUI"  # Cambiar por tu public key real

# Configuración de Stripe (Alternativa)
STRIPE_SECRET_KEY = "sk_test_51234567890abcdefghijklmnopqrstuvwxyz"  # Cambiar por tu clave real
STRIPE_PUBLISHABLE_KEY = "pk_test_51234567890abcdefghijklmnopqrstuvwxyz"  # Cambiar por tu clave real
STRIPE_WEBHOOK_SECRET = "whsec_1234567890abcdefghijklmnopqrstuvwxyz"  # Cambiar por tu webhook secret
