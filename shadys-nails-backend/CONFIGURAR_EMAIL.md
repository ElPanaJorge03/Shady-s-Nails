# 📧 Guía Rápida: Configurar Emails en Shady's Nails

## ⚡ Configuración Rápida (5 minutos)

### Paso 1: Crear App Password de Gmail

1. Ve a: https://myaccount.google.com/apppasswords
2. Inicia sesión con tu cuenta de Gmail
3. Selecciona "Mail" y "Windows Computer"
4. Copia la contraseña de 16 caracteres (ejemplo: `abcd efgh ijkl mnop`)

### Paso 2: Configurar `.env`

Crea o edita el archivo `.env` en la raíz del backend:

```env
# Copia estas líneas y reemplaza con tus datos
EMAIL_ENABLED=true
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=tu-email@gmail.com
SMTP_PASSWORD=abcd-efgh-ijkl-mnop
SENDER_NAME=Shady's Nails 💅
```

### Paso 3: Probar

1. **Inicia el servidor:**
   ```bash
   cd shadys-nails-backend
   .\venv\Scripts\activate
   uvicorn app.main:app --reload
   ```

2. **Crea una cita de prueba** (usando Swagger UI o la app):
   - Ve a: http://127.0.0.1:8000/docs
   - POST `/appointments/`
   - Usa un cliente con email válido

3. **Revisa tu email** - Deberías recibir la confirmación

---

## 🧪 Modo Simulación (Sin configurar email)

Si no quieres configurar email todavía, déjalo así en `.env`:

```env
SMTP_USER=
SMTP_PASSWORD=
```

Los emails se mostrarán en la consola del servidor:
```
📧 [SIMULACIÓN EMAIL] Para: cliente@example.com | Asunto: 💅 Confirmación de tu cita
```

---

## ✅ Qué Emails se Envían

| Acción | Email | Template |
|--------|-------|----------|
| Crear cita | ✅ Confirmación | Rosa 💅 |
| Actualizar cita | ✅ Notificación de cambios | Azul 📝 |
| Cancelar cita | ✅ Aviso de cancelación | Rojo 🚫 |

---

## 🐛 Solución de Problemas

**"SMTPAuthenticationError"**
→ Usa App Password, no tu contraseña normal de Gmail

**"Connection refused"**
→ Verifica firewall/antivirus

**Email no llega**
→ Revisa spam, verifica que el email del cliente sea válido

---

## 📝 Siguiente Paso

Una vez configurado, los emails se enviarán **automáticamente** en cada operación de cita. No necesitas hacer nada más! 🎉
