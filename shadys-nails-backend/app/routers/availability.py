from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from datetime import date, time, datetime, timedelta
from typing import Optional, List
from pydantic import BaseModel

from app.database import get_db
from app.models.appointment import Appointment
from app.utils.appointment_validation import get_total_duration, calculate_end_time

router = APIRouter(
    prefix="/availability",
    tags=["Availability"]
)

# ═══════════════════════════════════════════════════
# SCHEMAS
# ═══════════════════════════════════════════════════

class AvailabilityResponse(BaseModel):
    """Respuesta del endpoint de disponibilidad"""
    date: date
    worker_id: int
    service_id: int
    additional_id: Optional[int]
    total_duration_minutes: int
    available_slots: List[str]
    
    class Config:
        from_attributes = True


# ═══════════════════════════════════════════════════
# FUNCIONES AUXILIARES
# ═══════════════════════════════════════════════════

def generate_time_slots(interval_minutes: int = 15) -> List[time]:
    """
    Genera todos los slots de tiempo posibles en el día.
    
    Args:
        interval_minutes: Intervalo entre slots (default: 15 minutos)
    
    Returns:
        Lista de objetos time desde 09:00 hasta 20:59
    """
    slots = []
    current = datetime.strptime("09:00", "%H:%M")
    end = datetime.strptime("20:59", "%H:%M")
    
    while current <= end:
        slots.append(current.time())
        current += timedelta(minutes=interval_minutes)
    
    return slots


def is_slot_available(
    start_time: time,
    duration_minutes: int,
    existing_appointments: List[Appointment]
) -> bool:
    """
    Verifica si un slot está disponible.
    
    Args:
        start_time: Hora de inicio del slot
        duration_minutes: Duración total del servicio
        existing_appointments: Citas ya agendadas ese día
    
    Returns:
        True si el slot está disponible, False si no
    """
    # Calcular hora de fin
    end_time = calculate_end_time(start_time, duration_minutes)
    
    # VALIDACIÓN 1: La cita debe terminar antes de las 11:00 PM
    max_end_time = time(23, 0)
    if end_time > max_end_time:
        return False
    
    # VALIDACIÓN 2: No debe cruzarse con ninguna cita existente
    for appointment in existing_appointments:
        # Verificar si hay solapamiento
        # No hay solapamiento si:
        # - La nueva cita termina antes de que empiece la existente, O
        # - La nueva cita empieza después de que termine la existente
        no_overlap = (end_time <= appointment.start_time) or (start_time >= appointment.end_time)
        
        if not no_overlap:
            # Hay conflicto
            return False
    
    return True


# ═══════════════════════════════════════════════════
# ENDPOINT
# ═══════════════════════════════════════════════════

@router.get("", response_model=AvailabilityResponse)
def get_availability(
    worker_id: int = Query(..., description="ID de la manicurista"),
    date: date = Query(..., description="Fecha para consultar disponibilidad"),
    service_id: int = Query(..., description="ID del servicio a agendar"),
    additional_id: Optional[int] = Query(None, description="ID del adicional (opcional)"),
    db: Session = Depends(get_db)
):
    """
    Calcula y devuelve los horarios disponibles para agendar una cita.
    
    Considera:
    - Duración del servicio + adicional
    - Horarios laborales (9:00 AM - 8:59 PM inicio, 11:00 PM fin máximo)
    - Citas ya agendadas (evita conflictos)
    
    Retorna slots cada 15 minutos.
    """
    
    # 1️⃣ Calcular duración total del servicio
    total_duration = get_total_duration(
        service_id=service_id,
        additional_id=additional_id,
        db=db
    )
    
    # 2️⃣ Obtener citas existentes para ese worker en esa fecha
    existing_appointments = db.query(Appointment).filter(
        Appointment.worker_id == worker_id,
        Appointment.date == date,
        Appointment.status != "cancelled"  # Ignorar citas canceladas
    ).all()
    
    # 3️⃣ Generar todos los slots candidatos (cada 15 minutos)
    candidate_slots = generate_time_slots(interval_minutes=15)
    
    # 4️⃣ Filtrar solo los slots disponibles
    available_slots = []
    
    for slot in candidate_slots:
        if is_slot_available(slot, total_duration, existing_appointments):
            available_slots.append(slot.strftime("%H:%M:%S"))
    
    # 5️⃣ Retornar respuesta
    return AvailabilityResponse(
        date=date,
        worker_id=worker_id,
        service_id=service_id,
        additional_id=additional_id,
        total_duration_minutes=total_duration,
        available_slots=available_slots
    )
