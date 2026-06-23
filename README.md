# MultiTaller-Pro
Sistema Integral de Gestión para Taller de Reparación de Equipos Informáticos y Afines

## Resumen de cambios recientes

Se añadieron mejoras orientadas a seguridad y experiencia inicial:

- Pantalla de configuración inicial (/setup) que aparece si NO existe un usuario administrador. Desde allí se crea el usuario administrador y se configuran datos básicos del taller (nombre, dirección, teléfono y email).
- Soporte para variables de entorno mediante python-dotenv (.env). La aplicación carga multitaller/.env si existe.
- La creación automática del admin por defecto fue eliminada: ahora requiere ADMIN_PASSWORD en el entorno o la creación manual vía /setup.
- Imports internos ajustados a imports relativos (.models vs models) para ejecutar el paquete como módulo.
- .gitignore actualizado para ignorar archivos locales de licencia y BD de instancia.

---

## Requisitos previos

- Python 3.11+ recomendado
- pip

Opcional para despliegue: Docker (opcional) y systemd (Linux).

---

## Instalación local rápida

1. Clonar el repositorio y entrar en la carpeta del proyecto.
2. Crear y activar un entorno virtual:

   Windows (PowerShell):
   ```powershell
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1
   ```

   Linux/macOS:
   ```bash
   python -m venv .venv
   source .venv/bin/activate
   ```

3. Instalar dependencias:

   pip install -r multitaller/requirements.txt

---

## Variables de entorno

La app carga multitaller/.env si existe (python-dotenv). Variables relevantes:

- SECRET_KEY: clave para sesiones Flask (si no existe, se genera automáticamente en runtime).
- ADMIN_PASSWORD: contraseña para crear un usuario administrador al arrancar (si se desea creación automática).

Ejemplo de archivo multitaller/.env:

ADMIN_PASSWORD=UnaContraseñaSegura123

IMPORTANTE: No subir .env a git. El repositorio contiene .gitignore actualizado para ignorar archivos locales.

---

## Flujo de configuración inicial

Hay dos formas de crear el administrador:

1) Usar .env (ADMIN_PASSWORD): al iniciar la app, si no existe admin y ADMIN_PASSWORD está definido, la cuenta admin se crea automáticamente.

2) Usar la UI de primera ejecución: si no existe admin, la ruta raíz redirige a /setup. Allí se puede crear el usuario administrador (usuario y contraseña) y completar los datos del taller.

Recomendación: Usar la UI /setup en instalaciones nuevas y eliminar el archivo .env después de crear el usuario, o mantener .env fuera del control de versiones y con permisos seguros.

Para eliminar .env de forma segura tras crear admin:

- Borrar el archivo: `rm multitaller/.env` (Linux/macOS) o `del multitaller\.env` (Windows).
- Asegurarse de que ADMIN_PASSWORD no esté en variables de entorno compartidas.

---

## Ejecutar la aplicación

Desde la raíz del proyecto:

```bash
python multitaller/app.py
```

Abrir: http://localhost:5000

Si no existe administrador, se mostrará la pantalla de configuración inicial (/setup).

---

## Despliegue sugerido (opcional)

Docker (ejemplo rápido):

Dockerfile (ejemplo):

```
FROM python:3.11-slim
WORKDIR /app
COPY . /app
RUN pip install --no-cache-dir -r multitaller/requirements.txt
ENV FLASK_APP=multitaller/app.py
CMD ["python", "multitaller/app.py"]
```

systemd (ejemplo):

```
[Unit]
Description=MultiTaller-Pro Flask app
After=network.target

[Service]
User=www-data
WorkingDirectory=/path/to/repo
Environment=PYTHONUNBUFFERED=1
ExecStart=/path/to/repo/.venv/bin/python multitaller/app.py
Restart=on-failure

[Install]
WantedBy=multi-user.target
```

---

## Seguridad y buenas prácticas

- No committear contraseñas ni archivos .env en el repositorio.
- Usar contraseñas fuertes para ADMIN_PASSWORD y SECRET_KEY en producción.
- Proteger la carpeta de uploads y validar tipos/ tamaños de archivo (la app ya limita a 5MB y extensiones comunes).
- Mantener la base de datos de instancia fuera del control de versiones (ya está en .gitignore).

---

## Pruebas y verificación

1. Después de iniciar la app y crear el admin, ingresa con esas credenciales en /login.
2. Verifica que en Configuración (menu) aparecen los datos guardados.
3. Revisa que la ruta raíz redirige correctamente cuando hay admin y cuando no.

---

## Notas para desarrolladores

- Rutas nuevas: `multitaller/routes/setup.py` y plantilla `multitaller/templates/setup.html`.
- Se añadió `python-dotenv` en `multitaller/requirements.txt`.
- Se modificó `multitaller/app.py` para cargar .env y redirigir a /setup cuando no hay admin.

Si necesitas que agregue ejemplos de CI, Docker Compose, o un script para crear el admin desde la línea de comandos, indícalo y lo añado.
