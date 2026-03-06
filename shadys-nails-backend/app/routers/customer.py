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
    Crea un nuevo customer o retorna uno existente si ya existe con el mismo email o teléfono.
    Esto evita duplicados al agendar citas.
    """
    # 1. Buscar por email primero (más confiable, especialmente para usuarios Google OAuth)
    existing = None
    if customer.email:
        existing = db.query(Customer).filter(Customer.email == customer.email).first()
    
    # 2. Si no hay match por email, buscar por teléfono (solo si no es el default '0000000000')
    if not existing and customer.phone and customer.phone != '0000000000':
        existing = db.query(Customer).filter(Customer.phone == customer.phone).first()
    
    if existing:
        # Actualizar datos si llegaron nuevos
        existing.name = customer.name
        if customer.email:
            existing.email = customer.email
        if customer.phone and customer.phone != '0000000000':
            existing.phone = customer.phone
        db.commit()
        db.refresh(existing)
        print(f"✅ Customer existente encontrado ID={existing.id}, email={existing.email}")
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
    print(f"✅ Nuevo customer creado ID={new_customer.id}, email={new_customer.email}")
    return new_customer

