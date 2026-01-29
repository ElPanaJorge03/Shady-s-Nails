"""
Script para poblar la base de datos con datos iniciales de prueba
"""
import os
import sys
from sqlalchemy.orm import Session
from dotenv import load_dotenv

# Agregar el directorio raíz al path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.database import SessionLocal
from app.models.worker import Worker
from app.models.service import Service
from app.models.additional import Additional
from app.utils.security import get_password_hash

load_dotenv()

def create_initial_data():
    """Crea datos iniciales para testing"""
    db = SessionLocal()
    
    try:
        print("🚀 Iniciando población de base de datos...\n")
        
        # 1️⃣ Crear Workers (Manicuristas)
        print("👩‍💼 Creando manicuristas...")
        workers_data = [
            {
                "name": "María González",
                "phone": "3001234567",
                "email": "maria@shadysnails.com",
                "business_name": "Shady's Nails",
                "state": True
            },
            {
                "name": "Laura Martínez",
                "phone": "3009876543",
                "email": "laura@shadysnails.com",
                "business_name": "Shady's Nails",
                "state": True
            },
            {
                "name": "Carolina Rodríguez",
                "phone": "3005551234",
                "email": "carolina@shadysnails.com",
                "business_name": "Shady's Nails",
                "state": True
            }
        ]
        
        workers = []
        for worker_data in workers_data:
            # Verificar si ya existe
            existing = db.query(Worker).filter(Worker.email == worker_data["email"]).first()
            if not existing:
                worker = Worker(**worker_data)
                db.add(worker)
                workers.append(worker)
                print(f"  ✅ {worker_data['name']}")
            else:
                workers.append(existing)
                print(f"  ⏭️  {worker_data['name']} (ya existe)")
        
        db.commit()
        
        # 2️⃣ Crear Services
        print("\n💅 Creando servicios...")
        services_data = [
            {"name": "Manicure Básico", "duration_minutes": 30, "price": 25000},
            {"name": "Manicure Spa", "duration_minutes": 45, "price": 35000},
            {"name": "Manicure Permanente", "duration_minutes": 60, "price": 45000},
            {"name": "Pedicure Básico", "duration_minutes": 40, "price": 30000},
            {"name": "Pedicure Spa", "duration_minutes": 60, "price": 40000},
            {"name": "Uñas Acrílicas", "duration_minutes": 90, "price": 60000},
            {"name": "Uñas en Gel", "duration_minutes": 75, "price": 55000},
            {"name": "Diseño de Uñas", "duration_minutes": 45, "price": 35000},
        ]
        
        for worker in workers:
            for service_data in services_data:
                # Verificar si ya existe
                existing = db.query(Service).filter(
                    Service.worker_id == worker.id,
                    Service.name == service_data["name"]
                ).first()
                
                if not existing:
                    service = Service(
                        worker_id=worker.id,
                        **service_data,
                        state=True
                    )
                    db.add(service)
                    print(f"  ✅ {service_data['name']} - {worker.name}")
                else:
                    print(f"  ⏭️  {service_data['name']} - {worker.name} (ya existe)")
        
        db.commit()
        
        # 3️⃣ Crear Additionals (Servicios adicionales)
        print("\n✨ Creando servicios adicionales...")
        additionals_data = [
            {"name": "Decoración con Cristales", "extra_duration": 15, "price": 10000},
            {"name": "Nail Art Premium", "extra_duration": 20, "price": 15000},
            {"name": "Francés Clásico", "extra_duration": 10, "price": 8000},
            {"name": "Ombre/Degradado", "extra_duration": 15, "price": 12000},
            {"name": "Extensión de Uñas", "extra_duration": 30, "price": 20000},
        ]
        
        for additional_data in additionals_data:
            # Verificar si ya existe
            existing = db.query(Additional).filter(
                Additional.name == additional_data["name"]
            ).first()
            
            if not existing:
                additional = Additional(**additional_data, state=True)
                db.add(additional)
                print(f"  ✅ {additional_data['name']}")
            else:
                print(f"  ⏭️  {additional_data['name']} (ya existe)")
        
        db.commit()
        
        print("\n" + "="*60)
        print("✅ ¡Base de datos poblada exitosamente!")
        print("="*60)
        
        # Mostrar resumen
        total_workers = db.query(Worker).count()
        total_services = db.query(Service).count()
        total_additionals = db.query(Additional).count()
        
        print(f"\n📊 Resumen:")
        print(f"  • Manicuristas: {total_workers}")
        print(f"  • Servicios: {total_services}")
        print(f"  • Adicionales: {total_additionals}")
        
        print(f"\n🎯 Próximos pasos:")
        print(f"  1. Abre http://localhost:4200")
        print(f"  2. Regístrate con tu email y contraseña")
        print(f"  3. ¡Empieza a agendar citas!")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    create_initial_data()
