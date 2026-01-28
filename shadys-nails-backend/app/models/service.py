from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base

print("📦 Cargando modelo Service")

class Service(Base):
    __tablename__ = "services"

    id = Column(Integer, primary_key=True, index=True)
    worker_id = Column(Integer, ForeignKey("workers.id"))
    name = Column(String(100), nullable=False)
    duration_minutes = Column(Integer, nullable=False)
    price = Column(Integer, nullable=False)
    state = Column(Boolean, default=True)

    # ─────────────────────────────
    # Relaciones
    # ─────────────────────────────
    worker = relationship("Worker", back_populates="services")
    appointments = relationship("Appointment", back_populates="service")
