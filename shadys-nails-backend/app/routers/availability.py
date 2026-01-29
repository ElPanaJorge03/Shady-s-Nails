from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from datetime import date, time, datetime, timedelta
from typing import Optional, List
from pydantic import BaseModel

from app.database import get_db
from app.models.appointment import Appointment
from app.models.schedule import WorkerSchedule, BlockedDate
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
    is_blocked: bool = False
    block_reason: Optional[str] = None
    
    class Config:
        from_attributes = True


# ═══════════════════════════════════════════════════
# FUNCIONES AUXILIARES
# ═══════════════════════════════════════════════════

def generate_time_slots(
    start_time: time,
    end_time: time,
    interval_minutes: int = 15
) -> List[time]:
    """
    Genera slots de tiempo entre start_time y end_time.
    """
    slots = []
    
    # Convertir a datetime para poder sumar minutos
    # Usamos una fecha cualquiera (hoy) para tener referencia completa
    dummy_date = datetime.today().date()
    current_dt = datetime.combine(dummy_date, start_time)
    end_dt = datetime.combine(dummy_date, end_time)
    
    # Si end_time es menor que start_time (ej. cruza medianoche), sumar un día a end
    # (Aunque en este sistema asumimos turnos diurnos simples por ahora)
    if end_dt < current_dt:
        end_dt += timedelta(days=1)
    
    while current_dt <= end_dt:
        # El slot solo es válido si CITA + DURACIÓN cabe antes del fin.
        # Pero esta función solo genera puntos de inicio.
        # El límite superior del inicio depende de si la cita cabe.
        # Aquí generamos hasta end_time. La validación `is_slot_available` filtrará.
        slots.append(current_dt.time())
        current_dt += timedelta(minutes=interval_minutes)
    
    return slots


def is_slot_available(
    start_time: time,
    duration_minutes: int,
    existing_appointments: List[Appointment],
    work_end_time: time,
    break_start: Optional[time] = None,
    break_end: Optional[time] = None
) -> bool:
    """
    Verifica si un slot está disponible considerando:
    1. Horario de cierre
    2. Descansos (si existen)
    3. Citas existentes
    """
    # Calcular hora de fin de la CITA propuesta
    end_time = calculate_end_time(start_time, duration_minutes)
    
    # VALIDACIÓN 1: La cita debe terminar antes o a la misma hora del cierre
    # Ojo: si end_time es 00:00 (medianoche), hay que manejarlo con cuidado.
    # Asumimos logica simple del mismo día para work_end_time
    if end_time > work_end_time and end_time != time(0,0): 
        # Si termina después del cierre, NO disponible.
        # (Nota: calculate_end_time maneja cruce de día, pero aquí comparamos tiempos simples)
        return False
    
    # VALIDACIÓN 2: No debe cruzarse con el descanso (si existe)
    if break_start and break_end:
        # Si la cita empieza antes del fin del descanso Y termina después del inicio del descanso
        overlap_break = (start_time < break_end) and (end_time > break_start)
        if overlap_break:
            return False

    # VALIDACIÓN 3: No debe cruzarse con ninguna cita existente
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
    Calcula horarios dinámicos basados en la configuración del worker.
    """
    
    # 0️⃣ Verificar si la fecha está BLOQUEADA
    blocked = db.query(BlockedDate).filter(
        BlockedDate.worker_id == worker_id,
        BlockedDate.date == date
    ).first()

    if blocked:
        return AvailabilityResponse(
            date=date, worker_id=worker_id, service_id=service_id, additional_id=additional_id,
            total_duration_minutes=0, available_slots=[], is_blocked=True, block_reason=blocked.reason
        )

    # 1️⃣ Obtener configuración de horario para ese día
    day_of_week = date.weekday() # 0=Monday, 6=Sunday
    schedule = db.query(WorkerSchedule).filter(
        WorkerSchedule.worker_id == worker_id,
        WorkerSchedule.day_of_week == day_of_week
    ).first()

    # Logica de defaults si no existe configuración
    if not schedule:
        # Default: Lunes a Sábado, 9AM a 8PM
        if day_of_week < 6:
            start_time = time(9, 0)
            end_time = time(20, 0) # 8 PM
            is_working = True
        else:
            # Domingo descanso por defecto
            is_working = False
            start_time = time(9, 0)
            end_time = time(18, 0)
        
        break_start = None
        break_end = None
    else:
        is_working = schedule.is_working
        start_time = schedule.start_time
        end_time = schedule.end_time
        break_start = schedule.break_start
        break_end = schedule.break_end

    # Si no trabaja ese día, retornar vacío
    if not is_working:
        return AvailabilityResponse(
            date=date, worker_id=worker_id, service_id=service_id, additional_id=additional_id,
            total_duration_minutes=0, available_slots=[], is_blocked=False, block_reason="Día no laboral"
        )
    
    # 2️⃣ Calcular duración total del servicio
    total_duration = get_total_duration(
        service_id=service_id,
        additional_id=additional_id,
        db=db
    )
    
    # 3️⃣ Obtener citas existentes
    existing_appointments = db.query(Appointment).filter(
        Appointment.worker_id == worker_id,
        Appointment.date == date,
        Appointment.status != "cancelled"
    ).all()
    
    # 4️⃣ Generar slots candidatos según horario laboral
    candidate_slots = generate_time_slots(
        start_time=start_time,
        end_time=end_time, # Generar hasta el cierre
        interval_minutes=15
    )
    
    # 5️⃣ Filtrar solo los slots disponibles
    available_slots = []
    
    for slot in candidate_slots:
        # El slot de inicio no puede ser IGUAL al end_time laboral
        if slot >= end_time:
            continue

        if is_slot_available(
            start_time=slot,
            duration_minutes=total_duration,
            existing_appointments=existing_appointments,
            work_end_time=end_time,
            break_start=break_start,
            break_end=break_end
        ):
            available_slots.append(slot.strftime("%H:%M:%S"))
    
    # 6️⃣ Retornar respuesta
    return AvailabilityResponse(
        date=date,
        worker_id=worker_id,
        service_id=service_id,
        additional_id=additional_id,
        total_duration_minutes=total_duration,
        available_slots=available_slots
    )
