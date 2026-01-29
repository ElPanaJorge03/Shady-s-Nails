"""
Router de estadísticas para el dashboard de workers
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func, and_
from typing import Dict, List
from datetime import datetime, timedelta, date
from pydantic import BaseModel

from app.database import get_db
from app.models.user import User
from app.models.appointment import Appointment
from app.models.service import Service
from app.dependencies import get_current_user

router = APIRouter(
    prefix="/stats",
    tags=["Statistics"]
)

# ═══════════════════════════════════════════════════
# SCHEMAS
# ═══════════════════════════════════════════════════

class DailyStats(BaseModel):
    """Estadísticas del día"""
    date: str
    total_appointments: int
    confirmed_appointments: int
    pending_appointments: int
    completed_appointments: int
    cancelled_appointments: int
    estimated_revenue: int
    actual_revenue: int
    global_pending_appointments: int = 0  # 🆕 Nuevo campo para el total global

class ServicePopularity(BaseModel):
    """Popularidad de servicios"""
    service_id: int
    service_name: str
    total_bookings: int
    total_revenue: int

class RevenueStats(BaseModel):
    """Estadísticas de ingresos"""
    period: str
    total_revenue: int
    completed_revenue: int
    pending_revenue: int
    total_appointments: int


# ═══════════════════════════════════════════════════
# ENDPOINTS
# ═══════════════════════════════════════════════════

@router.get("/today", response_model=DailyStats)
def get_today_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Obtiene las estadísticas del día actual.
    Solo para workers.
    """
    if current_user.role != 'worker':
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo los workers pueden ver estadísticas"
        )
    
    today = date.today()
    
    # Obtener todas las citas del día para los KPIs diarios
    appointments = db.query(Appointment).filter(
        Appointment.worker_id == current_user.id,
        Appointment.date == today
    ).all()
    
    # Calcular estadísticas del DÍA
    total = len(appointments)
    confirmed = sum(1 for apt in appointments if apt.status == 'confirmed')
    pending = sum(1 for apt in appointments if apt.status == 'pending')
    completed = sum(1 for apt in appointments if apt.status == 'completed')
    cancelled = sum(1 for apt in appointments if apt.status == 'cancelled')
    
    # 🆕 Calcular total GLOBAL de pendientes (pendientes + confirmadas futuras)
    # Consideramos 'pending' y 'confirmed' como trabajo futuro pendiente
    global_pending = db.query(func.count(Appointment.id)).filter(
        Appointment.worker_id == current_user.id,
        Appointment.status.in_(['pending', 'confirmed']),
        Appointment.date >= today
    ).scalar() or 0
    
    # Calcular ingresos del día
    estimated_revenue = 0
    actual_revenue = 0
    
    for apt in appointments:
        service = db.query(Service).filter(Service.id == apt.service_id).first()
        if service:
            revenue = service.price
            # Agregar precio del adicional si existe
            if apt.additional_id:
                from app.models.additional import Additional
                additional = db.query(Additional).filter(Additional.id == apt.additional_id).first()
                if additional:
                    revenue += additional.price
            
            estimated_revenue += revenue
            if apt.status == 'completed':
                actual_revenue += revenue
    
    return DailyStats(
        date=str(today),
        total_appointments=total,
        confirmed_appointments=confirmed,
        pending_appointments=pending,
        completed_appointments=completed,
        cancelled_appointments=cancelled,
        estimated_revenue=estimated_revenue,
        actual_revenue=actual_revenue,
        global_pending_appointments=global_pending
    )


@router.get("/week", response_model=RevenueStats)
def get_week_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Obtiene las estadísticas de la semana actual.
    """
    if current_user.role != 'worker':
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo los workers pueden ver estadísticas"
        )
    
    today = date.today()
    week_start = today - timedelta(days=today.weekday())
    week_end = week_start + timedelta(days=6)
    
    appointments = db.query(Appointment).filter(
        Appointment.worker_id == current_user.id,
        Appointment.date >= week_start,
        Appointment.date <= week_end
    ).all()
    
    total_revenue = 0
    completed_revenue = 0
    pending_revenue = 0
    
    for apt in appointments:
        service = db.query(Service).filter(Service.id == apt.service_id).first()
        if service:
            revenue = service.price
            if apt.additional_id:
                from app.models.additional import Additional
                additional = db.query(Additional).filter(Additional.id == apt.additional_id).first()
                if additional:
                    revenue += additional.price
            
            total_revenue += revenue
            if apt.status == 'completed':
                completed_revenue += revenue
            elif apt.status in ['pending', 'confirmed']:
                pending_revenue += revenue
    
    return RevenueStats(
        period="week",
        total_revenue=total_revenue,
        completed_revenue=completed_revenue,
        pending_revenue=pending_revenue,
        total_appointments=len(appointments)
    )


@router.get("/month", response_model=RevenueStats)
def get_month_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Obtiene las estadísticas del mes actual.
    """
    if current_user.role != 'worker':
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo los workers pueden ver estadísticas"
        )
    
    today = date.today()
    month_start = date(today.year, today.month, 1)
    
    # Calcular el último día del mes
    if today.month == 12:
        month_end = date(today.year + 1, 1, 1) - timedelta(days=1)
    else:
        month_end = date(today.year, today.month + 1, 1) - timedelta(days=1)
    
    appointments = db.query(Appointment).filter(
        Appointment.worker_id == current_user.id,
        Appointment.date >= month_start,
        Appointment.date <= month_end
    ).all()
    
    total_revenue = 0
    completed_revenue = 0
    pending_revenue = 0
    
    for apt in appointments:
        service = db.query(Service).filter(Service.id == apt.service_id).first()
        if service:
            revenue = service.price
            if apt.additional_id:
                from app.models.additional import Additional
                additional = db.query(Additional).filter(Additional.id == apt.additional_id).first()
                if additional:
                    revenue += additional.price
            
            total_revenue += revenue
            if apt.status == 'completed':
                completed_revenue += revenue
            elif apt.status in ['pending', 'confirmed']:
                pending_revenue += revenue
    
    return RevenueStats(
        period="month",
        total_revenue=total_revenue,
        completed_revenue=completed_revenue,
        pending_revenue=pending_revenue,
        total_appointments=len(appointments)
    )


@router.get("/services-popular", response_model=List[ServicePopularity])
def get_popular_services(
    limit: int = 10,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Obtiene los servicios más populares.
    """
    if current_user.role != 'worker':
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo los workers pueden ver estadísticas"
        )
    
    # Agrupar por servicio y contar
    results = db.query(
        Service.id,
        Service.name,
        func.count(Appointment.id).label('total_bookings'),
        func.sum(Service.price).label('total_revenue')
    ).join(
        Appointment, Appointment.service_id == Service.id
    ).filter(
        Service.worker_id == current_user.id
    ).group_by(
        Service.id, Service.name
    ).order_by(
        func.count(Appointment.id).desc()
    ).limit(limit).all()
    
    return [
        ServicePopularity(
            service_id=r[0],
            service_name=r[1],
            total_bookings=r[2],
            total_revenue=r[3] or 0
        )
        for r in results
    ]
