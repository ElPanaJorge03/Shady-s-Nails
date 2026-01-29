"""
Script para verificar y crear/actualizar el usuario worker de Gina
"""
import sys
import os

# Agregar el directorio raíz al path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models.user import User
from app.models.worker import Worker
from app.utils.security import get_password_hash

def verify_and_create_gina():
    """Verifica y crea/actualiza el usuario worker para Gina"""
    db: Session = SessionLocal()
    
    try:
        print("\n" + "="*60)
        print("🔍 VERIFICANDO USUARIO WORKER DE GINA")
        print("="*60 + "\n")
        
        # Datos de Gina
        email = "gina@shadysnails.com"
        password = "Gina2024"  # Contraseña temporal
        name = "Gina Paola Martinez Barrera"
        phone = "3001234567"
        
        # 1. Verificar si existe el worker en la tabla Worker
        print("📋 Paso 1: Verificando tabla Worker...")
        worker = db.query(Worker).filter(Worker.name == name).first()
        
        if worker:
            print(f"✅ Worker encontrado en la base de datos:")
            print(f"   ID: {worker.id}")
            print(f"   Nombre: {worker.name}")
            print(f"   Email: {worker.email}")
            print(f"   Teléfono: {worker.phone}")
            print(f"   Negocio: {worker.business_name}")
            worker_id = worker.id
        else:
            print(f"⚠️  No se encontró worker con nombre '{name}'")
            worker_id = None
        
        # 2. Verificar si existe el usuario en la tabla User
        print(f"\n📋 Paso 2: Verificando tabla User...")
        user = db.query(User).filter(User.email == email).first()
        
        if user:
            print(f"✅ Usuario encontrado:")
            print(f"   ID: {user.id}")
            print(f"   Email: {user.email}")
            print(f"   Nombre: {user.name}")
            print(f"   Rol: {user.role}")
            print(f"   Tiene password_hash: {'✅ Sí' if user.password_hash else '❌ No'}")
            
            # Si no tiene password, agregarlo
            if not user.password_hash:
                print(f"\n🔧 Agregando contraseña al usuario...")
                user.password_hash = get_password_hash(password)
                db.commit()
                print(f"✅ Contraseña agregada")
            
        else:
            print(f"⚠️  No se encontró usuario con email '{email}'")
            
            # Si existe worker pero no user, crear el user
            if worker_id:
                print(f"\n🔧 Creando usuario para el worker existente...")
                new_user = User(
                    id=worker_id,  # Usar el mismo ID del worker
                    email=email,
                    password_hash=get_password_hash(password),
                    name=name,
                    phone=phone,
                    role="worker",
                    is_active=True
                )
                db.add(new_user)
                db.commit()
                db.refresh(new_user)
                user = new_user
                print(f"✅ Usuario creado con ID {new_user.id}")
            else:
                # No existe ni worker ni user, crear ambos
                print(f"\n🔧 Creando usuario y worker desde cero...")
                
                # Crear usuario primero
                new_user = User(
                    email=email,
                    password_hash=get_password_hash(password),
                    name=name,
                    phone=phone,
                    role="worker",
                    is_active=True
                )
                db.add(new_user)
                db.commit()
                db.refresh(new_user)
                user = new_user
                print(f"✅ Usuario creado con ID {new_user.id}")
                
                # Crear worker con el mismo ID
                new_worker = Worker(
                    id=new_user.id,
                    name=name,
                    phone=phone,
                    email=email,
                    business_name="Shady's Nails",
                    state=True
                )
                db.add(new_worker)
                db.commit()
                db.refresh(new_worker)
                worker = new_worker
                print(f"✅ Worker creado con ID {new_worker.id}")
        
        # 3. Resumen final
        print("\n" + "="*60)
        print("🎉 VERIFICACIÓN COMPLETADA")
        print("="*60)
        print(f"\n📋 CREDENCIALES PARA INICIAR SESIÓN:")
        print(f"   Email:      {email}")
        print(f"   Contraseña: {password}")
        print(f"\n🔗 URLs:")
        print(f"   Frontend:   http://localhost:4200")
        print(f"   Login:      http://localhost:4200/login")
        print(f"   Dashboard:  http://localhost:4200/worker-dashboard")
        print(f"\n⚠️  IMPORTANTE: Cambia esta contraseña después del primer inicio de sesión")
        print("="*60 + "\n")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        db.rollback()
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    verify_and_create_gina()
