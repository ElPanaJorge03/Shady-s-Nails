from typing import List, Optional

def require_roles(roles: List[str]):
    """
    Dependency para requerir uno o varios roles específicos en una ruta.
    Uso: Depends(require_roles(["admin"]))
    """
    def role_checker(current_user: User = Depends(get_current_user)):
        if current_user.role not in roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"No tienes permisos para acceder a este recurso. Rol requerido: {roles}"
            )
        return current_user
    return role_checker
"""
Dependencies compartidas para autenticación
"""
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from sqlalchemy import select

from app.database import get_db
from app.models.user import User
from app.utils.security import decode_access_token

# OAuth2 scheme para extraer el token del header
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> User:
    """
    Dependency para obtener el usuario actual desde el token JWT
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    # Decodificar token
    payload = decode_access_token(token)
    if payload is None:
        raise credentials_exception
    
    email: str = payload.get("sub")
    user_id: int = payload.get("user_id")
    
    if email is None:
        raise credentials_exception
    
    # Buscar usuario en la base de datos
    statement = select(User).where(User.email == email)
    result = db.execute(statement)
    user = result.scalar_one_or_none()
    
    if user is None:
        raise credentials_exception
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user"
        )
    
    return user
