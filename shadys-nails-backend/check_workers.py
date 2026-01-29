from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models.worker import Worker
from app.database import Base

SQLALCHEMY_DATABASE_URL = "sqlite:///./shadys_nails.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

db = SessionLocal()
workers = db.query(Worker).all()

print(f"Encontrados {len(workers)} workers:")
for w in workers:
    print(f"ID: {w.id} | Name: {w.name} | Email: {w.email}")

db.close()
