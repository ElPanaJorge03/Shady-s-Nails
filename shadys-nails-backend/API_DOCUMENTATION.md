# Documentación de API - Shady's Nails

## Base URL
```
http://127.0.0.1:8000
```

---

## 📅 Appointments (Citas)

### POST /appointments/
Crea una nueva cita.

**Request Body:**
```json
{
  "worker_id": 1,
  "customer_id": 1,
  "service_id": 3,
  "additional_id": 1,
  "date": "2025-01-25",
  "start_time": "10:00:00",
  "notes": "Cliente VIP"
}
```

**Response (201 Created):**
```json
{
  "id": 1,
  "worker_id": 1,
  "customer_id": 1,
  "service_id": 3,
  "additional_id": 1,
  "date": "2025-01-25",
  "start_time": "10:00:00",
  "end_time": "12:30:00",
  "status": "confirmed",
  "notes": "Cliente VIP"
}
```

**Validaciones:**
- ✅ Worker, customer y service deben existir
- ✅ Fecha no puede ser en el pasado
- ✅ Hora de inicio: 9:00 AM - 8:59 PM
- ✅ Hora de fin: antes de 11:00 PM
- ✅ No puede haber conflictos de horario

**Errores:**
- `400` - Validación fallida (fecha pasada, horario inválido)
- `404` - Worker, customer o service no encontrado
- `409` - Conflicto de horario

---

### GET /appointments/
Lista todas las citas con filtros opcionales.

**Query Parameters:**
- `worker_id` (opcional) - Filtrar por worker
- `date` (opcional) - Filtrar por fecha (YYYY-MM-DD)

**Response (200 OK):**
```json
[
  {
    "id": 1,
    "worker_id": 1,
    "customer_id": 1,
    "service_id": 3,
    "additional_id": 1,
    "date": "2025-01-25",
    "start_time": "10:00:00",
    "end_time": "12:30:00",
    "status": "confirmed",
    "notes": "Cliente VIP"
  }
]
```

---

### GET /appointments/{appointment_id}
Obtiene una cita específica por ID.

**Response (200 OK):**
```json
{
  "id": 1,
  "worker_id": 1,
  "customer_id": 1,
  "service_id": 3,
  "additional_id": 1,
  "date": "2025-01-25",
  "start_time": "10:00:00",
  "end_time": "12:30:00",
  "status": "confirmed",
  "notes": "Cliente VIP"
}
```

**Errores:**
- `404` - Cita no encontrada

---

### PUT /appointments/{appointment_id}
Actualiza una cita existente.

**Request Body (todos los campos son opcionales):**
```json
{
  "worker_id": 1,
  "customer_id": 1,
  "service_id": 2,
  "additional_id": null,
  "date": "2025-01-26",
  "start_time": "14:00:00",
  "notes": "Cambio de horario",
  "status": "confirmed"
}
```

**Response (200 OK):**
```json
{
  "id": 1,
  "worker_id": 1,
  "customer_id": 1,
  "service_id": 2,
  "additional_id": null,
  "date": "2025-01-26",
  "start_time": "14:00:00",
  "end_time": "15:30:00",
  "status": "confirmed",
  "notes": "Cambio de horario"
}
```

**Validaciones:**
- ✅ No se puede editar cita cancelada o completada
- ✅ Mismas validaciones que POST si se cambian worker/service/fecha/hora

**Errores:**
- `400` - Cita cancelada/completada o validación fallida
- `404` - Cita, worker, customer o service no encontrado
- `409` - Conflicto de horario

---

### DELETE /appointments/{appointment_id}
Cancela una cita (soft delete).

**Response (200 OK):**
```json
{
  "message": "Cita cancelada exitosamente",
  "appointment_id": 1,
  "previous_status": "confirmed",
  "new_status": "cancelled"
}
```

**Errores:**
- `400` - Cita ya está cancelada
- `404` - Cita no encontrada

---

## 🕐 Availability (Disponibilidad)

### GET /availability
Consulta horarios disponibles para agendar.

**Query Parameters:**
- `worker_id` (requerido) - ID del worker
- `date` (requerido) - Fecha (YYYY-MM-DD)
- `service_id` (requerido) - ID del servicio
- `additional_id` (opcional) - ID del adicional

**Response (200 OK):**
```json
{
  "date": "2025-01-25",
  "worker_id": 1,
  "service_id": 3,
  "additional_id": 1,
  "total_duration_minutes": 150,
  "available_slots": [
    "09:00:00",
    "09:15:00",
    "09:30:00",
    "14:00:00",
    "20:30:00"
  ]
}
```

**Errores:**
- `404` - Service o additional no encontrado

---

## 💼 Services (Servicios)

### GET /services
Lista todos los servicios.

**Query Parameters:**
- `worker_id` (opcional) - Filtrar por worker
- `active_only` (opcional, default: true) - Solo servicios activos

**Response (200 OK):**
```json
[
  {
    "id": 1,
    "worker_id": 1,
    "name": "Acrílicas",
    "duration_minutes": 120,
    "price": 50000,
    "state": true
  }
]
```

---

## 👷 Workers (Manicuristas)

### GET /workers
Lista todos los workers.

**Query Parameters:**
- `active_only` (opcional, default: true) - Solo workers activos

**Response (200 OK):**
```json
[
  {
    "id": 1,
    "name": "Gina Paola Martinez Barrera",
    "phone": "3003710184",
    "email": "ginap.mb.martinez@gmail.com",
    "business_name": "Shady's Nails",
    "state": true
  }
]
```

---

## 👥 Customers (Clientes)

### GET /customers
Lista todos los clientes.

**Response (200 OK):**
```json
[
  {
    "id": 1,
    "name": "Ana María López",
    "phone": "3001234567",
    "email": "ana.lopez@email.com"
  }
]
```

---

## ✨ Additionals (Adicionales)

### GET /additionals
Lista todos los adicionales.

**Query Parameters:**
- `active_only` (opcional, default: true) - Solo adicionales activos

**Response (200 OK):**
```json
[
  {
    "id": 1,
    "name": "Diseños complejos",
    "extra_duration": 30,
    "price": 5000,
    "state": true
  }
]
```

---

## 🔢 Códigos de Estado HTTP

- `200 OK` - Solicitud exitosa
- `201 Created` - Recurso creado exitosamente
- `400 Bad Request` - Validación fallida o datos inválidos
- `404 Not Found` - Recurso no encontrado
- `409 Conflict` - Conflicto (ej: horario ocupado)
- `500 Internal Server Error` - Error del servidor

---

## 📝 Notas Importantes

1. **Fechas:** Formato `YYYY-MM-DD` (ej: `2025-01-25`)
2. **Horas:** Formato `HH:MM:SS` (ej: `14:30:00`)
3. **Horarios laborales:** 9:00 AM - 8:59 PM (inicio de cita)
4. **Hora máxima de fin:** 11:00 PM
5. **Slots de disponibilidad:** Cada 15 minutos
6. **Soft delete:** Las citas canceladas se mantienen en la BD
