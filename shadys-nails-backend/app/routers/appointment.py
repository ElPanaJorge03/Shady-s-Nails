from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload
from datetime import date, time
from typing import Optional
from pydantic import BaseModel

from app.database import get_db
from app.models.appointment import Appointment
from app.dependencies import get_current_user  # Importar desde dependencies
from app.models.user import User
from app.utils.appointment_validation import (
    validate_appointment_time,
    calculate_end_time,
    get_total_duration,
    validate_future_date
)
from app.utils.entity_validation import validate_all_entities
from app.utils.email_service import send_email, get_confirmation_template, get_cancellation_template, get_update_template
from app.models.customer import Customer
from app.models.service import Service

router = APIRouter(
    prefix="/appointments",
    tags=["Appointments"]
)

# ═══════════════════════════════════════════════════
# SCHEMAS
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
    worker_name: Optional[str] = None
    customer_name: Optional[str] = None
    service_name: Optional[str] = None
    additional_name: Optional[str] = None
    
    class Config:
        from_attributes = True

class AppointmentUpdate(BaseModel):
    """Schema para actualizar una cita existente"""
    worker_id: Optional[int] = None
    customer_id: Optional[int] = None
    service_id: Optional[int] = None
    additional_id: Optional[int] = None
    date: Optional[date] = None
    start_time: Optional[time] = None
    notes: Optional[str] = None
    status: Optional[str] = None

# ═══════════════════════════════════════════════════
# ENDPOINTS
# ═══════════════════════════════════════════════════

