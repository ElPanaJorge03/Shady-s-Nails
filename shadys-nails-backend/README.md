# 💅 Shady's Nails - Backend API

Sistema de gestión de citas para salón de uñas. API REST construida con FastAPI y PostgreSQL.

## 📋 Descripción

Backend completo para la aplicación móvil de **Shady's Nails**, que permite:
- Gestión de citas (crear, listar, actualizar, cancelar)
- Consulta de disponibilidad en tiempo real
- Gestión de servicios, workers, clientes y adicionales
- Validaciones robustas de horarios y conflictos

## 🛠️ Tecnologías Utilizadas

- **FastAPI** - Framework web moderno y rápido
- **PostgreSQL** - Base de datos relacional
- **SQLAlchemy** - ORM para Python
- **Pydantic** - Validación de datos
- **Uvicorn** - Servidor ASGI

## 📦 Requisitos Previos

- Python 3.8+
- PostgreSQL 12+
- pip (gestor de paquetes de Python)

## 🚀 Instalación

### 1. Clonar el repositorio
```bash
git clone <url-del-repositorio>
cd shadys-nails-backend
```

### 2. Crear entorno virtual
```bash
python -m venv venv
```

### 3. Activar entorno virtual

**Windows:**
```bash
.\venv\Scripts\activate
```

**Linux/Mac:**
```bash
source venv/bin/activate
```

### 4. Instalar dependencias
```bash
pip install -r requirements.txt
```

### 5. Configurar base de datos

Crear base de datos en PostgreSQL:
```sql
CREATE DATABASE shadys_nails_db;
```

### 6. Configurar variables de entorno

Crear archivo `.env` en la raíz del proyecto:
```env
DATABASE_URL=postgresql://postgres:tu_password@localhost:5432/shadys_nails_db
```

### 7. Ejecutar el servidor
```bash
uvicorn app.main:app --reload
```

El servidor estará disponible en: **http://127.0.0.1:8000**

## 📚 Documentación de la API

Una vez que el servidor esté corriendo, accede a:
- **Swagger UI:** http://127.0.0.1:8000/docs
- **ReDoc:** http://127.0.0.1:8000/redoc

## 🔌 Endpoints Principales

### Appointments (Citas)
- `POST /appointments/` - Crear nueva cita
- `GET /appointments/` - Listar citas (con filtros)
- `GET /appointments/{id}` - Obtener cita específica
- `PUT /appointments/{id}` - Actualizar cita
- `DELETE /appointments/{id}` - Cancelar cita

### Availability (Disponibilidad)
- `GET /availability` - Consultar horarios disponibles

### Catálogos
- `GET /services` - Listar servicios
- `GET /workers` - Listar manicuristas
- `GET /customers` - Listar clientes
- `GET /additionals` - Listar adicionales

## 💡 Ejemplos de Uso

### Crear una cita
```bash
curl -X POST "http://127.0.0.1:8000/appointments/" \
  -H "Content-Type: application/json" \
  -d '{
    "worker_id": 1,
    "customer_id": 1,
    "service_id": 3,
    "additional_id": 1,
    "date": "2025-01-25",
    "start_time": "10:00:00",
    "notes": "Cliente VIP"
  }'
```

### Consultar disponibilidad
```bash
curl "http://127.0.0.1:8000/availability?worker_id=1&date=2025-01-25&service_id=3"
```

### Listar servicios
```bash
curl "http://127.0.0.1:8000/services"
```

## 🗂️ Estructura del Proyecto

```
shadys-nails-backend/
├── app/
│   ├── models/          # Modelos SQLAlchemy
│   │   ├── appointment.py
│   │   ├── worker.py
│   │   ├── customer.py
│   │   ├── service.py
│   │   └── additional.py
│   ├── routers/         # Endpoints de la API
│   │   ├── appointment.py
│   │   ├── availability.py
│   │   ├── service.py
│   │   ├── worker.py
│   │   ├── customer.py
│   │   └── additional.py
│   ├── schemas/         # Schemas Pydantic
│   ├── utils/           # Utilidades y validaciones
│   │   ├── appointment_validation.py
│   │   └── entity_validation.py
│   ├── database.py      # Configuración de BD
│   └── main.py          # Punto de entrada
├── venv/                # Entorno virtual
├── .env                 # Variables de entorno (no subir a git)
├── .gitignore
├── requirements.txt     # Dependencias
└── README.md
```

## ✨ Características

### Validaciones Automáticas
- ✅ Horarios laborales (9:00 AM - 8:59 PM inicio)
- ✅ Hora de fin máxima (11:00 PM)
- ✅ Detección de conflictos de horario
- ✅ Validación de existencia de entidades
- ✅ No permite citas en fechas pasadas
- ✅ Verificación de estado activo de servicios/workers

