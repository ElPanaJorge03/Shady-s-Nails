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
        
        # 1. Asegurar que Gina exista como Worker (Administradora)
        gina_email = "ginap.mb.martinez@gmail.com"
        worker = db.query(Worker).filter(Worker.email == gina_email).first()
        
        if not worker:
            print(f"👷 Creando perfil de Worker para {gina_email}")
            worker = Worker(
                name="Gina Martinez",
                email=gina_email,
                phone="3000000000",
                password_hash=get_password_hash("Shadys2024*"),
                role="worker",
                state=True
            )
            db.add(worker)
            db.commit()
            print(f"✅ Gina creada como Worker oficial.")
        else:
            print(f"🔄 Sincronizando perfil de Gina...")
            worker.role = "worker"
            worker.state = True
            # Si quieres que la clave de producción sea la misma siempre:
            # worker.password_hash = get_password_hash("Shadys2024*")
            db.commit()

        # 2. También asegurar que exista en la tabla de Usuarios (para el login de Google)
        user = db.query(User).filter(User.email == gina_email).first()
        if not user:
            print(f"➕ Creando usuario general para Google Auth...")
            user = User(
                email=gina_email,
                name="Gina Martinez",
                password_hash=get_password_hash("Shadys2024*"),
                role="worker",
                is_active=True
            )
            db.add(user)
        else:
            user.role = "worker"
            user.is_active = True
            
        db.commit()
        print(f"✨ ¡PRODUCCIÓN REPARADA! {gina_email} ahora tiene perfiles vinculados.")
            
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    init_production_data()
