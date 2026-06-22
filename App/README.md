# MultiTaller - Aplicación Android Nativa

Este proyecto contiene todos los archivos necesarios para compilar la aplicación web MultiTaller como una aplicación nativa de Android utilizando un WebView.

## 📋 Requisitos Previos

Antes de comenzar, asegúrate de tener instalado lo siguiente:

### 1. Java Development Kit (JDK)
- **Versión requerida**: JDK 17 o superior
- **Descarga**: [Oracle JDK](https://www.oracle.com/java/technologies/downloads/) o [OpenJDK](https://openjdk.org/)
- **Verificar instalación**:
  ```bash
  java -version
  ```

### 2. Android Studio (Recomendado)
- **Descarga**: [Android Studio](https://developer.android.com/studio)
- Incluye Android SDK y todas las herramientas necesarias

### 3. Android SDK
Si no usas Android Studio, necesitas instalar el SDK por separado:
- **SDK Platform**: API Level 34 (Android 14)
- **Build Tools**: Versión 34.0.0
- **Platform Tools**: Última versión

### 4. Variables de Entorno
Configura las siguientes variables de entorno:

#### En Windows:
```cmd
set JAVA_HOME=C:\Program Files\Java\jdk-17
set ANDROID_HOME=C:\Users\TuUsuario\AppData\Local\Android\Sdk
set PATH=%PATH%;%ANDROID_HOME%\tools;%ANDROID_HOME%\platform-tools
```

#### En Linux/Mac:
```bash
export JAVA_HOME=/usr/lib/jvm/java-17-openjdk
export ANDROID_HOME=$HOME/Android/Sdk
export PATH=$PATH:$ANDROID_HOME/tools:$ANDROID_HOME/platform-tools
```

## 📁 Estructura del Proyecto

```
App/
├── app/
│   ├── build.gradle              # Configuración del módulo app
│   ├── proguard-rules.pro        # Reglas de ProGuard
│   └── src/main/
│       ├── AndroidManifest.xml   # Manifiesto de la aplicación
│       ├── java/com/multitaller/app/
│       │   └── MainActivity.java # Actividad principal (WebView)
│       ├── res/                  # Recursos de la aplicación
│       │   ├── drawable/         # Gráficos vectoriales
│       │   ├── layout/           # Diseños XML
│       │   ├── mipmap-*/         # Iconos de launcher
│       │   └── values/           # Colores, strings, temas
│       └── assets/               # Assets adicionales
├── gradle/
│   └── wrapper/
│       └── gradle-wrapper.properties
├── build.gradle                  # Configuración del proyecto
├── settings.gradle               # Configuración de ajustes
├── gradle.properties             # Propiedades de Gradle
├── gradlew                       # Script Gradle para Linux/Mac
└── README.md                     # Este archivo
```

## 🚀 Pasos para Compilar

### Opción 1: Usando Android Studio (Recomendado)

1. **Abrir el proyecto en Android Studio**
   ```
   File → Open → Seleccionar la carpeta "App"
   ```

2. **Esperar la sincronización de Gradle**
   - Android Studio descargará automáticamente las dependencias
   - Esto puede tomar varios minutos la primera vez

3. **Configurar el dispositivo de prueba**
   - Conecta un dispositivo Android vía USB con depuración activada
   - O crea un emulador: `Tools → Device Manager → Create Device`

4. **Compilar y ejecutar**
   - Haz clic en el botón ▶️ "Run"
   - O usa: `Shift + F10`

5. **Generar APK**
   - `Build → Build Bundle(s) / APK(s) → Build APK(s)`
   - El APK se generará en: `app/build/outputs/apk/debug/app-debug.apk`

### Opción 2: Usando Línea de Comandos

1. **Navegar a la carpeta del proyecto**
   ```bash
   cd App
   ```

2. **Dar permisos al script Gradle (Linux/Mac)**
   ```bash
   chmod +x gradlew
   ```

3. **Compilar el proyecto**
   ```bash
   # Para debug
   ./gradlew assembleDebug
   
   # Para release
   ./gradlew assembleRelease
   ```

4. **Encontrar el APK generado**
   ```bash
   # Debug
   app/build/outputs/apk/debug/app-debug.apk
   
   # Release
   app/build/outputs/apk/release/app-release-unsigned.apk
   ```

## 🔧 Configuración de la URL del Servidor

La aplicación está configurada por defecto para conectarse a un servidor Flask local:

```java
// En MainActivity.java, línea 44
webView.loadUrl("http://10.0.2.2:5000");
```

### URLs Especiales para Diferentes Entornos:

| Entorno | URL | Descripción |
|---------|-----|-------------|
| Emulador Android | `http://10.0.2.2:5000` | localhost del host |
| Dispositivo físico (misma red) | `http://192.168.X.X:5000` | IP de tu computadora |
| Servidor remoto | `https://tudominio.com` | URL de producción |

### Cambiar la URL:

1. Abre `app/src/main/java/com/multitaller/app/MainActivity.java`
2. Modifica la línea 44 con la URL deseada
3. Vuelve a compilar la aplicación

## 🌐 Configurar el Servidor Flask para Acceso Remoto

Para que la aplicación móvil se conecte a tu servidor Flask:

1. **Ejecutar Flask escuchando en todas las interfaces**:
   ```python
   # En app.py o donde inicies la app
   app.run(host='0.0.0.0', port=5000, debug=False)
   ```

2. **Permitir tráfico HTTP claro (si no usas HTTPS)**:
   - Ya está configurado en `AndroidManifest.xml` con `android:usesCleartextTraffic="true"`

3. **Configurar firewall**:
   ```bash
   # Linux
   sudo ufw allow 5000/tcp
   
   # Windows Firewall
   # Panel de Control → Firewall → Permitir aplicación → Python
   ```

4. **Obtener tu IP local**:
   ```bash
   # Windows
   ipconfig
   
   # Linux/Mac
   ifconfig o ip addr
   ```

5. **Actualizar la URL en MainActivity.java**:
   ```java
   webView.loadUrl("http://192.168.1.XX:5000");
   ```

## 📱 Firmar APK para Producción

Para distribuir tu aplicación:

1. **Generar keystore**:
   ```bash
   keytool -genkey -v -keystore multitaller.keystore -alias multitaller -keyalg RSA -keysize 2048 -validity 10000
   ```

2. **Configurar signing en build.gradle**:
   ```gradle
   android {
       ...
       signingConfigs {
           release {
               storeFile file('multitaller.keystore')
               storePassword 'tu_password'
               keyAlias 'multitaller'
               keyPassword 'tu_password'
           }
       }
       buildTypes {
           release {
               signingConfig signingConfigs.release
           }
       }
   }
   ```

3. **Compilar APK firmado**:
   ```bash
   ./gradlew assembleRelease
   ```

## 🐛 Solución de Problemas

### Error: "SDK not found"
```bash
# Crear o editar local.properties
echo "sdk.dir=/ruta/a/tu/Android/Sdk" > local.properties
```

### Error: "Java version mismatch"
- Asegúrate de usar JDK 17
- Verifica `JAVA_HOME` apunta a la instalación correcta

### Error: "Cleartext traffic not allowed"
- Ya está habilitado en el manifiesto
- Para producción, considera usar HTTPS

### La aplicación no se conecta al servidor
1. Verifica que el servidor Flask esté corriendo
2. Confirma que el firewall permite el puerto 5000
3. Usa la IP correcta según tu entorno (ver tabla arriba)
4. Asegúrate de que el dispositivo/emulador tenga acceso a la red

### Error de compilación con Gradle
```bash
# Limpiar proyecto
./gradlew clean

# Forzar descarga de dependencias
./gradlew build --refresh-dependencies
```

## 📄 Licencia

Este proyecto sigue la misma licencia que el proyecto MultiTaller original.

## 🤝 Soporte

Para problemas específicos de la aplicación Flask MultiTaller, consulta el README principal del proyecto.

Para problemas de compilación Android, revisa la [documentación oficial de Android](https://developer.android.com/docs).

---

**Nota**: Esta aplicación Android es un contenedor WebView para la aplicación web Flask MultiTaller. No modifica el código original de la aplicación web.
