from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel

from app.database import get_db
from app.models.customer import Customer

router = APIRouter(
    prefix="/customers",
    tags=["Customers"]
)

# ═══════════════════════════════════════════════════
# SCHEMAS
# ═══════════════════════════════════════════════════

class CustomerResponse(BaseModel):
    """Schema para respuesta de customer"""
    id: int
    name: str
    phone: Optional[str]
    email: Optional[str]
    
    class Config:
        from_attributes = True


class CustomerCreate(BaseModel):
    """Schema para crear customer"""
    name: str
    phone: str
    email: Optional[str] = None


# ═══════════════════════════════════════════════════
# ENDPOINTS
# ═══════════════════════════════════════════════════

@router.get("/", response_model=List[CustomerResponse])
def list_customers(
    db: Session = Depends(get_db)
):
    """
    Lista todos los clientes registrados.
    """
    return db.query(Customer).all()


@router.post("/", response_model=CustomerResponse)
def create_or_get_customer(
    customer: CustomerCreate,
    db: Session = Depends(get_db)
):
    """
    Crea un nuevo customer o retorna uno existente si ya existe con el mismo teléfono.
    Esto evita duplicados al agendar citas.
    """
    # Buscar si ya existe un customer con ese teléfono
    existing = db.query(Customer).filter(Customer.phone == customer.phone).first()
    
    if existing:
        # Actualizar datos si es necesario
        existing.name = customer.name
        if customer.email:
            existing.email = customer.email
        db.commit()
        db.refresh(existing)
        return existing
    
    # Crear nuevo customer
    new_customer = Customer(
        name=customer.name,
        phone=customer.phone,
        email=customer.email
    )
    db.add(new_customer)
    db.commit()
    db.refresh(new_customer)
    return new_customer

