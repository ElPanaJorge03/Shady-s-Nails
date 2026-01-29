"""
Script para actualizar la base de datos con los servicios REALES de Shady's Nails
- Elimina todos los workers y servicios actuales
- Crea solo a Gina Paola Martinez Barrera como worker
- Agrega los servicios reales con precios y duraciones correctas
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

def update_to_real_data():
    """Actualiza la base de datos con datos reales"""
    db = SessionLocal()
    
    try:
        print("🔄 Actualizando base de datos con información REAL...\n")
        
        # 1️⃣ LIMPIAR TODO (en orden correcto para evitar errores de FK)
        print("🗑️  Eliminando datos de prueba...")
        
        # Primero eliminar appointments (tienen FK a services)
        from app.models.appointment import Appointment
        deleted_appointments = db.query(Appointment).delete()
        print(f"  ✅ Eliminadas {deleted_appointments} citas")
        
        # Luego services y workers
        deleted_services = db.query(Service).delete()
        print(f"  ✅ Eliminados {deleted_services} servicios")
        
        deleted_workers = db.query(Worker).delete()
        print(f"  ✅ Eliminados {deleted_workers} workers")
        
        # Finalmente additionals
        deleted_additionals = db.query(Additional).delete()
        print(f"  ✅ Eliminados {deleted_additionals} adicionales")
        
        db.commit()
        print("  ✅ Base de datos limpia\n")
        
        # 2️⃣ CREAR WORKER REAL
        print("👩‍💼 Creando manicurista real...")
        gina = Worker(
            name="Gina Paola Martinez Barrera",
            phone="3001234567",  # Actualiza con el número real si lo tienes
            email="gina@shadysnails.com",
            business_name="Shady's Nails",
            state=True
        )
        db.add(gina)
        db.commit()
        db.refresh(gina)
        print(f"  ✅ {gina.name} (ID: {gina.id})\n")
        
        # 3️⃣ CREAR SERVICIOS REALES
        print("💅 Creando servicios reales...")
        
        # Nota: Para duraciones variables, uso el tiempo promedio/máximo
        # para asegurar que no haya problemas de agenda
        servicios_reales = [
            {
                "name": "Press On",
                "duration_minutes": 35,  # Máximo del rango 30-35
                "price": 35000
            },
            {
                "name": "Polygel",
                "duration_minutes": 120,  # 2 horas (máximo del rango)
                "price": 45000
            },
            {
                "name": "Acrílicas",
                "duration_minutes": 120,  # 2 horas (máximo del rango)
                "price": 50000
            },
            {
                "name": "Baño de Acrílico con Tip",
                "duration_minutes": 90,  # 1.5 horas (máximo del rango)
                "price": 40000
            },
            {
                "name": "Nivelación con Builder Gel o Base Rubber",
                "duration_minutes": 90,  # 1.5 horas (máximo del rango)
                "price": 35000
            },
            {
                "name": "Mantenimiento o Retiro",
                "duration_minutes": 60,  # 60 min (máximo del rango)
                "price": 20000
            },
            {
                "name": "Semipermanente",
                "duration_minutes": 45,  # 45 min (máximo del rango)
                "price": 25000
            },
            {
                "name": "Tips con Baño de Gel de Reconstrucción",
                "duration_minutes": 90,  # 1.5 horas (máximo del rango)
                "price": 35000
            }
        ]
        
        for servicio_data in servicios_reales:
            servicio = Service(
                worker_id=gina.id,
                **servicio_data,
                state=True
            )
            db.add(servicio)
            print(f"  ✅ {servicio_data['name']} - {servicio_data['duration_minutes']} min - ${servicio_data['price']:,}")
        
        db.commit()
        
        # 4️⃣ CREAR ADICIONALES REALES
        print("\n✨ Creando servicios adicionales reales...")
        
        adicionales_reales = [
            {
                "name": "Diseño o Figuras",
                "extra_duration": 60,  # Máximo del rango 30-60
                "price": 5000
            }
        ]
        
        for adicional_data in adicionales_reales:
            adicional = Additional(**adicional_data, state=True)
            db.add(adicional)
            print(f"  ✅ {adicional_data['name']} - +{adicional_data['extra_duration']} min - ${adicional_data['price']:,}")
        
        db.commit()
        
        print("\n" + "="*70)
        print("✅ ¡Base de datos actualizada con información REAL!")
        print("="*70)
        
        # Mostrar resumen
        total_workers = db.query(Worker).count()
        total_services = db.query(Service).count()
        total_additionals = db.query(Additional).count()
        
        print(f"\n📊 Resumen:")
        print(f"  • Manicurista: {gina.name}")
        print(f"  • Servicios: {total_services}")
        print(f"  • Adicionales: {total_additionals}")
        
        print(f"\n💡 Notas:")
        print(f"  • Duraciones: Se usó el tiempo máximo de cada rango para evitar")
        print(f"    problemas de agenda (mejor sobrar tiempo que faltar)")
        print(f"  • Horario: 9:00 AM - 9:00 PM (última cita puede iniciar a las 8:59 PM)")
        print(f"  • Máximo trabajo: Hasta las 11:00 PM para terminar última cita")
        
        print(f"\n🎯 ¡Listo para usar con datos reales de Shady's Nails!")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    update_to_real_data()
