"""
Script para limpiar y reorganizar la base de datos
"""
import os
import sys
from sqlalchemy.orm import Session
from dotenv import load_dotenv

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.database import SessionLocal
from app.models.worker import Worker
from app.models.service import Service
from app.models.additional import Additional

load_dotenv()

def clean_and_reorganize():
    """Limpia duplicados y reorganiza los datos"""
    db = SessionLocal()
    
    try:
        print("🧹 Limpiando base de datos...\n")
        
        # 1️⃣ Eliminar todos los servicios (están duplicados)
        print("🗑️  Eliminando servicios duplicados...")
        deleted_services = db.query(Service).delete()
        db.commit()
        print(f"  ✅ Eliminados {deleted_services} servicios\n")
        
        # 2️⃣ Verificar workers existentes
        print("👥 Workers existentes:")
        workers = db.query(Worker).all()
        for w in workers:
            print(f"  • ID {w.id}: {w.name}")
        print()
        
        # 3️⃣ Crear servicios solo para el primer worker (para evitar duplicados en el frontend)
        if workers:
            first_worker = workers[0]
            print(f"💅 Creando servicios para: {first_worker.name}")
            
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
            
            for service_data in services_data:
                service = Service(
                    worker_id=first_worker.id,
                    **service_data,
                    state=True
                )
                db.add(service)
                print(f"  ✅ {service_data['name']}")
            
            db.commit()
        
        print("\n" + "="*60)
        print("✅ ¡Base de datos reorganizada!")
        print("="*60)
        
        # Mostrar resumen
        total_workers = db.query(Worker).count()
        total_services = db.query(Service).count()
        total_additionals = db.query(Additional).count()
        
        print(f"\n📊 Resumen:")
        print(f"  • Manicuristas: {total_workers}")
        print(f"  • Servicios: {total_services}")
        print(f"  • Adicionales: {total_additionals}")
        
        print(f"\n💡 Nota: Los servicios ahora aparecen una sola vez")
        print(f"   Todos los workers pueden ofrecer los mismos servicios")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    clean_and_reorganize()
