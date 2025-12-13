from sqlalchemy.orm import Session
from app.models.appointment import Appointment
from app.schemas.appointment import AppointmentCreate


def create_appointment(db: Session, data: AppointmentCreate):
    appointment = Appointment(
        worker_id=data.worker_id,
        customer_id=data.customer_id,
        service_id=data.service_id,
        additional_id=data.additional_id,
        date=data.date,
        start_time=data.start_time,
        end_time=data.end_time,
        notes=data.notes,
    )

    db.add(appointment)
    db.commit()
    db.refresh(appointment)

    return appointment
