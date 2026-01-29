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
            # Crear Usuario Admin desde cero
            admin_user = User(
                email=gina_email,
                name="Gina Martinez",
                password_hash=get_password_hash("Shadys2024*"),
                role="worker",
                phone="3000000000",
                is_active=True
            )
            db.add(admin_user)
            db.commit()
            db.refresh(admin_user)
            print(f"✅ Administradora {gina_email} creada desde cero.")
        else:
            # Si ya existe (ej. entró por Google), asegurar que sea 'worker'
            if existing_user.role != "worker":
                existing_user.role = "worker"
                db.commit()
                print(f"⬆️ Usuario {gina_email} promovido a Administradora.")
            admin_user = existing_user

        # 2. Asegurar que esté en la tabla de Workers
        existing_worker = db.query(Worker).filter(Worker.user_id == admin_user.id).first()
        if not existing_worker:
            new_worker = Worker(
                user_id=admin_user.id,
                name=admin_user.name,
                specialty="Manicura y Pedicura Premium",
                bio="Especialista en belleza de uñas con años de experiencia.",
                is_active=True
            )
            db.add(new_worker)
            db.commit()
            print(f"👷 Entidad Worker creada para {gina_email}.")
        else:
            print(f"✅ Gina ya está configurada como Worker.")
            
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    init_production_data()
