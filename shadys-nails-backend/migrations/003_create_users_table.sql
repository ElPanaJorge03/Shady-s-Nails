-- Migración 003: Crear tabla de usuarios y asociar citas a usuarios

-- 1. Eliminar tabla users si existe (para empezar limpio)
DROP TABLE IF EXISTS users CASCADE;

-- 2. Crear tabla users
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    name VARCHAR(255) NOT NULL,
    phone VARCHAR(20),
    role VARCHAR(50) DEFAULT 'customer', -- 'customer' o 'worker'
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 3. Migrar workers existentes a users (solo los que tienen password_hash)
INSERT INTO users (email, password_hash, name, phone, role, created_at)
SELECT 
    email, 
    password_hash, 
    name, 
    phone, 
    'worker',
    CURRENT_TIMESTAMP
FROM workers
WHERE email IS NOT NULL 
  AND password_hash IS NOT NULL
  AND password_hash != ''
ON CONFLICT (email) DO NOTHING;

-- 4. Agregar columna user_id a appointments si no existe
DO $$ 
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'appointments' AND column_name = 'user_id'
    ) THEN
        ALTER TABLE appointments ADD COLUMN user_id INTEGER REFERENCES users(id);
    END IF;
END $$;

-- 5. Actualizar appointments existentes (asociar al primer worker/user)
UPDATE appointments 
SET user_id = (SELECT id FROM users WHERE role = 'worker' LIMIT 1)
WHERE user_id IS NULL;

-- 6. Crear índices para mejorar performance
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_users_role ON users(role);
CREATE INDEX IF NOT EXISTS idx_appointments_user_id ON appointments(user_id);

-- Verificación
SELECT 'Users creados:' as info, COUNT(*) as count FROM users;
SELECT 'Appointments con user_id:' as info, COUNT(*) as count FROM appointments WHERE user_id IS NOT NULL;
SELECT 'Usuarios por rol:' as info, role, COUNT(*) as count FROM users GROUP BY role;
