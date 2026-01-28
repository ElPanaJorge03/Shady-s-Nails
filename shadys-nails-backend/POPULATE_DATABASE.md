# 📊 Poblar Base de Datos de Producción en Render

## Opción 1: Usando Render Dashboard (Recomendado)

### Paso 1: Acceder a la Base de Datos

1. Ve a Render Dashboard: https://dashboard.render.com
2. Haz clic en tu base de datos **PostgreSQL** (no el web service)
3. Ve a la pestaña **"Shell"** o **"Connect"**

### Paso 2: Conectar vía psql

Render te dará un comando similar a:
```bash
PGPASSWORD=tu_password psql -h dpg-xxxxx-a.oregon-postgres.render.com -U shadys_nails_user shadys_nails_prod
```

### Paso 3: Copiar y Pegar el Script

1. Abre el archivo `seed_production.sql`
2. **Copia TODO el contenido**
3. **Pégalo en el shell de psql** de Render
4. Presiona Enter

### Paso 4: Verificar

Deberías ver mensajes como:
```
✅ WORKERS: 1
✅ SERVICES: 8
✅ ADDITIONALS: 5
✅ CUSTOMERS: 5
✅ USERS: 1
```

---

## Opción 2: Usando Cliente Local (Alternativa)

Si tienes `psql` instalado localmente:

### Paso 1: Obtener Credenciales

En Render Dashboard → PostgreSQL → Info:
- **Host:** dpg-xxxxx-a.oregon-postgres.render.com
- **Database:** shadys_nails_prod
- **User:** shadys_nails_user
- **Password:** (copia el password)
- **Port:** 5432

### Paso 2: Conectar

```bash
psql -h dpg-xxxxx-a.oregon-postgres.render.com -U shadys_nails_user -d shadys_nails_prod -p 5432
```

Ingresa el password cuando te lo pida.

### Paso 3: Ejecutar Script

```bash
\i seed_production.sql
```

O copiar y pegar el contenido directamente.

---

## Opción 3: Usando DBeaver o pgAdmin (GUI)

### Paso 1: Crear Nueva Conexión

**Datos de conexión:**
- Host: (de Render)
- Port: 5432
- Database: shadys_nails_prod
- User: shadys_nails_user
- Password: (de Render)

### Paso 2: Ejecutar Script

1. Abre `seed_production.sql` en el editor SQL
2. Ejecuta todo el script
3. Verifica los resultados

---

## 📋 Datos que se Crearán

### Workers (1)
- **Gina Paola Martinez Barrera**
  - Email: gina.paola@shadysnails.com
  - Password: shadysnails2024
  - Rol: admin

### Services (8)
1. Manicure Tradicional - $25,000 (60 min)
2. Manicure Semipermanente - $35,000 (90 min)
3. Manicure Gel - $45,000 (120 min)
4. Acrílicas - $50,000 (120 min)
5. Pedicure Tradicional - $30,000 (60 min)
6. Pedicure Spa - $40,000 (90 min)
7. Esmaltado Permanente - $20,000 (45 min)
8. Retiro de Uñas - $15,000 (30 min)

### Additionals (5)
1. Diseños Simples - $3,000 (15 min)
2. Diseños Complejos - $5,000 (30 min)
3. Diseños Premium - $8,000 (45 min)
4. Piedras y Accesorios - $4,000 (20 min)
5. French - $2,000 (10 min)

### Customers (5)
- Ana García
- María López
- Laura Martínez
- Carolina Rodríguez
- Valentina Sánchez

### Users (1)
- Admin user vinculado a Gina Paola

---

## ✅ Verificación

Después de ejecutar el script, verifica en Swagger UI:

1. **GET /services** → Deberías ver 8 servicios
2. **GET /workers** → Deberías ver 1 worker
3. **GET /additionals** → Deberías ver 5 adicionales
4. **GET /customers** → Deberías ver 5 clientes

**Swagger URL:** https://shadys-nails-api.onrender.com/docs

---

## 🔐 Credenciales de Acceso

**Para login en la app:**
- **Email:** gina.paola@shadysnails.com
- **Password:** shadysnails2024
- **Rol:** admin/worker

⚠️ **Importante:** Cambia la contraseña después del primer login.

---

## 🐛 Solución de Problemas

### Error: "relation does not exist"
- Las tablas se crean automáticamente al iniciar el servidor
- Verifica que el servidor de Render esté corriendo

### Error: "duplicate key value"
- Los datos ya existen
- Usa `ON CONFLICT DO NOTHING` (ya incluido en el script)

### No puedo conectar a la base de datos
- Verifica que estés usando la URL **interna** de Render
- Verifica el password

---

## 📝 Siguiente Paso

Una vez poblada la base de datos:
✅ Continúa con el despliegue del frontend a Netlify
