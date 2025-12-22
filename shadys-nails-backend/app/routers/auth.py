"""
Router de autenticación
Endpoints para login, registro y gestión de usuarios
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import select

from app.database import get_db
from app.models.user import User
from app.schemas.auth import Token, UserResponse, LoginRequest, RegisterRequest
from app.utils.security import verify_password, create_access_token, get_password_hash
from app.dependencies import get_current_user  # Importar desde dependencies

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)


# Explicit OPTIONS handlers for CORS preflight
@router.options("/register")
@router.options("/login")
async def options_handler():
    """Handle CORS preflight requests"""
    return {}



@router.post("/register", response_model=UserResponse, status_code=201)
def register(
    register_data: RegisterRequest,
    db: Session = Depends(get_db)
):
    """
    Registro de nuevo usuario (cliente)
    """
    # Verificar si el email ya existe
    statement = select(User).where(User.email == register_data.email)
    result = db.execute(statement)
    existing_user = result.scalar_one_or_none()
    
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Crear nuevo usuario
    new_user = User(
        email=register_data.email,
        password_hash=get_password_hash(register_data.password),
        name=register_data.name,
        phone=register_data.phone,
        role='customer'
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    return new_user


@router.post("/login", response_model=Token)
def login(
    login_data: LoginRequest,
    db: Session = Depends(get_db)
):
    """
    Login de usuario (worker o customer)
    
    Retorna un JWT token si las credenciales son correctas
    """
    # Buscar usuario por email
    statement = select(User).where(User.email == login_data.email)
    result = db.execute(statement)
    user = result.scalar_one_or_none()
    
    # Verificar que existe
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Verificar contraseña
    if not verify_password(login_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Verificar que esté activo
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user"
        )
    
    # Crear token con user_id y role
    access_token = create_access_token(
        data={
            "sub": user.email,
            "user_id": user.id,
            "role": user.role
        }
    )
    
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/me", response_model=UserResponse)
async def get_me(current_user: User = Depends(get_current_user)):
    """
    Obtiene la información del usuario actual
    """
    return current_user


@router.post("/logout")
async def logout():
    """
    Logout (en el cliente se debe eliminar el token)
    """
    return {"message": "Logged out successfully"}
