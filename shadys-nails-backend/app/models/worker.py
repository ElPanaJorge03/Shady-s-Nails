from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy.orm import relationship
from app.database import Base

print("📦 Cargando modelo Worker")

class Worker(Base):
    __tablename__ = "workers"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    phone = Column(String(20))
    email = Column(String(100))
    business_name = Column(String(100))
    state = Column(Boolean, default=True)

    # ─────────────────────────────
    # Relaciones
    # ─────────────────────────────
    appointments = relationship("Appointment", back_populates="worker")
    services = relationship("Service", back_populates="worker")
