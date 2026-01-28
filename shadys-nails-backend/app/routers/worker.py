from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
from pydantic import BaseModel, EmailStr
from typing import Optional

from app.database import get_db
from app.models.worker import Worker

router = APIRouter(
    prefix="/workers",
    tags=["Workers"]
)

# ═══════════════════════════════════════════════════
# SCHEMAS
# ═══════════════════════════════════════════════════

class WorkerResponse(BaseModel):
    """Schema para respuesta de worker"""
    id: int
    name: str
    phone: Optional[str]
    email: Optional[str]
    business_name: Optional[str]
    state: bool
    
    class Config:
        from_attributes = True


# ═══════════════════════════════════════════════════
# ENDPOINTS
# ═══════════════════════════════════════════════════

@router.get("/", response_model=List[WorkerResponse])
def list_workers(
    active_only: bool = True,
    db: Session = Depends(get_db)
):
    """
    Lista todos los workers (manicuristas) disponibles.
    
    Parámetros:
    - active_only: Solo workers activos (default: True)
    """
    query = db.query(Worker)
    
    if active_only:
        query = query.filter(Worker.state == True)
    
    return query.all()
