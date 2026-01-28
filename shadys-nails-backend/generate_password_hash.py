"""
Script para generar hash de contraseña
"""
from app.utils.security import get_password_hash

password = "shadysnails2024"
hashed = get_password_hash(password)

print(f"Password: {password}")
print(f"Hash: {hashed}")
print("\nEjecuta este SQL en pgAdmin:")
print(f"UPDATE workers SET password_hash = '{hashed}' WHERE id = 1;")
