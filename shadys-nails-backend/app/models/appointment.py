from sqlalchemy import Column, Integer, String, Date, Time, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base

print("📦 Cargando modelo Appointment")

class Appointment(Base):
    __tablename__ = "appointments"

    id = Column(Integer, primary_key=True, index=True)
    worker_id = Column(Integer, ForeignKey("workers.id"), nullable=False)
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=False)
    service_id = Column(Integer, ForeignKey("services.id"), nullable=False)
    additional_id = Column(Integer, ForeignKey("additionals.id"), nullable=True)
    
    date = Column(Date, nullable=False)
    start_time = Column(Time, nullable=False)
    end_time = Column(Time, nullable=False)
    status = Column(String(20), default="confirmed")
    notes = Column(String(255))

    # ═══════════════════════════════════════════════════
    # RELACIONES (ESTO ES LO QUE FALTA)
    # ═══════════════════════════════════════════════════
    worker = relationship("Worker", back_populates="appointments")
    customer = relationship("Customer", back_populates="appointments")
    service = relationship("Service", back_populates="appointments")
    additional = relationship("Additional", back_populates="appointments")