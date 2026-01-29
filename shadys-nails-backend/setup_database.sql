-- Script para crear la base de datos de Shady's Nails
-- Ejecutar este script con psql o pgAdmin

-- Crear la base de datos
CREATE DATABASE shadys_nails_db
    WITH 
    OWNER = postgres
    ENCODING = 'UTF8'
    LC_COLLATE = 'Spanish_Spain.1252'
    LC_CTYPE = 'Spanish_Spain.1252'
    TABLESPACE = pg_default
    CONNECTION LIMIT = -1;

-- Conectar a la base de datos
\c shadys_nails_db

-- Mensaje de confirmación
SELECT 'Base de datos shadys_nails_db creada exitosamente!' as mensaje;
