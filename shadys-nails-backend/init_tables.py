import os
import sys
from dotenv import load_dotenv

# Asegurar que estamos cargando el entorno correcto
load_dotenv()

# Importar modelos y base
from app.database import engine, Base

# Importar TODOS los modelos para que SQLAlchemy los registre
from app.models.user import User
from app.models.worker import Worker
from app.models.customer import Customer
from app.models.service import Service, Additional
from app.models.appointment import Appointment

print(f"Conectando a la base de datos: {os.getenv('DATABASE_URL').split('@')[-1]}")
print("Creando tablas en Neon...")

try:
    Base.metadata.create_all(bind=engine)
    print("✅ Tablas creadas exitosamente en Neon!")
except Exception as e:
    print(f"❌ Error al crear tablas: {e}")
