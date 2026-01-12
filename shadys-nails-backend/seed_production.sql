-- ═══════════════════════════════════════════════════════════════
-- SEED DATA PARA PRODUCCIÓN - SHADY'S NAILS
-- ═══════════════════════════════════════════════════════════════
-- Este script popula la base de datos con datos iniciales
-- Ejecutar en Render PostgreSQL después del deploy
-- ═══════════════════════════════════════════════════════════════

-- 1️⃣ WORKERS (Manicuristas)
-- ═══════════════════════════════════════════════════════════════
INSERT INTO workers (name, phone, email, business_name, state, password_hash, role, is_active)
VALUES 
    ('Gina Paola Martinez Barrera', '3003710184', 'gina.paola@shadysnails.com', 'Shady''s Nails', true, 
     '$2b$12$yKQc8kq9S0sKr6gpHXGiLefxDxkRGmya84MR4h5K544Di6XqyRZLi', 'admin', true)
ON CONFLICT (email) DO NOTHING;

-- 2️⃣ SERVICES (Servicios)
-- ═══════════════════════════════════════════════════════════════
INSERT INTO services (worker_id, name, duration_minutes, price, state)
VALUES 
    (1, 'Manicure Tradicional', 60, 25000, true),
    (1, 'Manicure Semipermanente', 90, 35000, true),
    (1, 'Manicure Gel', 120, 45000, true),
    (1, 'Acrílicas', 120, 50000, true),
    (1, 'Pedicure Tradicional', 60, 30000, true),
    (1, 'Pedicure Spa', 90, 40000, true),
    (1, 'Esmaltado Permanente', 45, 20000, true),
    (1, 'Retiro de Uñas', 30, 15000, true)
ON CONFLICT DO NOTHING;

-- 3️⃣ ADDITIONALS (Adicionales/Diseños)
-- ═══════════════════════════════════════════════════════════════
INSERT INTO additionals (name, extra_duration, price, state)
VALUES 
    ('Diseños Simples', 15, 3000, true),
    ('Diseños Complejos', 30, 5000, true),
    ('Diseños Premium', 45, 8000, true),
    ('Piedras y Accesorios', 20, 4000, true),
    ('French', 10, 2000, true)
ON CONFLICT DO NOTHING;

-- 4️⃣ CUSTOMERS (Clientes de Prueba)
-- ═══════════════════════════════════════════════════════════════
INSERT INTO customers (name, phone, email, notes)
VALUES 
    ('Ana García', '3001234567', 'ana.garcia@example.com', 'Cliente frecuente'),
    ('María López', '3009876543', 'maria.lopez@example.com', 'Prefiere diseños complejos'),
    ('Laura Martínez', '3005551234', 'laura.martinez@example.com', 'Alérgica a ciertos productos'),
    ('Carolina Rodríguez', '3007778888', 'carolina.rodriguez@example.com', 'VIP'),
    ('Valentina Sánchez', '3002223333', 'valentina.sanchez@example.com', 'Primera vez')
ON CONFLICT (email) DO NOTHING;

-- 5️⃣ USERS (Usuario Admin)
-- ═══════════════════════════════════════════════════════════════
-- Crear usuario admin basado en el worker
INSERT INTO users (email, password_hash, name, phone, role, is_active)
SELECT 
    email, 
    password_hash, 
    name, 
    phone, 
    'worker',
    is_active
FROM workers
WHERE email = 'gina.paola@shadysnails.com'
ON CONFLICT (email) DO NOTHING;

-- ═══════════════════════════════════════════════════════════════
-- VERIFICACIÓN
-- ═══════════════════════════════════════════════════════════════

-- Verificar workers
SELECT '✅ WORKERS:' as tabla, COUNT(*) as total FROM workers;
SELECT id, name, email, role FROM workers;

-- Verificar services
SELECT '✅ SERVICES:' as tabla, COUNT(*) as total FROM services;
SELECT id, name, price, duration_minutes FROM services ORDER BY id;

-- Verificar additionals
SELECT '✅ ADDITIONALS:' as tabla, COUNT(*) as total FROM additionals;
SELECT id, name, price, extra_duration FROM additionals ORDER BY id;

-- Verificar customers
SELECT '✅ CUSTOMERS:' as tabla, COUNT(*) as total FROM customers;
SELECT id, name, email FROM customers ORDER BY id;

-- Verificar users
SELECT '✅ USERS:' as tabla, COUNT(*) as total FROM users;
SELECT id, email, name, role FROM users;

-- ═══════════════════════════════════════════════════════════════
-- CREDENCIALES DE ACCESO
-- ═══════════════════════════════════════════════════════════════
-- Email: gina.paola@shadysnails.com
-- Password: shadysnails2024
-- Rol: admin/worker
-- ═══════════════════════════════════════════════════════════════
