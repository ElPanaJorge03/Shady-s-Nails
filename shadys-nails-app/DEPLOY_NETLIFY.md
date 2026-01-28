# 🚀 Desplegar Frontend a Netlify - Guía Paso a Paso

## ✅ Build Completado

El build de producción se completó exitosamente:
- **Ubicación:** `dist/shadys-nails-app/browser`
- **Configuración:** `netlify.toml` creado
- **API URL:** https://shadys-nails-api.onrender.com

---

## 📋 Opciones de Despliegue

### Opción 1: Netlify CLI (Más Rápido) ⚡

#### Paso 1: Instalar Netlify CLI
```bash
npm install -g netlify-cli
```

#### Paso 2: Login
```bash
netlify login
```
Se abrirá el navegador para autenticarte.

#### Paso 3: Deploy
```bash
cd shadys-nails-app
netlify deploy --prod
```

Cuando pregunte:
- **Publish directory:** `dist/shadys-nails-app/browser`
- Confirma el deploy

---

### Opción 2: Netlify Dashboard (Manual) 🖱️

#### Paso 1: Ir a Netlify
1. Ve a: https://app.netlify.com
2. Inicia sesión (o crea cuenta con GitHub/Email)

#### Paso 2: Deploy Manual
1. Haz clic en **"Add new site"** → **"Deploy manually"**
2. Arrastra la carpeta `dist/shadys-nails-app/browser` a la zona de drop
3. Espera a que termine el deploy (1-2 minutos)

#### Paso 3: Obtener URL
- Netlify te dará una URL como: `https://random-name-123.netlify.app`
- Puedes cambiar el nombre en **Site settings** → **Change site name**

---

### Opción 3: GitHub Integration (Continuous Deployment) 🔄

#### Paso 1: Push a GitHub
```bash
git add .
git commit -m "feat: Add Netlify configuration"
git push
```

#### Paso 2: Conectar en Netlify
1. En Netlify: **Add new site** → **Import an existing project**
2. Conecta con GitHub
3. Selecciona el repositorio `Shady-s-Nails`
4. Configura:
   - **Base directory:** `shadys-nails-app`
   - **Build command:** `npm run build`
   - **Publish directory:** `dist/shadys-nails-app/browser`
5. Click **Deploy site**

---

## 🧪 Verificación Post-Despliegue

### 1. Acceder a la App
Visita la URL de Netlify (ej: `https://shadys-nails.netlify.app`)

### 2. Probar Funcionalidades
- ✅ Página de inicio carga
- ✅ Servicios se muestran (desde Render API)
- ✅ Navegación funciona
- ✅ Login/Register funciona
- ✅ Booking flow completo

### 3. Revisar Console
Abre DevTools (F12) → Console:
- ❌ No debe haber errores CORS
- ✅ API calls deben ser exitosos

---

## 🔧 Configuración Adicional

### Cambiar Nombre del Sitio
1. En Netlify Dashboard → **Site settings**
2. **Change site name**
3. Ejemplo: `shadys-nails` → `https://shadys-nails.netlify.app`

### Dominio Personalizado (Opcional)
1. **Site settings** → **Domain management**
2. **Add custom domain**
3. Sigue las instrucciones para configurar DNS

### Variables de Entorno (Si necesitas)
1. **Site settings** → **Environment variables**
2. Agrega variables si es necesario

---

## 🐛 Solución de Problemas

### Error: "Page not found" en rutas
- **Causa:** Falta configuración de redirects
- **Solución:** Verifica que `netlify.toml` esté en la raíz del proyecto

### Error CORS
- **Causa:** Backend no permite el dominio de Netlify
- **Solución:** Actualiza `CORS_ORIGINS` en Render:
  ```
  CORS_ORIGINS=https://tu-sitio.netlify.app,http://localhost:4200
  ```

### Build falla en Netlify
- **Causa:** Dependencias faltantes
- **Solución:** Verifica `package.json` y `package-lock.json` estén en Git

### App no carga datos
- **Causa:** API URL incorrecta
- **Solución:** Verifica `environment.prod.ts` tenga la URL correcta de Render

---

## 📊 Siguiente Paso

Una vez desplegado:
1. ✅ Prueba la app en la URL de Netlify
2. ✅ Verifica integración con backend
3. ✅ Comparte la URL para testing

---

## 🎯 URLs Finales

**Backend (Render):**
- API: https://shadys-nails-api.onrender.com
- Docs: https://shadys-nails-api.onrender.com/docs

**Frontend (Netlify):**
- App: https://[tu-sitio].netlify.app (después del deploy)

---

¿Qué opción prefieres usar para el deploy?
1. **CLI** (más rápido, requiere instalar)
2. **Manual** (más fácil, drag & drop)
3. **GitHub** (automático, mejor para CI/CD)
