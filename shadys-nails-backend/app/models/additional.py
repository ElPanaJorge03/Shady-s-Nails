from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy.orm import relationship
from app.database import Base

print("📦 Cargando modelo Additional")

class Additional(Base):
    __tablename__ = "additionals"

    id = Column(Integer, primary_key=True, index=True)

    name = Column(String(100), nullable=False)
    extra_duration = Column(Integer, nullable=False)  # minutos extra
    price = Column(Integer, nullable=False)

    state = Column(Boolean, default=True)

    # ─────────────────────────────
    # Relaciones
    # ─────────────────────────────
    appointments = relationship(
        "Appointment",
        back_populates="additional"
    )
