# 📱 Guía de Instalación de Flutter en Windows

## ⚠️ Requisitos Previos

Antes de instalar Flutter, asegúrate de tener:
- Windows 10 o superior (64-bit)
- Espacio en disco: ~2.5 GB
- Git instalado
- Un editor de código (VS Code recomendado)

---

## 🚀 Paso 1: Descargar Flutter

1. Ve a: https://docs.flutter.dev/get-started/install/windows
2. Descarga el archivo ZIP de Flutter SDK
3. O descarga directamente desde: https://storage.googleapis.com/flutter_infra_release/releases/stable/windows/flutter_windows_3.16.0-stable.zip

---

## 📂 Paso 2: Extraer Flutter

1. Extrae el archivo ZIP en una ubicación permanente
   - **Recomendado:** `C:\src\flutter`
   - **NO extraer en:** `C:\Program Files\` (requiere permisos elevados)

2. La estructura debería verse así:
   ```
   C:\src\flutter\
   ├── bin\
   ├── packages\
   └── ...
   ```

---

## 🔧 Paso 3: Agregar Flutter al PATH

### Opción A: Manualmente (Recomendado)

1. Busca "Variables de entorno" en el menú de Windows
2. Click en "Variables de entorno..."
3. En "Variables del sistema", busca "Path"
4. Click en "Editar..."
5. Click en "Nuevo"
6. Agrega: `C:\src\flutter\bin`
7. Click en "Aceptar" en todas las ventanas

### Opción B: PowerShell (Temporal)
```powershell
$env:Path += ";C:\src\flutter\bin"
```

---

## ✅ Paso 4: Verificar Instalación

Abre una **nueva** terminal PowerShell y ejecuta:

```powershell
flutter doctor
```

Deberías ver algo como:
```
Doctor summary (to see all details, run flutter doctor -v):
[✓] Flutter (Channel stable, 3.16.0, on Microsoft Windows...)
[✗] Android toolchain - develop for Android devices
[✗] Chrome - develop for the web
[✓] Visual Studio - develop Windows apps
[!] Android Studio (not installed)
[✓] VS Code (version 1.85.0)
[✓] Connected device (1 available)
```

---

## 📱 Paso 5: Configurar para Android (Opcional pero Recomendado)

### Instalar Android Studio

1. Descarga Android Studio: https://developer.android.com/studio
2. Instala Android Studio
3. Abre Android Studio
4. Ve a: `Tools > SDK Manager`
5. Instala:
   - Android SDK Platform (API 33 o superior)
   - Android SDK Command-line Tools
   - Android SDK Build-Tools
   - Android Emulator

### Aceptar Licencias de Android

```powershell
flutter doctor --android-licenses
```

Presiona `y` para aceptar todas las licencias.

---

## 🌐 Paso 6: Configurar para Web (Opcional)

```powershell
flutter config --enable-web
```

---

## 🔍 Paso 7: Verificar Todo

```powershell
flutter doctor -v
```

Deberías ver checkmarks (✓) en:
- [✓] Flutter
- [✓] Android toolchain (si instalaste Android Studio)
- [✓] VS Code o Android Studio

---

## 🎯 Comandos Útiles

```powershell
# Ver versión de Flutter
flutter --version

# Actualizar Flutter
flutter upgrade

# Ver dispositivos disponibles
flutter devices

# Crear nuevo proyecto
flutter create nombre_proyecto

# Ejecutar app
flutter run
```

---

## 🐛 Solución de Problemas

### Error: "flutter no se reconoce como comando"
**Solución:** 
1. Verifica que agregaste Flutter al PATH correctamente
2. Cierra y abre una nueva terminal
3. Reinicia tu computadora si es necesario

### Error: "cmdline-tools component is missing"
**Solución:**
1. Abre Android Studio
2. `Tools > SDK Manager > SDK Tools`
3. Marca "Android SDK Command-line Tools"
4. Click "Apply"

### Error: "Unable to locate Android SDK"
**Solución:**
```powershell
flutter config --android-sdk "C:\Users\TuUsuario\AppData\Local\Android\Sdk"
```

---

## ✨ Siguiente Paso

Una vez que `flutter doctor` muestre al menos:
- [✓] Flutter
- [✓] Android toolchain (o Chrome para web)

Estarás listo para crear el proyecto de Shady's Nails.

---

## 📝 Notas Importantes

1. **Reinicia tu terminal** después de agregar Flutter al PATH
2. La primera vez que ejecutes `flutter doctor` puede tardar varios minutos
3. No necesitas tener TODO en verde, solo Flutter y al menos una plataforma (Android/Web)
4. Para desarrollo rápido, puedes usar Chrome (Web) sin instalar Android Studio

---

## 🚀 Alternativa Rápida: Flutter Web

Si quieres empezar rápido sin instalar Android Studio:

1. Instala Flutter (Pasos 1-4)
2. Habilita web:
   ```powershell
   flutter config --enable-web
   ```
3. Verifica que Chrome esté instalado
4. ¡Listo! Puedes desarrollar para web

---

**¿Prefieres instalar Flutter completo con Android o comenzar solo con Web?**
