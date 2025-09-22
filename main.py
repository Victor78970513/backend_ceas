from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import login
from routers import usuarios
from routers import socios
from routers import acciones
from routers import pagos
from routers import personal
from routers import asistencia
from routers import finanzas
from routers import bi
from routers import bi_personal
from routers import bi_administrativo
from routers import bi_avanzado
from routers import eventos
from routers import reservas
from routers import inventario
from routers import proveedores
from routers import compras
from routers import facturacion
from routers import logs
from routers import catalogos
from routers import socio_profile

app = FastAPI(
    title="CEAS ERP API",
    description="API para el sistema ERP del Club de Emprendedores y Accionistas",
    version="1.0.0"
)

# Configuración de CORS - Para desarrollo, permitir cualquier origen local
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En desarrollo, permitir cualquier origen
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH", "HEAD"],
    allow_headers=[
        "Accept",
        "Accept-Language",
        "Content-Language",
        "Content-Type",
        "Authorization",
        "X-Requested-With",
        "Origin",
        "Access-Control-Request-Method",
        "Access-Control-Request-Headers",
        "Access-Control-Allow-Origin",
        "Access-Control-Allow-Headers",
        "Access-Control-Allow-Methods",
    ],
)

app.include_router(login.router)
app.include_router(usuarios.router)
app.include_router(socios.router)
app.include_router(acciones.router)
app.include_router(pagos.router)
app.include_router(personal.router)
app.include_router(asistencia.router)
app.include_router(finanzas.router)
app.include_router(bi.router)
app.include_router(bi_personal.router)
app.include_router(bi_administrativo.router)
app.include_router(bi_avanzado.router)
app.include_router(eventos.router)
app.include_router(reservas.router)
app.include_router(inventario.router)
app.include_router(proveedores.router)
app.include_router(compras.router)
app.include_router(facturacion.router)
app.include_router(logs.router)
app.include_router(catalogos.router)
app.include_router(socio_profile.router)

# Aquí se incluirán los routers de la arquitectura limpia 