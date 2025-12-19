"""
Validaciones de existencia de entidades
Verifica que worker, customer, service y additional existan en la BD
"""

from sqlalchemy.orm import Session
from fastapi import HTTPException
from typing import Optional

from app.models.worker import Worker
from app.models.customer import Customer
from app.models.service import Service
from app.models.additional import Additional


def validate_worker_exists(worker_id: int, db: Session) -> Worker:
    """
    Valida que el worker exista en la base de datos.
    
    Args:
        worker_id: ID del worker a validar
        db: Sesión de base de datos
        
    Returns:
        Worker: El worker si existe
        
    Raises:
        HTTPException 404: Si el worker no existe
    """
    worker = db.query(Worker).filter(Worker.id == worker_id).first()
    
    if not worker:
        raise HTTPException(
            status_code=404,
            detail=f"Worker con ID {worker_id} no encontrado"
        )
    
    if not worker.state:
        raise HTTPException(
            status_code=400,
            detail=f"Worker con ID {worker_id} está inactivo"
        )
    
    return worker


def validate_customer_exists(customer_id: int, db: Session) -> Customer:
    """
    Valida que el customer exista en la base de datos.
    
    Args:
        customer_id: ID del customer a validar
        db: Sesión de base de datos
        
    Returns:
        Customer: El customer si existe
        
    Raises:
        HTTPException 404: Si el customer no existe
    """
    customer = db.query(Customer).filter(Customer.id == customer_id).first()
    
    if not customer:
        raise HTTPException(
            status_code=404,
            detail=f"Customer con ID {customer_id} no encontrado"
        )
    
    return customer


def validate_service_exists(service_id: int, db: Session) -> Service:
    """
    Valida que el service exista en la base de datos.
    
    Args:
        service_id: ID del service a validar
        db: Sesión de base de datos
        
    Returns:
        Service: El service si existe
        
    Raises:
        HTTPException 404: Si el service no existe
    """
    service = db.query(Service).filter(Service.id == service_id).first()
    
    if not service:
        raise HTTPException(
            status_code=404,
            detail=f"Service con ID {service_id} no encontrado"
        )
    
    if not service.state:
        raise HTTPException(
            status_code=400,
            detail=f"Service con ID {service_id} está inactivo"
        )
    
    return service


def validate_additional_exists(additional_id: int, db: Session) -> Additional:
    """
    Valida que el additional exista en la base de datos.
    
    Args:
        additional_id: ID del additional a validar
        db: Sesión de base de datos
        
    Returns:
        Additional: El additional si existe
        
    Raises:
        HTTPException 404: Si el additional no existe
    """
    additional = db.query(Additional).filter(Additional.id == additional_id).first()
    
    if not additional:
        raise HTTPException(
            status_code=404,
            detail=f"Additional con ID {additional_id} no encontrado"
        )
    
    if not additional.state:
        raise HTTPException(
            status_code=400,
            detail=f"Additional con ID {additional_id} está inactivo"
        )
    
    return additional


def validate_all_entities(
    worker_id: int,
    customer_id: int,
    service_id: int,
    additional_id: Optional[int],
    db: Session
) -> None:
    """
    Valida que todas las entidades existan en la base de datos.
    
    Args:
        worker_id: ID del worker
        customer_id: ID del customer
        service_id: ID del service
        additional_id: ID del additional (opcional)
        db: Sesión de base de datos
        
    Raises:
        HTTPException 404: Si alguna entidad no existe
        HTTPException 400: Si alguna entidad está inactiva
    """
    validate_worker_exists(worker_id, db)
    validate_customer_exists(customer_id, db)
    validate_service_exists(service_id, db)
    
    if additional_id is not None:
        validate_additional_exists(additional_id, db)
