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
        
        # 1. Asegurar que el usuario existe y es 'worker'
        gina_email = "ginap.mb.martinez@gmail.com"
        user = db.query(User).filter(User.email == gina_email).first()
        
        if not user:
            print(f"➕ Creando nuevo usuario para {gina_email}")
            user = User(
                email=gina_email,
                name="Gina Martinez",
                password_hash=get_password_hash("Shadys2024*"),
                role="worker",
                is_active=True
            )
            db.add(user)
            db.commit()
            db.refresh(user)
        else:
            print(f"🔄 Actualizando usuario existente {gina_email} a rol worker")
            user.role = "worker"
            user.is_active = True
            db.commit()

        # 2. Asegurar que tiene un perfil en la tabla de Workers
        worker = db.query(Worker).filter(Worker.user_id == user.id).first()
        if not worker:
            print(f"👷 Creando perfil de Worker para {user.name}")
            worker = Worker(
                user_id=user.id,
                name=user.name,
                specialty="Manicura y Pedicura Premium",
                bio="Especialista en belleza de uñas con años de experiencia.",
                is_active=True
            )
            db.add(worker)
        else:
            print(f"✅ Perfil de Worker existente. Asegurando estado activo.")
            worker.is_active = True
            worker.name = user.name # Sincronizar nombre
            
        db.commit()
        print(f"✨ ¡PRODUCCIÓN REPARADA! {gina_email} ahora es Administradora oficial.")
            
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    init_production_data()
