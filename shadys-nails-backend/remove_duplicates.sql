-- Script para eliminar servicios duplicados
-- Mantiene solo el registro con el ID más bajo de cada servicio duplicado

-- Ver servicios duplicados primero
SELECT name, COUNT(*) as cantidad
FROM services
GROUP BY name
HAVING COUNT(*) > 1;

-- Eliminar duplicados (mantiene el de menor ID)
DELETE FROM services
WHERE id NOT IN (
    SELECT MIN(id)
    FROM services
    GROUP BY name, worker_id, duration_minutes, price
);

-- Verificar que quedaron 8 servicios únicos
SELECT * FROM services ORDER BY id;
