from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
from pydantic import BaseModel

from app.database import get_db
from app.models.additional import Additional

router = APIRouter(
    prefix="/additionals",
    tags=["Additionals"]
)

# ═══════════════════════════════════════════════════
# SCHEMAS
# ═══════════════════════════════════════════════════

class AdditionalResponse(BaseModel):
    """Schema para respuesta de additional"""
    id: int
    name: str
    extra_duration: int
    price: int
    state: bool
    
    class Config:
        from_attributes = True


# ═══════════════════════════════════════════════════
# ENDPOINTS
# ═══════════════════════════════════════════════════

@router.get("/", response_model=List[AdditionalResponse])
def list_additionals(
    active_only: bool = True,
    db: Session = Depends(get_db)
):
    """
    Lista todos los adicionales disponibles (diseños, etc.).
    
    Parámetros:
    - active_only: Solo adicionales activos (default: True)
    """
    query = db.query(Additional)
    
    if active_only:
        query = query.filter(Additional.state == True)
    
    return query.all()
