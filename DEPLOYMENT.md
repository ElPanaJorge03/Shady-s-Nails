# 🚀 Guía de Despliegue - Shady's Nails

Esta guía detalla cómo subir la aplicación a un entorno de producción.

## 1. Preparación del Backend (FastAPI)

### Variables de Entorno
Asegúrate de configurar las siguientes variables en tu plataforma de hosting (Render, Railway, etc.):
- `DATABASE_URL`: La URL de tu base de datos PostgreSQL en la nube.
- `SECRET_KEY`: Una clave larga y aleatoria para los tokens JWT.
- `GOOGLE_CLIENT_ID`: Tu ID de Google Cloud.
- `EMAIL_ENABLED`: `true`
- `SMTP_USER`: Tu correo de envío (ej. Gmail).
- `SMTP_PASSWORD`: Tu contraseña de aplicación de Google.

### Hosting Recomendado
- **Railway.app** o **Render.com**: Ambos detectan automáticamente el archivo `requirements.txt` y permiten conectar una base de datos PostgreSQL fácilmente.

---

## 2. Base de Datos (PostgreSQL)

Si usas Render o Railway, puedes crear una base de datos administrada con un clic. 
Una vez creada, copia la **External Database URL** y pégala en la variable `DATABASE_URL` del backend.

---

## 3. Preparación del Frontend (Angular)

### Configuración de la API
Antes de compilar, asegúrate de que el archivo `src/environments/environment.prod.ts` tenga la URL real de tu backend:
```typescript
export const environment = {
  production: true,
  apiUrl: 'https://tu-backend.render.com'
};
```

### Compilación
Ejecuta:
```bash
npm run build --prod
```
Esto generará la carpeta `dist/shadys-nails-app`.

### Hosting Recomendado
- **Vercel** o **Netlify**: Simplemente conecta tu repositorio de GitHub y selecciona la carpeta del proyecto Angular.

---

## 4. Google Cloud Console
No olvides actualizar los **Orígenes de JavaScript autorizados** en tu consola de Google para incluir la URL final de producción (ej. `https://shadys-nails.vercel.app`).

---

¡Buena suerte con el lanzamiento! 💅✨
