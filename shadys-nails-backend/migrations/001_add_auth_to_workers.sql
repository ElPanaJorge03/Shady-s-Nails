-- Migración: Agregar autenticación a workers
-- Fecha: 2025-12-16

-- 1. Agregar columnas necesarias para autenticación
ALTER TABLE workers ADD COLUMN IF NOT EXISTS email VARCHAR(255) UNIQUE;
ALTER TABLE workers ADD COLUMN IF NOT EXISTS password_hash VARCHAR(255);
ALTER TABLE workers ADD COLUMN IF NOT EXISTS role VARCHAR(20) DEFAULT 'worker';
ALTER TABLE workers ADD COLUMN IF NOT EXISTS is_active BOOLEAN DEFAULT TRUE;

-- 2. Actualizar el worker existente (Gina Paola) con credenciales
-- Password por defecto: "shadysnails2024" (cambiar después del primer login)
UPDATE workers 
SET 
    email = 'gina.paola@shadysnails.com',
    password_hash = '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYfQaI3QqK2', -- shadysnails2024
    role = 'admin',
    is_active = TRUE
WHERE id = 1;

-- 3. Verificar los cambios
SELECT id, name, email, role, is_active FROM workers;
