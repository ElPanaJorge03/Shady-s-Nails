
import sys
import os
sys.path.append(os.getcwd())
from app.database import SessionLocal
from app.models.user import User

def check_users():
    db = SessionLocal()
    try:
        users = db.query(User).all()
        print(f"👥 Usuarios en DB:")
        for u in users:
            print(f" - ID: {u.id}, Email: {u.email}, Role: {u.role}")
    finally:
        db.close()

if __name__ == "__main__":
    check_users()
