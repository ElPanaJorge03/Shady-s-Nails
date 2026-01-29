from app.database import SessionLocal
from app.models.worker import Worker

def list_workers():
    db = SessionLocal()
    try:
        workers = db.query(Worker).all()
        print("\n--- WORKERS ENCONTRADOS ---")
        for w in workers:
            print(f"ID: {w.id} | Nombre: {w.name} | Email: {w.email}")
        print("---------------------------\n")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    list_workers()
