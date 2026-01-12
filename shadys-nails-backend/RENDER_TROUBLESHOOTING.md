# 🔧 Troubleshooting Render Deployment

## Problemas Comunes y Soluciones

### 1. Error de Base de Datos
**Síntoma:** `could not connect to server` o `relation does not exist`

**Solución:**
- Asegúrate de que la base de datos PostgreSQL esté creada en Render
- Verifica que `DATABASE_URL` esté configurada en las variables de entorno
- Usa la URL **interna** de la base de datos, no la externa

### 2. Error de Dependencias
**Síntoma:** `ModuleNotFoundError` o `No module named 'xxx'`

**Solución:**
- Verifica que `requirements.txt` esté completo
- Asegúrate de que todas las dependencias estén listadas

### 3. Error de Puerto
**Síntoma:** `Address already in use` o `Failed to bind`

**Solución:**
- Verifica que el Procfile use `$PORT` (variable de Render)
- Comando correcto: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`

### 4. Error de Variables de Entorno
**Síntoma:** `KeyError` o valores None en configuración

**Solución:**
- Verifica que todas las variables estén configuradas en Render
- Variables críticas:
  - `DATABASE_URL`
  - `SECRET_KEY`
  - `CORS_ORIGINS`

### 5. Error de Python Version
**Síntoma:** `Python version not supported`

**Solución:**
- Crear archivo `runtime.txt` con: `python-3.11.0`

---

## Checklist de Verificación

- [ ] Base de datos PostgreSQL creada en Render
- [ ] DATABASE_URL configurada (URL interna)
- [ ] Todas las variables de entorno configuradas
- [ ] Procfile existe y es correcto
- [ ] requirements.txt completo
- [ ] Python version especificada (runtime.txt)

---

## Próximos Pasos

1. Revisa los logs de Render
2. Identifica el error específico
3. Aplica la solución correspondiente
4. Redeploy el servicio
