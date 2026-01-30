from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import time, date
from pydantic import BaseModel

from app.database import get_db
from app.models.schedule import WorkerSchedule, BlockedDate
from app.models.user import User
from app.dependencies import get_current_user, get_current_worker
from app.models.worker import Worker

router = APIRouter(
    prefix="/schedules",
    tags=["Schedules"]
)

# ═══════════════════════════════════════════════════
# SCHEMAS
# ═══════════════════════════════════════════════════

class ScheduleItem(BaseModel):
    day_of_week: int # 0-6
    is_working: bool
    start_time: time
    end_time: time
    break_start: Optional[time] = None
    break_end: Optional[time] = None

class ScheduleUpdate(BaseModel):
    schedules: List[ScheduleItem]

class BlockedDateCreate(BaseModel):
    date: date
    reason: Optional[str] = None

class BlockedDateResponse(BaseModel):
    id: int
    worker_id: int
    date: date
    reason: Optional[str]

    class Config:
        from_attributes = True

# ═══════════════════════════════════════════════════
# ENDPOINTS
# ═══════════════════════════════════════════════════

@router.get("", response_model=List[ScheduleItem])
def get_my_schedule(
    db: Session = Depends(get_db),
    current_worker: Worker = Depends(get_current_worker)
):
    """
    Obtiene el horario de trabajo del worker autenticado.
    Si no tiene horario configurado, devuelve uno por defecto (9-6 L-S).
    """
    # Buscar horario en BD
    db_schedules = db.query(WorkerSchedule).filter(
        WorkerSchedule.worker_id == current_worker.id
    ).order_by(WorkerSchedule.day_of_week).all()

    # Si ya tiene configuración, devolverla
    if db_schedules:
        return [
            ScheduleItem(
                day_of_week=s.day_of_week,
                is_working=s.is_working,
                start_time=s.start_time,
                end_time=s.end_time,
                break_start=s.break_start,
                break_end=s.break_end
            ) for s in db_schedules
        ]
    
    # Si no, devolver defaults
    defaults = []
    for day in range(7):
        # Por defecto Lunes(0) a Sabado(5) trabaja, Domingo(6) descansa
        is_working = day < 6
        defaults.append(ScheduleItem(
            day_of_week=day,
            is_working=is_working,
            start_time=time(9, 0),
            end_time=time(18, 0)
        ))
    return defaults


@router.put("", status_code=200)
def update_schedule(
    data: ScheduleUpdate,
    db: Session = Depends(get_db),
    current_worker: Worker = Depends(get_current_worker)
):
    """
    Actualiza el horario semanal del worker.
    Sobreescribe la configuración existente.
    """
    # Borrar configuración anterior (simple reset)
    db.query(WorkerSchedule).filter(WorkerSchedule.worker_id == current_worker.id).delete()
    
    # Crear nuevos registros
    for item in data.schedules:
        new_schedule = WorkerSchedule(
            worker_id=current_worker.id,
            day_of_week=item.day_of_week,
            is_working=item.is_working,
            start_time=item.start_time,
            end_time=item.end_time,
            break_start=item.break_start,
            break_end=item.break_end
        )
        db.add(new_schedule)
    
    db.commit()
    return {"message": "Horario actualizado correctamente"}


@router.get("/blocks", response_model=List[BlockedDateResponse])
def get_blocked_dates(
    db: Session = Depends(get_db),
    current_worker: Worker = Depends(get_current_worker)
):
    return db.query(BlockedDate).filter(
        BlockedDate.worker_id == current_worker.id,
        BlockedDate.date >= date.today()
    ).order_by(BlockedDate.date).all()


@router.post("/blocks", response_model=BlockedDateResponse)
def block_date(
    data: BlockedDateCreate,
    db: Session = Depends(get_db),
    current_worker: Worker = Depends(get_current_worker)
):
    # Verificar si ya existe
    existing = db.query(BlockedDate).filter(
        BlockedDate.worker_id == current_worker.id,
        BlockedDate.date == data.date
    ).first()
    
    if existing:
        raise HTTPException(status_code=400, detail="Esta fecha ya está bloqueada")

    new_block = BlockedDate(
        worker_id=current_worker.id,
        date=data.date,
        reason=data.reason
    )
    db.add(new_block)
    db.commit()
    db.refresh(new_block)
    return new_block


@router.delete("/blocks/{date_val}")
def unblock_date(
    date_val: date,
    db: Session = Depends(get_db),
    current_worker: Worker = Depends(get_current_worker)
):
    deleted = db.query(BlockedDate).filter(
        BlockedDate.worker_id == current_worker.id,
        BlockedDate.date == date_val
    ).delete()

    if deleted == 0:
        raise HTTPException(status_code=404, detail="Fecha no encontrada")
    
    db.commit()
    return {"message": "Fecha desbloqueada"}
