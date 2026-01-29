"""
Utilidades de seguridad para autenticación
- Hashing de contraseñas con bcrypt
- Creación y verificación de JWT tokens
"""

from datetime import datetime, timedelta
from typing import Optional
import os
from dotenv import load_dotenv
from jose import JWTError, jwt
from passlib.context import CryptContext

load_dotenv()

# Configuración (usa variables de entorno para producción)
SECRET_KEY = os.getenv("SECRET_KEY")
if not SECRET_KEY:
    SECRET_KEY = "dev-secret-key-change-in-prod"  # fallback seguro para desarrollo
    print("WARNING: SECRET_KEY no está definido en el entorno. Usando fallback de desarrollo. Configúralo en producción.")

ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # 24 horas
REFRESH_TOKEN_EXPIRE_DAYS = 7
def create_refresh_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Crea un refresh token JWT
    Args:
        data: Datos a incluir en el token (ej: {"sub": "user@example.com"})
        expires_delta: Tiempo de expiración personalizado
    Returns:
        Token JWT como string
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire, "type": "refresh"})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def decode_refresh_token(token: str) -> Optional[dict]:
    """
    Decodifica y verifica un refresh token JWT
    Args:
        token: Token JWT a decodificar
    Returns:
        Payload del token si es válido y es refresh, None si no lo es
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        if payload.get("type") != "refresh":
            return None
        return payload
    except JWTError:
        return None

# Contexto para hashing de contraseñas
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verifica si una contraseña coincide con su hash
    
    Trunca la contraseña a 72 bytes para mantener consistencia con el hashing.
    """
    # Truncar a 72 bytes para mantener consistencia
    password_bytes = plain_password.encode('utf-8')[:72]
    password_truncated = password_bytes.decode('utf-8', errors='ignore')
    return pwd_context.verify(password_truncated, hashed_password)


def get_password_hash(password: str) -> str:
    """
    Genera el hash de una contraseña
    
    Bcrypt tiene un límite de 72 bytes, así que truncamos la contraseña
    si es necesario para evitar errores.
    """
    # Truncar a 72 bytes para cumplir con el límite de bcrypt
    password_bytes = password.encode('utf-8')[:72]
    password_truncated = password_bytes.decode('utf-8', errors='ignore')
    return pwd_context.hash(password_truncated)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Crea un JWT token
    
    Args:
        data: Datos a incluir en el token (ej: {"sub": "user@example.com"})
        expires_delta: Tiempo de expiración personalizado
    
    Returns:
        Token JWT como string
    """
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def decode_access_token(token: str) -> Optional[dict]:
    """
    Decodifica y verifica un JWT token
    
    Args:
        token: Token JWT a decodificar
    
    Returns:
        Payload del token si es válido, None si no lo es
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None
