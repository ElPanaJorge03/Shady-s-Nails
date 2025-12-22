from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os
from sqlalchemy import text

from app.database import engine, Base

# 🔹 IMPORTANTE: importar CLASES, no archivos
from app.models.customer import Customer
print("🧪 Customer cargado:", Customer)

from app.models.worker import Worker
from app.models.service import Service
from app.models.additional import Additional
from app.models.appointment import Appointment



from app.routers.appointment import router as appointment_router
from app.routers.availability import router as availability_router
from app.routers.service import router as service_router
from app.routers.worker import router as worker_router
from app.routers.customer import router as customer_router
from app.routers.additional import router as additional_router
from app.routers.auth import router as auth_router





# ─────────────────────────────────────────────
# Verificar conexión real a la base de datos
# ─────────────────────────────────────────────
with engine.connect() as conn:
    result = conn.execute(text("SELECT current_database(), current_schema();"))
    for row in result:
        print("📌 BASE REAL:", row)


# ─────────────────────────────────────────────
# Crear aplicación FastAPI
# ─────────────────────────────────────────────
app = FastAPI(
    title="Shadys Nails API",
    version="0.1.0"
)

# Configurar CORS para permitir peticiones desde Angular
cors_origins_str = os.getenv("CORS_ORIGINS", "http://localhost:4200,http://127.0.0.1:4200")
cors_origins = [origin.strip() for origin in cors_origins_str.split(",")]

print("=" * 60)
print("🔒 CORS CONFIGURATION")
print("=" * 60)
print(f"CORS_ORIGINS env var: {cors_origins_str}")
print(f"Parsed origins: {cors_origins}")
print("=" * 60)

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
    allow_headers=["*"],
    expose_headers=["*"],
    max_age=3600,  # Cache preflight requests for 1 hour
)

# Registrar routers
app.include_router(auth_router)  # Auth debe ir primero
app.include_router(appointment_router)
app.include_router(availability_router)
app.include_router(service_router)
app.include_router(worker_router)
app.include_router(customer_router)
app.include_router(additional_router)
# ─────────────────────────────────────────────
# Crear tablas en PostgreSQL
# ─────────────────────────────────────────────
print("📦 Tablas registradas en metadata:", Base.metadata.tables.keys())

Base.metadata.create_all(bind=engine)

print("🛠️ create_all ejecutado correctamente")


# ─────────────────────────────────────────────
# Endpoint raíz
# ─────────────────────────────────────────────
@app.get("/")
def root():
    return {
        "msg": "Shadys Nails API funcionando correctamente 💅"
    }
