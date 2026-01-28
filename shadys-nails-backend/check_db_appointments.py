
import sys
import os
sys.path.append(os.getcwd())
from app.database import SessionLocal
from app.models.appointment import Appointment

def check_appointments():
    db = SessionLocal()
    try:
        count = db.query(Appointment).count()
        print(f"📊 Total de citas en DB: {count}")
        if count > 0:
            apps = db.query(Appointment).limit(5).all()
            for a in apps:
                print(f" - ID: {a.id}, Worker: {a.worker_id}, Date: {a.date}, Status: {a.status}")
    finally:
        db.close()

if __name__ == "__main__":
    check_appointments()
