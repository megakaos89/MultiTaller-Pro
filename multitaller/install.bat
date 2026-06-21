@echo off
REM Script de instalación para MultiTaller en Windows
REM Requiere Python 3.8+ instalado

echo ============================================
echo   Instalador de MultiTaller
echo   Sistema de Gestion para Talleres
echo ============================================
echo.

REM Verificar si Python esta instalado
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python no esta instalado o no esta en el PATH
    echo Por favor instale Python 3.8 o superior desde https://www.python.org
    pause
    exit /b 1
)

echo [1/4] Verificando Python... OK
echo.

REM Crear entorno virtual si no existe
if not exist "venv" (
    echo [2/4] Creando entorno virtual...
    python -m venv venv
) else (
    echo [2/4] Entorno virtual ya existe... OK
)
echo.

REM Activar entorno virtual e instalar dependencias
echo [3/4] Instalando dependencias...
call venv\Scripts\activate.bat
pip install --upgrade pip
pip install -r requirements.txt
echo.

REM Inicializar base de datos
echo [4/4] Inicializando base de datos...
python -c "from app import create_app; app = create_app(); print('Base de datos inicializada correctamente')"
echo.

echo ============================================
echo   Instalacion completada exitosamente!
echo ============================================
echo.
echo Para iniciar MultiTaller:
echo   1. Ejecute: start.bat
echo   2. Abra su navegador en: http://localhost:5000
echo.
echo Credenciales por defecto:
echo   Usuario: admin
echo   Contrasena: admin123
echo.
echo ============================================
pause
