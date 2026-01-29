import sys
import os

# Añadir el directorio actual al path para importar la app
sys.path.append(os.getcwd())

from sqlalchemy.orm import Session
from app.database import SessionLocal, engine
from app.models.user import User
from app.models.worker import Worker
from app.utils.security import get_password_hash

def init_production_data():
    db = SessionLocal()
    try:
        print("🚀 Iniciando creación de administradora en producción...")
        
        # 1. Verificar si Gina ya existe
        gina_email = "ginap.mb.martinez@gmail.com"
        existing_user = db.query(User).filter(User.email == gina_email).first()
        
        if not existing_user:
            # Crear Usuario Admin
            admin_user = User(
                email=gina_email,
                name="Gina Martinez",
                password_hash=get_password_hash("Shadys2024*"), # Contraseña temporal
                role="worker",
                phone="3000000000",
                is_active=True
            )
            db.add(admin_user)
            db.commit()
            db.refresh(admin_user)
            
            # Crear entrada en la tabla de Workers
            new_worker = Worker(
                user_id=admin_user.id,
                name=admin_user.name,
                specialty="Manicura y Pedicura Premium",
                bio="Especialista en belleza de uñas con años de experiencia.",
                is_active=True
            )
            db.add(new_worker)
            db.commit()
            print(f"✅ Administradora {gina_email} creada con éxito.")
        else:
            print(f"ℹ️ La administradora {gina_email} ya existe.")
            
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    init_production_data()
