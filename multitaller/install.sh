#!/bin/bash
# Script de instalación para MultiTaller en Linux
# Requiere Python 3.8+ instalado

echo "============================================"
echo "  Instalador de MultiTaller"
echo "  Sistema de Gestión para Talleres"
echo "============================================"
echo ""

# Verificar si Python está instalado
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python3 no está instalado"
    echo "Por favor instale Python 3.8 o superior"
    exit 1
fi

echo "[1/4] Verificando Python... $(python3 --version)"
echo ""

# Crear entorno virtual si no existe
if [ ! -d "venv" ]; then
    echo "[2/4] Creando entorno virtual..."
    python3 -m venv venv
else
    echo "[2/4] Entorno virtual ya existe... OK"
fi
echo ""

# Activar entorno virtual e instalar dependencias
echo "[3/4] Instalando dependencias..."
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
echo ""

# Inicializar base de datos
echo "[4/4] Inicializando base de datos..."
python -c "from app import create_app; app = create_app(); print('Base de datos inicializada correctamente')"
echo ""

echo "============================================"
echo "  Instalación completada exitosamente!"
echo "============================================"
echo ""
echo "Para iniciar MultiTaller:"
echo "  1. Ejecute: ./start.sh"
echo "  2. Abra su navegador en: http://localhost:5000"
echo ""
echo "Credenciales por defecto:"
echo "  Usuario: admin"
echo "  Contraseña: admin123"
echo ""
echo "============================================"
