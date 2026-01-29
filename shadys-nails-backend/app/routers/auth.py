"""
Router de autenticación
Endpoints para login, registro y gestión de usuarios
"""

import random
import string
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, status, Body
from sqlalchemy.orm import Session
from sqlalchemy import select

from app.database import get_db
from app.models.user import User
from app.schemas.auth import (
    Token, UserResponse, LoginRequest, RegisterRequest, 
    UserUpdate, ForgotPasswordRequest, ResetPasswordRequest,
    GoogleLoginRequest
)
from app.utils.security import verify_password, create_access_token, create_refresh_token, get_password_hash, decode_refresh_token
from app.dependencies import get_current_user
from app.utils.email_service import send_email, get_reset_password_template

# Google Auth
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests
import os

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
    
    # Crear access y refresh token
    token_data = {
        "sub": user.email,
        "user_id": user.id,
        "role": user.role
    }
    access_token = create_access_token(data=token_data)
    refresh_token = create_refresh_token(data=token_data)
    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}


@router.post("/refresh", response_model=Token)
def refresh_token(
    refresh_token: str = Body(..., embed=True),
    db: Session = Depends(get_db)
):
    """
    Renueva el access token usando un refresh token válido
    """
    payload = decode_refresh_token(refresh_token)
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    # Buscar usuario por email
    email = payload.get("sub")
    statement = select(User).where(User.email == email)
    result = db.execute(statement)
    user = result.scalar_one_or_none()
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive",
            headers={"WWW-Authenticate": "Bearer"},
        )
    token_data = {
        "sub": user.email,
        "user_id": user.id,
        "role": user.role
    }
    access_token = create_access_token(data=token_data)
    new_refresh_token = create_refresh_token(data=token_data)
    return {"access_token": access_token, "refresh_token": new_refresh_token, "token_type": "bearer"}


@router.get("/me", response_model=UserResponse)
async def get_me(current_user: User = Depends(get_current_user)):
    """
    Obtiene la información del usuario actual
    """
    return current_user


@router.put("/me", response_model=UserResponse)
def update_me(
    user_data: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Actualiza la información del usuario actual (nombre, teléfono, contraseña)
    """
    if user_data.name is not None:
        current_user.name = user_data.name
    
    if user_data.phone is not None:
        current_user.phone = user_data.phone
        
    if user_data.password is not None:
        # Validar password minima longitud si se desea
        if len(user_data.password) < 6:
             raise HTTPException(status_code=400, detail="Password must be at least 6 characters")
        current_user.password_hash = get_password_hash(user_data.password)
    
    db.commit()
    db.refresh(current_user)
    return current_user


@router.post("/logout")
async def logout():
    """
    Logout (en el cliente se debe eliminar el token)
    """
    return {"message": "Logged out successfully"}


@router.post("/forgot-password")
def forgot_password(data: ForgotPasswordRequest, db: Session = Depends(get_db)):
    """Genera un código de recuperación y lo envía por email"""
    user = db.query(User).filter(User.email == data.email).first()
    if not user:
        # Por seguridad no revelamos si el email existe, pero internamente no hacemos nada
        return {"message": "Si el email está registrado, recibirás un código en breve."}

    # Generar código de 6 dígitos
    code = ''.join(random.choices(string.digits, k=6))
    user.reset_token = code
    user.reset_token_expires = datetime.now() + timedelta(minutes=15)
    db.commit()

    # Enviar email
    try:
        body = get_reset_password_template(user.name, code)
        send_email(
            subject="🔐 Código de recuperación - Shady's Nails",
            recipient=user.email,
            body_html=body
        )
    except Exception as e:
        print(f"Error enviando email de recuperación: {e}")

    return {"message": "Si el email está registrado, recibirás un código en breve."}


@router.post("/reset-password")
def reset_password(data: ResetPasswordRequest, db: Session = Depends(get_db)):
    """Valida el código y cambia la contraseña"""
    user = db.query(User).filter(User.email == data.email).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    if not user.reset_token or user.reset_token != data.code:
        raise HTTPException(status_code=400, detail="Código inválido o ya utilizado")

    if datetime.now() > user.reset_token_expires:
        raise HTTPException(status_code=400, detail="El código ha expirado")

    # Cambiar contraseña
    user.password_hash = get_password_hash(data.new_password)
    user.reset_token = None # Limpiar token
    user.reset_token_expires = None
    db.commit()

    return {"message": "Contraseña actualizada con éxito. Ya puedes iniciar sesión."}


@router.post("/google", response_model=Token)
def google_auth(data: GoogleLoginRequest, db: Session = Depends(get_db)):
    """
    Autenticación con Google
    1. Verifica el token con Google
    2. Crea el usuario si no existe
    3. Retorna tokens de acceso
    """
    client_id = os.getenv("GOOGLE_CLIENT_ID")
    if not client_id:
        print("⚠️ GOOGLE_CLIENT_ID no configurado en .env")
        # Para desarrollo, puedes ponerlo aquí si quieres, sino fallará.
        # client_id = "TU_CLIENT_ID_REAL"
    
    try:
        # 1. Verificar el token de Google
        idinfo = id_token.verify_oauth2_token(
            data.id_token, 
            google_requests.Request(), 
            client_id
        )

        # ID de usuario en Google (sub) y email
        email = idinfo['email']
        name = idinfo.get('name', email.split('@')[0])
        
        # 2. Buscar si el usuario ya existe
        user = db.query(User).filter(User.email == email).first()
        
        if not user:
            # 3. Si no existe, crearlo (Registro Automático)
            # Usamos una contraseña aleatoria compleja ya que entrará por Google
            random_pass = ''.join(random.choices(string.ascii_letters + string.digits, k=32))
            user = User(
                email=email,
                name=name,
                password_hash=get_password_hash(random_pass),
                role='customer', # Por defecto son clientes
                is_active=True
            )
            db.add(user)
            db.commit()
            db.refresh(user)
            print(f"🆕 Nuevo usuario creado vía Google: {email}")

        # 4. Generar tokens de Shady's Nails
        token_data = {
            "sub": user.email,
            "user_id": user.id,
            "role": user.role
        }
        access_token = create_access_token(data=token_data)
        refresh_token = create_refresh_token(data=token_data)
        
        return {
            "access_token": access_token, 
            "refresh_token": refresh_token, 
            "token_type": "bearer"
        }

    except ValueError as e:
        # Token inválido
        print(f"❌ Error verificando token de Google: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Google Token"
        )
    except Exception as e:
        print(f"❌ Error inesperado en Google Auth: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")


