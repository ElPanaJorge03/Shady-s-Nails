from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import date, time
from typing import Optional
from pydantic import BaseModel

from app.database import get_db
from app.models.appointment import Appointment
from app.utils.appointment_validation import (
    validate_appointment_time,
    calculate_end_time,
    get_total_duration
)

router = APIRouter(
    prefix="/appointments",
    tags=["Appointments"]
)

# ═══════════════════════════════════════════════════
# SCHEMAS (inline por ahora)
# ═══════════════════════════════════════════════════

class AppointmentCreate(BaseModel):
    worker_id: int
    customer_id: int
    service_id: int
    additional_id: Optional[int] = None
    date: date
    start_time: time
    notes: Optional[str] = None

class AppointmentResponse(BaseModel):
    id: int
    worker_id: int
    customer_id: int
    service_id: int
    additional_id: Optional[int]
    date: date
    start_time: time
    end_time: time
    status: str
    notes: Optional[str]
    
    class Config:
        from_attributes = True

# ═══════════════════════════════════════════════════
# ENDPOINTS
# ═══════════════════════════════════════════════════

@router.post("/", response_model=AppointmentResponse, status_code=201)
def create_appointment(
    data: AppointmentCreate,
    db: Session = Depends(get_db)
):
    """
    Crea una nueva cita con validaciones automáticas:
    - Calcula end_time según duración del servicio + adicional
    - Valida horarios (9am-8:59pm inicio, 11pm fin máximo)
    - Evita cruces con otras citas del mismo worker
    """
    
    # 1️⃣ Calcular duración total
    total_duration = get_total_duration(
        service_id=data.service_id,
        additional_id=data.additional_id,
        db=db
    )
    
    # 2️⃣ Calcular end_time automáticamente
    end_time = calculate_end_time(data.start_time, total_duration)
    
    # 3️⃣ Validar todas las reglas de negocio
    validate_appointment_time(
        worker_id=data.worker_id,
        date=data.date,
        start_time=data.start_time,
        end_time=end_time,
        db=db
    )
    
    # 4️⃣ Crear la cita
    new_appointment = Appointment(
        worker_id=data.worker_id,
        customer_id=data.customer_id,
        service_id=data.service_id,
        additional_id=data.additional_id,
        date=data.date,
        start_time=data.start_time,
        end_time=end_time,  # ✅ Calculado automáticamente
        status="confirmed",
        notes=data.notes
    )
    
    db.add(new_appointment)
    db.commit()
    db.refresh(new_appointment)
    
    return new_appointment


@router.get("/", response_model=list[AppointmentResponse])
def list_appointments(
    worker_id: Optional[int] = None,
    date: Optional[date] = None,
    db: Session = Depends(get_db)
):
    """
    Lista todas las citas, con filtros opcionales
    """
    query = db.query(Appointment)
    
    if worker_id:
        query = query.filter(Appointment.worker_id == worker_id)
    
    if date:
        query = query.filter(Appointment.date == date)
    
    return query.all()