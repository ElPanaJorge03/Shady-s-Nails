# 🔐 Configuración de Variables de Entorno en Render

## 📋 Pasos para Configurar

### 1. Acceder a la Configuración

1. Ve al dashboard de Render: https://dashboard.render.com
2. Haz clic en tu servicio **`shadys-nails-api`**
3. En el menú lateral izquierdo, haz clic en **"Environment"**
4. Haz clic en **"Add Environment Variable"**

---

## 🔑 Variables de Entorno a Configurar

### Variables de Seguridad

#### SECRET_KEY
**Valor:** `XbELQkVocarlaHs-Ko8yjm0kbiCLfi75q7U30XmxMzg`
- **Descripción:** Clave secreta para JWT y seguridad
- **Importante:** ⚠️ NO compartas esta clave públicamente

#### DEBUG
**Valor:** `False`
- **Descripción:** Desactiva modo debug en producción

---

### Variables de CORS

#### CORS_ORIGINS
**Valor:** `https://shadys-nails.netlify.app,http://localhost:4200`
- **Descripción:** Dominios permitidos para hacer peticiones al API
- **Nota:** Actualiza con tu dominio de Netlify cuando lo tengas

---

### Variables de Email (SMTP)

#### EMAIL_ENABLED
**Valor:** `true`

#### SMTP_SERVER
**Valor:** `smtp.gmail.com`

#### SMTP_PORT
**Valor:** `587`

#### SMTP_USER
**Valor:** `shadysnailsapp@gmail.com`

#### SMTP_PASSWORD
**Valor:** `ryebekfgtjyyhflt`
- **Importante:** ⚠️ Esta es tu App Password de Gmail

#### SENDER_NAME
**Valor:** `Shady's Nails 💅`

---

## ✅ Checklist de Configuración

Marca cada variable a medida que la agregues:

- [ ] SECRET_KEY
- [ ] DEBUG
- [ ] CORS_ORIGINS
- [ ] EMAIL_ENABLED
- [ ] SMTP_SERVER
- [ ] SMTP_PORT
- [ ] SMTP_USER
- [ ] SMTP_PASSWORD
- [ ] SENDER_NAME

---

## 🔄 Después de Configurar

1. **Guarda los cambios** - Render reiniciará automáticamente el servicio
2. **Espera 1-2 minutos** para que el servicio se reinicie
3. **Verifica que el servicio esté "Live"** (verde)

---

## 🧪 Verificar Configuración

### Probar el API

```bash
# Health check
curl https://shadys-nails-api.onrender.com/

# Debería responder:
# {"msg":"Shadys Nails API funcionando correctamente 💅"}
```

### Probar Swagger UI

Visita: https://shadys-nails-api.onrender.com/docs

Deberías ver la documentación interactiva de la API.

---

## ⚠️ Notas Importantes

### DATABASE_URL
- ✅ **Ya está configurada automáticamente** por Render
- No necesitas agregarla manualmente
- Render la conecta automáticamente con tu PostgreSQL

### Seguridad
- ⚠️ **NUNCA** compartas tu `SECRET_KEY` o `SMTP_PASSWORD` públicamente
- ⚠️ **NO** hagas commit de estas variables en Git
- ✅ Estas variables solo existen en Render (seguras)

---

## 📸 Captura de Pantalla de Referencia

Tu configuración debería verse así en Render:

```
Environment Variables
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

DATABASE_URL          postgresql://...  (Auto-generated)
SECRET_KEY            XbELQkVocar...    (Hidden)
DEBUG                 False
CORS_ORIGINS          https://shadys-nails.netlify.app,...
EMAIL_ENABLED         true
SMTP_SERVER           smtp.gmail.com
SMTP_PORT             587
SMTP_USER             shadysnailsapp@gmail.com
SMTP_PASSWORD         ****             (Hidden)
SENDER_NAME           Shady's Nails 💅
```

---

## 🆘 Solución de Problemas

### El servicio no reinicia
- Espera 2-3 minutos
- Refresca la página
- Verifica los logs en la pestaña "Logs"

### Error de CORS
- Verifica que `CORS_ORIGINS` incluya tu dominio de frontend
- Asegúrate de no tener espacios extra en el valor

### Emails no se envían
- Verifica que `SMTP_PASSWORD` sea la App Password correcta
- Revisa los logs para ver errores de SMTP

---

## ✅ Siguiente Paso

Una vez configuradas todas las variables:
1. ✅ Verifica que el servicio esté "Live"
2. ✅ Prueba el endpoint raíz
3. ✅ Continúa con el despliegue del frontend a Netlify
