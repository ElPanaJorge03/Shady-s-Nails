from datetime import datetime, time, timedelta, date as date_type
from sqlalchemy.orm import Session
from fastapi import HTTPException

from app.models.appointment import Appointment
from app.models.service import Service
from app.models.additional import Additional


def calculate_end_time(start_time: time, duration_minutes: int) -> time:
    """Calcula la hora de fin sumando duración a la hora de inicio"""
    dummy_date = datetime.combine(datetime.today(), start_time)
    end_datetime = dummy_date + timedelta(minutes=duration_minutes)
    return end_datetime.time()


def validate_appointment_time(
    worker_id: int,
    date: date_type,
    start_time: time,
    end_time: time,
    db: Session,
    appointment_id: int = None
) -> None:
    """Valida que la cita cumpla con todas las reglas de negocio"""
    
    # REGLA 1: Horario de inicio válido (9:00 - 20:59)
    hora_inicio_min = time(9, 0)
    hora_inicio_max = time(20, 59)
    
    if start_time < hora_inicio_min or start_time > hora_inicio_max:
        raise HTTPException(
            status_code=400,
            detail=f"La cita debe iniciar entre las 9:00 AM y las 8:59 PM"
        )
    
    # REGLA 2: La cita debe terminar antes de las 11:00 PM
    hora_fin_max = time(23, 0)
    
    if end_time > hora_fin_max:
        raise HTTPException(
            status_code=400,
            detail=f"La cita debe terminar antes de las 11:00 PM"
        )
    
    # REGLA 3: No puede cruzarse con otra cita del mismo worker
    query = db.query(Appointment).filter(
        Appointment.worker_id == worker_id,
        Appointment.date == date,
        Appointment.status != "cancelled"
    )
    
    if appointment_id:
        query = query.filter(Appointment.id != appointment_id)
    
    existing_appointments = query.all()
    
    for existing in existing_appointments:
        no_overlap = (end_time <= existing.start_time) or (start_time >= existing.end_time)
        
        if not no_overlap:
            raise HTTPException(
                status_code=409,
                detail=f"Conflicto de horario: Ya existe una cita de {existing.start_time} a {existing.end_time}"
            )


def get_total_duration(service_id: int, additional_id: int = None, db: Session = None) -> int:
    """Calcula la duración total de una cita"""
    service = db.query(Service).filter(Service.id == service_id).first()
    
    if not service:
        raise HTTPException(
            status_code=404,
            detail=f"Servicio con ID {service_id} no encontrado"
        )
    
    total_duration = service.duration_minutes
    
    if additional_id:
        additional = db.query(Additional).filter(Additional.id == additional_id).first()
        
        if not additional:
            raise HTTPException(
                status_code=404,
                detail=f"Adicional con ID {additional_id} no encontrado"
            )
        
        total_duration += additional.extra_duration
    
    return total_duration