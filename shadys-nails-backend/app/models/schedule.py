from sqlalchemy import Column, Integer, String, Boolean, Time, Date, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from app.database import Base

class WorkerSchedule(Base):
    __tablename__ = "worker_schedules"

    id = Column(Integer, primary_key=True, index=True)
    worker_id = Column(Integer, ForeignKey("workers.id"), nullable=False)
    day_of_week = Column(Integer, nullable=False)  # 0=Monday, 6=Sunday
    is_working = Column(Boolean, default=True)
    start_time = Column(Time, nullable=False, default="09:00:00")
    end_time = Column(Time, nullable=False, default="18:00:00")
    break_start = Column(Time, nullable=True)
    break_end = Column(Time, nullable=True)

    worker = relationship("Worker", backref="schedules")

    # Evitar duplicados para el mismo día y trabajador
    __table_args__ = (
        UniqueConstraint('worker_id', 'day_of_week', name='uq_worker_day_schedule'),
    )

class BlockedDate(Base):
    __tablename__ = "blocked_dates"

    id = Column(Integer, primary_key=True, index=True)
    worker_id = Column(Integer, ForeignKey("workers.id"), nullable=False)
    date = Column(Date, nullable=False)
    reason = Column(String(255), nullable=True)

    worker = relationship("Worker", backref="blocked_dates")

    # Evitar duplicados de fecha para el mismo trabajador
    __table_args__ = (
        UniqueConstraint('worker_id', 'date', name='uq_worker_date_block'),
    )
