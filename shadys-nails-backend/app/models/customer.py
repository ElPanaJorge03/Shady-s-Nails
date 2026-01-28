from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from app.database import Base

print("📦 Cargando modelo Customer")

class Customer(Base):
    __tablename__ = "customers"

    id = Column(Integer, primary_key=True, index=True)

    name = Column(String(100), nullable=False)
    phone = Column(String(20))
    email = Column(String(100))

    # ─────────────────────────────
    # Relaciones
    # ─────────────────────────────
    appointments = relationship("Appointment",back_populates="customer")
 