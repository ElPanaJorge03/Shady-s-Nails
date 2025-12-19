from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
from pydantic import BaseModel

from app.database import get_db
from app.models.service import Service

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


# ═══════════════════════════════════════════════════
# ENDPOINTS
# ═══════════════════════════════════════════════════

@router.get("/", response_model=List[ServiceResponse])
def list_services(
    worker_id: int = None,
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
