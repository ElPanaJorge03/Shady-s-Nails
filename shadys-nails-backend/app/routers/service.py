from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel, Field

from app.database import get_db
from app.models.service import Service
from app.models.user import User
from app.dependencies import get_current_user, get_current_worker
from app.models.worker import Worker

router = APIRouter(
    prefix="/services",
    tags=["Services"]
)

# ═══════════════════════════════════════════════════
# SCHEMAS
# ═══════════════════════════════════════════════════

class ServiceResponse(BaseModel):
    """Schema para respuesta de servicio"""
    id: int
    worker_id: int
    name: str
    duration_minutes: int
    price: int
    state: bool
    
    class Config:
        from_attributes = True


class ServiceCreate(BaseModel):
    """Schema para crear un servicio"""
    name: str = Field(..., min_length=3, max_length=100, description="Nombre del servicio")
    duration_minutes: int = Field(..., gt=0, le=480, description="Duración en minutos (máx 8 horas)")
    price: int = Field(..., gt=0, description="Precio del servicio")
    state: bool = Field(default=True, description="Estado activo/inactivo")


class ServiceUpdate(BaseModel):
    """Schema para actualizar un servicio"""
    name: Optional[str] = Field(None, min_length=3, max_length=100)
    duration_minutes: Optional[int] = Field(None, gt=0, le=480)
    price: Optional[int] = Field(None, gt=0)
    state: Optional[bool] = None


# ═══════════════════════════════════════════════════
# ENDPOINTS
# ═══════════════════════════════════════════════════

@router.get("/", response_model=List[ServiceResponse])
def list_services(
    worker_id: Optional[int] = None,
    active_only: bool = True,
    db: Session = Depends(get_db)
):
    """
    Lista todos los servicios disponibles.
    
    Parámetros:
    - worker_id: Filtrar por worker específico (opcional)
    - active_only: Solo servicios activos (default: True)
    """
    query = db.query(Service)
    
    if worker_id:
        query = query.filter(Service.worker_id == worker_id)
    
    if active_only:
        query = query.filter(Service.state == True)
    
    return query.all()


@router.get("/{service_id}", response_model=ServiceResponse)
def get_service(
    service_id: int,
    db: Session = Depends(get_db)
):
    """
    Obtiene un servicio específico por ID.
    """
    service = db.query(Service).filter(Service.id == service_id).first()
    
    if not service:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Servicio con ID {service_id} no encontrado"
        )
    
    return service


@router.post("/", response_model=ServiceResponse, status_code=status.HTTP_201_CREATED)
def create_service(
    data: ServiceCreate,
    db: Session = Depends(get_db),
    current_worker: Worker = Depends(get_current_worker)
):
    """
    Crea un nuevo servicio.
    
    Solo workers pueden crear servicios.
    El servicio se asocia automáticamente al worker autenticado.
    """
    # Verificar que no exista un servicio con el mismo nombre para este worker
    existing = db.query(Service).filter(
        Service.worker_id == current_worker.id,
        Service.name == data.name
    ).first()
    
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Ya existe un servicio llamado '{data.name}'"
        )
    
    # Crear el servicio
    new_service = Service(
        worker_id=current_worker.id,
        name=data.name,
        duration_minutes=data.duration_minutes,
        price=data.price,
        state=data.state
    )
    
    db.add(new_service)
    db.commit()
    db.refresh(new_service)
    
    return new_service


@router.put("/{service_id}", response_model=ServiceResponse)
def update_service(
    service_id: int,
    data: ServiceUpdate,
    db: Session = Depends(get_db),
    current_worker: Worker = Depends(get_current_worker)
):
    """
    Actualiza un servicio existente.
    
    Solo el worker dueño del servicio puede actualizarlo.
    """
    # Buscar el servicio
    service = db.query(Service).filter(Service.id == service_id).first()
    
    if not service:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Servicio con ID {service_id} no encontrado"
        )
    
    # Verificar que el usuario sea el dueño del servicio
    if service.worker_id != current_worker.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permiso para editar este servicio"
        )
    
    # Actualizar solo los campos proporcionados
    update_data = data.dict(exclude_unset=True)
    
    # Si se está cambiando el nombre, verificar que no exista otro con ese nombre
    if 'name' in update_data and update_data['name'] != service.name:
        existing = db.query(Service).filter(
            Service.worker_id == current_user.id,
            Service.name == update_data['name'],
            Service.id != service_id
        ).first()
        
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Ya existe otro servicio llamado '{update_data['name']}'"
            )
    
    for field, value in update_data.items():
        setattr(service, field, value)
    
    db.commit()
    db.refresh(service)
    
    return service


@router.delete("/{service_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_service(
    service_id: int,
    db: Session = Depends(get_db),
    current_worker: Worker = Depends(get_current_worker)
):
    """
    Elimina un servicio.
    
    Solo el worker dueño del servicio puede eliminarlo.
    NOTA: Si hay citas asociadas, se recomienda desactivar en lugar de eliminar.
    """
    # Buscar el servicio
    service = db.query(Service).filter(Service.id == service_id).first()
    
    if not service:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Servicio con ID {service_id} no encontrado"
        )
    
    # Verificar que el usuario sea el dueño del servicio
    if service.worker_id != current_worker.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permiso para eliminar este servicio"
        )
    
    # Verificar si hay citas asociadas
    from app.models.appointment import Appointment
    appointments_count = db.query(Appointment).filter(
        Appointment.service_id == service_id
    ).count()
    
    if appointments_count > 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"No se puede eliminar el servicio porque tiene {appointments_count} cita(s) asociada(s). "
                   "Considera desactivarlo en su lugar usando PATCH /services/{service_id}/toggle"
        )
    
    db.delete(service)
    db.commit()
    
    return None


@router.patch("/{service_id}/toggle", response_model=ServiceResponse)
def toggle_service(
    service_id: int,
    db: Session = Depends(get_db),
    current_worker: Worker = Depends(get_current_worker)
):
    """
    Activa o desactiva un servicio.
    
    Esto es más seguro que eliminar, ya que preserva el historial de citas.
    """
    # Buscar el servicio
    service = db.query(Service).filter(Service.id == service_id).first()
    
    if not service:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Servicio con ID {service_id} no encontrado"
        )
    
    # Verificar que el usuario sea el dueño del servicio
    if service.worker_id != current_worker.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permiso para modificar este servicio"
        )
    
    # Cambiar el estado
    service.state = not service.state
    
    db.commit()
    db.refresh(service)
    
    return service
