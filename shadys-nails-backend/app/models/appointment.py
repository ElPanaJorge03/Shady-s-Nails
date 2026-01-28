from sqlalchemy import Column, Integer, String, Date, Time, ForeignKey, Text, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base

print("📦 Cargando modelo Appointment")

class Appointment(Base):
    __tablename__ = "appointments"

    id = Column(Integer, primary_key=True, index=True)
    worker_id = Column(Integer, ForeignKey("workers.id"), nullable=False)
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=False)
    service_id = Column(Integer, ForeignKey("services.id"), nullable=False)
    additional_id = Column(Integer, ForeignKey("additionals.id"), nullable=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)  # Usuario que creó la cita
    
    date = Column(Date, nullable=False)
    start_time = Column(Time, nullable=False)
    end_time = Column(Time, nullable=False)
    status = Column(String(20), default="confirmed")
    notes = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relaciones
    worker = relationship("Worker", back_populates="appointments")
    customer = relationship("Customer", back_populates="appointments")
    service = relationship("Service", back_populates="appointments")
    additional = relationship("Additional", back_populates="appointments")

    @property
    def worker_name(self):
        return self.worker.name if self.worker else None

    @property
    def customer_name(self):
        return self.customer.name if self.customer else None

    @property
    def service_name(self):
        return self.service.name if self.service else None

    @property
    def additional_name(self):
        return self.additional.name if self.additional else None