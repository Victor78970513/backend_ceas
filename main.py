from fastapi import FastAPI
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

app = FastAPI()

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

# Aquí se incluirán los routers de la arquitectura limpia 