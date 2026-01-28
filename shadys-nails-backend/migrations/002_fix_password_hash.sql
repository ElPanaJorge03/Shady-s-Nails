-- Actualizar password hash COMPLETO para Gina Paola
-- Password: shadysnails2024

UPDATE workers 
SET password_hash = '$2b$12$yKQc8kq9S0sKr6gpHXGiLefxDxkRGmya84MR4h5K544Di6XqyRZLi'
WHERE id = 1;

-- Verificar
SELECT id, name, email, role, LENGTH(password_hash) as hash_length FROM workers WHERE id = 1;