@router.post("", response_model=AppointmentResponse, status_code=201)
def create_appointment(
    data: AppointmentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Crea una nueva cita con validaciones automáticas:
    - Valida que worker, customer y service existan
    - Auto-crea customer si no existe pero hay un user con ese ID
    - Valida que la fecha no sea en el pasado
    - Calcula end_time según duración del servicio + adicional
    - Valida horarios (9am-8:59pm inicio, 11pm fin máximo)
    - Evita cruces con otras citas del mismo worker
    - Asocia la cita al usuario autenticado (si existe)
    """
    
    # VALIDACIÓN 1: Auto-crear customer si no existe pero el user sí
    from app.models.user import User
    customer = db.query(Customer).filter(Customer.id == data.customer_id).first()
    
    if not customer:
        # Intentar encontrar el usuario correspondiente
        user = db.query(User).filter(User.id == data.customer_id).first()
        if user:
            # Auto-crear customer desde user
            customer = Customer(
                id=user.id,
                name=user.name,
                phone=user.phone,
                email=user.email
            )
            db.add(customer)
            db.commit()
            db.refresh(customer)
            print(f"✅ Auto-creado customer ID {customer.id} desde user")
        else:
            raise HTTPException(
                status_code=404,
                detail=f"Customer con ID {data.customer_id} no encontrado"
            )
    
    # VALIDACIÓN 2: Verificar que worker y service existan
    validate_all_entities(
        worker_id=data.worker_id,
        customer_id=data.customer_id,
        service_id=data.service_id,
        additional_id=data.additional_id,
        db=db
    )
    
    # VALIDACIÓN 2: Verificar que la fecha no sea en el pasado
    validate_future_date(data.date)
    
    # Calcular duración total y hora de fin
    additional_id_value = data.additional_id if data.additional_id is not None else 0
    total_duration = get_total_duration(
        service_id=data.service_id,
        additional_id=additional_id_value,
        db=db
    )
    
    end_time = calculate_end_time(data.start_time, total_duration)
    
    validate_appointment_time(
        worker_id=data.worker_id,
        date=data.date,
        start_time=data.start_time,
        end_time=end_time,
        db=db
    )
    
    new_appointment = Appointment(
        worker_id=data.worker_id,
        customer_id=data.customer_id,
        service_id=data.service_id,
        additional_id=data.additional_id,
        user_id=current_user.id if current_user else None,  # Opcional
        date=data.date,
        start_time=data.start_time,
        end_time=end_time,
        status="confirmed",
        notes=data.notes
    )
    
    db.add(new_appointment)
    db.commit()
    db.refresh(new_appointment)
    
    # 📧 ENVIAR CORREO DE CONFIRMACIÓN
    try:
        # Cargar relaciones para el correo si no están cargadas
        customer = db.query(Customer).filter(Customer.id == data.customer_id).first()
        service = db.query(Service).filter(Service.id == data.service_id).first()
        
        if customer and customer.email and service:
            body = get_confirmation_template(
                customer_name=customer.name,
                service_name=service.name,
                date=str(data.date),
                time=str(data.start_time)
            )
            send_email(
                subject="💅 Confirmación de tu cita - Shady's Nails",
                recipient=customer.email,
                body_html=body
            )
    except Exception as email_err:
        print(f"⚠️ Error al preparar email de confirmación: {email_err}")
    
    return new_appointment


@router.get("", response_model=list[AppointmentResponse])
def list_appointments(
    worker_id: Optional[int] = None,
    date: Optional[date] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Lista citas según el rol del usuario:
    - Sin autenticación: todas las citas
    - Customers: solo sus propias citas
    - Workers: todas las citas (con filtros opcionales)
    """
    query = db.query(Appointment).options(
        joinedload(Appointment.worker),
        joinedload(Appointment.customer),
        joinedload(Appointment.service),
        joinedload(Appointment.additional)
    )
    
    # Si hay usuario autenticado y es customer, filtrar por user_id
    if current_user and hasattr(current_user, 'role') and current_user.role == 'customer':
        query = query.filter(Appointment.user_id == current_user.id)
    
    # Filtros opcionales para workers o sin autenticación
    if worker_id:
        query = query.filter(Appointment.worker_id == worker_id)
    
    if date:
        query = query.filter(Appointment.date == date)
    
    return query.all()


@router.get("/{appointment_id}", response_model=AppointmentResponse)
def get_appointment(
    appointment_id: int,
    db: Session = Depends(get_db)
):
    """
    Obtiene una cita específica por su ID.
    
    Args:
        appointment_id: ID de la cita a obtener
        
    Returns:
        AppointmentResponse: Datos de la cita
        
    Raises:
        HTTPException 404: Si la cita no existe
    """
    appointment = db.query(Appointment).filter(
        Appointment.id == appointment_id
    ).first()
    
    if not appointment:
        raise HTTPException(
            status_code=404,
            detail=f"Cita con ID {appointment_id} no encontrada"
        )
    
    return appointment



@router.put("/{appointment_id}", response_model=AppointmentResponse)
def update_appointment(
    appointment_id: int,
    data: AppointmentUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Actualiza una cita existente.
    Valida automáticamente horarios y conflictos.
    """
    
    # 1️⃣ Buscar la cita existente
    appointment = db.query(Appointment).filter(
        Appointment.id == appointment_id
    ).first()
    
    if not appointment:
        raise HTTPException(
            status_code=404,
            detail=f"Cita con ID {appointment_id} no encontrada"
        )
    
    # 2️⃣ Validar que se pueda editar
    if appointment.status in ["cancelled", "completed"]:
        raise HTTPException(
            status_code=400,
            detail=f"No se puede editar una cita con status '{appointment.status}'"
        )
    
    # 3️⃣ Determinar valores finales
    worker_id = data.worker_id if data.worker_id is not None else appointment.worker_id
    customer_id = data.customer_id if data.customer_id is not None else appointment.customer_id
    service_id = data.service_id if data.service_id is not None else appointment.service_id
    additional_id = data.additional_id if data.additional_id is not None else appointment.additional_id
    date_val = data.date if data.date is not None else appointment.date
    
    # 4️⃣ Validar que las entidades existan (si se están cambiando)
    if data.worker_id or data.customer_id or data.service_id or data.additional_id is not None:
        validate_all_entities(
            worker_id=worker_id,
            customer_id=customer_id,
            service_id=service_id,
            additional_id=additional_id,
            db=db
        )
    
    # 5️⃣ Validar fecha futura (si se está cambiando)
    if data.date is not None:
        validate_future_date(date_val)
    
    start_time_val = data.start_time if data.start_time is not None else appointment.start_time
    
    # 4️⃣ Recalcular duración y end_time si cambió el servicio o adicional
    if data.service_id or data.additional_id is not None:
        duration = get_total_duration(service_id, additional_id, db)
        end_time_val = calculate_end_time(start_time_val, duration)
    else:
        end_time_val = appointment.end_time
    
    # 5️⃣ Validar reglas de negocio (excluyendo esta cita) ✅ CORREGIDO
    validate_appointment_time(
        worker_id=worker_id,
        date=date_val,
        start_time=start_time_val,
        end_time=end_time_val,
        db=db,
        appointment_id=appointment_id  # ✅ Excluir esta cita
    )
    
    # 6️⃣ Actualizar campos
    appointment.worker_id = worker_id
    appointment.customer_id = customer_id
    appointment.service_id = service_id
    appointment.additional_id = additional_id
    appointment.date = date_val
    appointment.start_time = start_time_val
    appointment.end_time = end_time_val
    
    if data.notes is not None:
        appointment.notes = data.notes
    
    if data.status is not None:
        appointment.status = data.status
    
    # 7️⃣ Guardar cambios
    db.commit()
    db.refresh(appointment)
    
    # 📧 ENVIAR CORREO DE ACTUALIZACIÓN
    try:
        # Cargar relaciones si no están cargadas
        if appointment.customer and appointment.customer.email and appointment.service:
            # Determinar qué cambió para el mensaje
            changes_list = []
            if data.date is not None:
                changes_list.append(f"Fecha actualizada a {date_val}")
            if data.start_time is not None:
                changes_list.append(f"Hora actualizada a {start_time_val}")
            if data.service_id is not None:
                changes_list.append(f"Servicio cambiado a {appointment.service.name}")
            if data.worker_id is not None and appointment.worker:
                changes_list.append(f"Manicurista cambiada a {appointment.worker.name}")
            
            changes_description = ". ".join(changes_list) if changes_list else "Se han actualizado los detalles de tu cita"
            
            body = get_update_template(
                customer_name=appointment.customer.name,
                service_name=appointment.service.name,
                date=str(appointment.date),
                time=str(appointment.start_time),
                changes=changes_description
            )
            send_email(
                subject="📝 Tu cita ha sido actualizada - Shady's Nails",
                recipient=appointment.customer.email,
                body_html=body
            )
    except Exception as email_err:
        print(f"⚠️ Error al preparar email de actualización: {email_err}")
    
    return appointment


@router.delete("/{appointment_id}", status_code=status.HTTP_200_OK)
def cancel_appointment(
    appointment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Cancela una cita (soft delete - cambia status a 'cancelled').
    No elimina físicamente la cita para mantener historial.
    """
    
    appointment = db.query(Appointment).filter(
        Appointment.id == appointment_id
    ).first()
    
    if not appointment:
        raise HTTPException(
            status_code=404,
            detail=f"Cita con ID {appointment_id} no encontrada"
        )
    
    if appointment.status == "cancelled":
        raise HTTPException(
            status_code=400,
            detail="Esta cita ya está cancelada"
        )
    
    # Guardar el status anterior antes de modificarlo
    previous_status = appointment.status
    
    appointment.status = "cancelled"
    
    db.commit()
    db.refresh(appointment)
    
    # 📧 ENVIAR CORREO DE CANCELACIÓN
    try:
        if appointment.customer and appointment.customer.email:
            body = get_cancellation_template(
                customer_name=appointment.customer.name,
                service_name=appointment.service.name if appointment.service else "Servicio",
                date=str(appointment.date),
                time=str(appointment.start_time)
            )
            send_email(
                subject="🚫 Cita Cancelada - Shady's Nails",
                recipient=appointment.customer.email,
                body_html=body
            )
    except Exception as email_err:
        print(f"⚠️ Error al preparar email de cancelación: {email_err}")
    
    return {
        "message": "Cita cancelada exitosamente",
        "appointment_id": appointment_id,
        "previous_status": previous_status,
        "new_status": "cancelled"
    }
