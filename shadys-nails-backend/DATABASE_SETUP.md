# 🗄️ Configuración de PostgreSQL para Shady's Nails

## Pasos para configurar la base de datos:

### 1️⃣ Verificar instalación de PostgreSQL

Abre PowerShell y verifica que PostgreSQL esté instalado:

```powershell
psql --version
```

### 2️⃣ Crear la base de datos

**Opción A - Usando psql (línea de comandos):**

```powershell
# Conectar a PostgreSQL como usuario postgres
psql -U postgres

# Dentro de psql, ejecutar:
CREATE DATABASE shadys_nails_db WITH ENCODING 'UTF8';

# Salir de psql
\q
```

**Opción B - Usando el script SQL:**

```powershell
psql -U postgres -f setup_database.sql
```

**Opción C - Usando pgAdmin (interfaz gráfica):**

1. Abre pgAdmin
2. Conecta al servidor PostgreSQL
3. Click derecho en "Databases" → "Create" → "Database"
4. Nombre: `shadys_nails_db`
5. Encoding: `UTF8`
6. Click "Save"

### 3️⃣ Configurar credenciales

Edita el archivo `.env` con tus credenciales de PostgreSQL:

```env
DATABASE_URL=postgresql://postgres:TU_CONTRASEÑA@localhost:5432/shadys_nails_db
SECRET_KEY=tu-clave-secreta-super-segura-cambiala-en-produccion-123456789
```

**Reemplaza `TU_CONTRASEÑA` con la contraseña que configuraste al instalar PostgreSQL.**

### 4️⃣ Verificar conexión

```powershell
# Desde el directorio shadys-nails-backend
venv\Scripts\python.exe test_db.py
```

Si ves "Connected!" y "Result: 1", ¡todo está bien! 🎉

### 5️⃣ Iniciar el servidor

```powershell
venv\Scripts\python.exe -m uvicorn app.main:app --reload
```

El servidor creará automáticamente todas las tablas necesarias (users, customers, workers, services, appointments, etc.)

---

## 🔧 Solución de problemas

### Error: "password authentication failed"
- Verifica que la contraseña en `.env` sea correcta
- Intenta conectarte manualmente: `psql -U postgres`

### Error: "database does not exist"
- Ejecuta el paso 2 para crear la base de datos

### Error: "could not connect to server"
- Verifica que PostgreSQL esté corriendo:
  ```powershell
  # Ver servicios de Windows
  Get-Service -Name postgresql*
  
  # Si no está corriendo, iniciarlo
  Start-Service postgresql-x64-XX  # Reemplaza XX con tu versión
  ```

### Error de encoding UTF-8
- Ya está configurado en el código para manejar esto correctamente
- Asegúrate de que la base de datos se creó con encoding UTF8

---

## 📊 Estructura de la base de datos

Una vez que inicies el backend, se crearán automáticamente estas tablas:

- **users** - Usuarios del sistema (autenticación)
- **customers** - Clientes
- **workers** - Manicuristas
- **services** - Servicios disponibles
- **additionals** - Servicios adicionales
- **appointments** - Citas agendadas

¡No necesitas crear las tablas manualmente! SQLAlchemy lo hace por ti. 🚀