### Funcionalidades Avanzadas
- ✅ Cálculo automático de duración (servicio + adicionales)
- ✅ Slots de disponibilidad cada 15 minutos
- ✅ Soft delete (citas canceladas se mantienen en historial)
- ✅ Filtros por worker y fecha
- ✅ Documentación automática con Swagger
- ✅ **Notificaciones por email** (confirmación, actualización, cancelación)
- ✅ **Templates HTML personalizados** para emails
- ✅ **Modo simulación** para testing sin enviar emails reales

## 🔒 Seguridad

- Variables sensibles en archivo `.env`
- Validación de datos con Pydantic
- Manejo de errores con códigos HTTP apropiados
- Prevención de inyección SQL con SQLAlchemy ORM

## 🧪 Datos de Prueba

Para poblar la base de datos con datos iniciales, ejecuta:
```bash
psql -U postgres -d shadys_nails_db -f seed_data.sql
```

Esto creará:
- 1 worker (Gina Paola Martinez Barrera)
- 8 servicios con precios reales
- 3 adicionales (diseños)
- 5 clientes de prueba

## 🐛 Solución de Problemas

### Error: "No module named 'app'"
**Solución:** Asegúrate de ejecutar uvicorn desde la carpeta raíz del proyecto

### Error: "could not connect to server"
**Solución:** Verifica que PostgreSQL esté corriendo y las credenciales en `.env` sean correctas

### Error: "relation does not exist"
**Solución:** Las tablas se crean automáticamente al iniciar el servidor. Verifica que `create_all` se ejecute correctamente

## 📧 Notificaciones por Email

### Configuración de Email

El sistema envía notificaciones automáticas por email cuando:
- ✅ Se crea una nueva cita (confirmación)
- ✅ Se actualiza una cita (notificación de cambios)
- ✅ Se cancela una cita (aviso de cancelación)

### Configurar Gmail (Recomendado)

1. **Crear App Password** (no uses tu contraseña normal):
   - Ve a tu cuenta de Google: https://myaccount.google.com/security
   - Activa la verificación en 2 pasos si no la tienes
   - Ve a "App Passwords": https://myaccount.google.com/apppasswords
   - Selecciona "Mail" y "Windows Computer" (o el que prefieras)
   - Copia la contraseña de 16 caracteres generada

2. **Configurar en `.env`**:
```env
EMAIL_ENABLED=true
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=tu-email@gmail.com
SMTP_PASSWORD=xxxx-xxxx-xxxx-xxxx  # App Password de 16 caracteres
SENDER_NAME=Shady's Nails 💅
```

### Configurar Outlook/Hotmail

```env
EMAIL_ENABLED=true
SMTP_SERVER=smtp-mail.outlook.com
SMTP_PORT=587
SMTP_USER=tu-email@outlook.com
SMTP_PASSWORD=tu-contraseña
SENDER_NAME=Shady's Nails 💅
```

### Modo Simulación (Testing)

Si no configuras credenciales SMTP, los emails se simularán en la consola:

```env
# Dejar vacío para modo simulación
SMTP_USER=
SMTP_PASSWORD=
```

O deshabilitar completamente:

```env
EMAIL_ENABLED=false
```

### Probar el Sistema de Emails

Ejecuta el script de prueba:

```bash
python test_email_notifications.py
```

Este script probará:
- ✅ Creación de cita con email de confirmación
- ✅ Actualización de cita con email de notificación
- ✅ Cancelación de cita con email de aviso
- ✅ Validación de templates HTML

### Solución de Problemas de Email

**Error: "SMTPAuthenticationError"**
- Verifica que uses una App Password (Gmail) y no tu contraseña normal
- Asegúrate de que la verificación en 2 pasos esté activada (Gmail)

**Error: "Connection refused"**
- Verifica que `SMTP_SERVER` y `SMTP_PORT` sean correctos
- Revisa tu firewall/antivirus

**Los emails no llegan**
- Revisa la carpeta de spam
- Verifica que el email del cliente en la BD sea válido
- Revisa los logs del servidor para ver si hubo errores

**Modo simulación no funciona**
- Asegúrate de que `SMTP_USER` y `SMTP_PASSWORD` estén vacíos en `.env`
- O configura `EMAIL_ENABLED=false`

## 📝 Próximos Pasos

- [ ] Implementar autenticación JWT completa
- [x] ~~Sistema de notificaciones por email~~ ✅ **COMPLETADO**
- [ ] Implementar recordatorios automáticos (24h antes)
- [ ] Agregar tests unitarios
- [ ] Configurar CI/CD

## 👥 Autor

Desarrollado para **Shady's Nails** por Jorge

## 📄 Licencia

Este proyecto es privado y de uso exclusivo para Shady's Nails.
