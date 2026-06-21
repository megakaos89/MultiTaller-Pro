# MultiTaller - Sistema Integral de Gestión para Talleres

![Versión](https://img.shields.io/badge/versión-1.0.0-blue)
![Python](https://img.shields.io/badge/python-3.8+-green)
![Licencia](https://img.shields.io/badge/licencia-Comercial-orange)

## Descripción

**MultiTaller** es un sistema informático diseñado para automatizar la gestión de talleres independientes de reparación y mantenimiento de equipos informáticos y electrónicos afines: computadoras de escritorio, laptops, impresoras, máquinas de contar billetes, escáneres, monitores, UPS, y cualquier otro dispositivo que el taller atienda.

### Características principales

- ✅ **100% Offline** - Funciona sin conexión a Internet
- ✅ **Bajos recursos** - Compatible con equipos de 1-4 GB RAM
- ✅ **Multimoneda** - CUP principal, con equivalencias en MLC/USD/EUR
- ✅ **Sistema de licencias** - Activación offline para comercialización
- ✅ **Roles de usuario** - Administrador, Técnico, Recepcionista
- ✅ **Órdenes multiequipo** - Varios dispositivos por orden
- ✅ **Control de inventario** - Con alertas de stock mínimo
- ✅ **Gestión de garantías** - Seguimiento de reingresos
- ✅ **Contratos de mantenimiento** - Recordatorios automáticos
- ✅ **Reportes financieros** - Cálculo de tributos cubanos (ISIP, Seguridad Social)
- ✅ **Copia de seguridad** - Respaldo y restauración sencilla

## Requisitos del sistema

- **Sistema operativo**: Windows 7/10/11 o Linux (Nova, Ubuntu)
- **Procesador**: 1 GHz o superior
- **RAM**: 1 GB mínimo (2 GB recomendado)
- **Almacenamiento**: 500 MB libres
- **Python**: 3.8 o superior
- **Navegador**: Chrome, Firefox, Edge (cualquiera moderno)

## Instalación rápida

### En Windows

1. Descargue el código fuente
2. Ejecute `install.bat` como administrador
3. Espere a que complete la instalación
4. Ejecute `start.bat` para iniciar el sistema
5. Abra su navegador en `http://localhost:5000`

### En Linux

```bash
chmod +x install.sh start.sh
./install.sh
./start.sh
```

## Credenciales por defecto

| Usuario | Contraseña | Rol |
|---------|------------|-----|
| admin | admin123 | Administrador |

**⚠️ IMPORTANTE:** Cambie la contraseña por defecto inmediatamente después de la primera instalación.

## Módulos del sistema

### 📊 Panel de Control
Vista general del estado del taller con indicadores clave, próximas tareas y panel financiero.

### 📋 Órdenes de Servicio
- Creación de órdenes multiequipo
- Seguimiento de estados
- Asignación de técnicos
- Registro de piezas utilizadas
- Gestión de garantías y reingresos

### 👥 Clientes
- Registro de clientes (particulares, empresas, MIPYMES)
- Historial completo de servicios
- Búsqueda rápida por nombre/teléfono

### 💻 Dispositivos
- Catálogo de equipos de clientes
- Vinculación con modelos predefinidos
- Historial de reparaciones por dispositivo

### 🔩 Inventario
- Control de piezas y consumibles
- Alertas de stock mínimo
- Entradas y salidas
- Compatibilidad con modelos de equipos

### 📈 Reportes
- Ingresos por período
- Productividad por técnico
- Piezas más utilizadas
- Resumen fiscal (ISIP, Seguridad Social)
- Exportación a CSV

### ⚙️ Configuración
- Parámetros del taller
- Régimen tributario
- Tasas de cambio
- Monedas

## Sistema de Licencias

MultiTaller incluye un sistema de activación offline para su comercialización:

### Período de prueba
- 15 días de uso completo desde la primera ejecución
- Todas las funcionalidades disponibles

### Tipos de licencia

| Tipo | Instalaciones | Precio CUP | Precio USD |
|------|---------------|------------|------------|
| Estándar | 1 taller, 1 PC | 3,500 | 15 |
| Ampliada | 2 PCs mismo taller | 6,000 | 25 |
| Sucursales | Hasta 5 instalaciones | 12,000 | 50 |

### Proceso de activación

1. El sistema genera un **ID de máquina** único
2. El usuario envía este ID al vendedor
3. El vendedor genera el **código de activación** usando la copia maestra
4. El usuario introduce el código y el sistema se activa permanentemente

## Contacto y Soporte

- **Email:** megashopsc20@gmail.com
- **Teléfono:** +53 50625350

### Métodos de pago

- **Qbapay:** (configurable en el sistema)
- **Bitcoin (BTC):** (configurable en el sistema)
- **USDT (TRC20):** (configurable en el sistema)

## Estructura del proyecto

```
multitaller/
├── app.py                 # Aplicación principal
├── models.py              # Modelos de base de datos
├── routes/                # Controladores (blueprints)
│   ├── auth.py           # Autenticación
│   ├── dashboard.py      # Panel de control
│   ├── clientes.py       # Gestión de clientes
│   ├── ordenes.py        # Órdenes de servicio
│   ├── inventario.py     # Inventario de piezas
│   └── ...               # Otros módulos
├── templates/             # Plantillas HTML
├── static/               # Archivos estáticos
│   ├── css/             # Hojas de estilo
│   └── js/              # JavaScript
├── backup/              # Copias de seguridad
├── install.bat / .sh    # Scripts de instalación
└── README.md            # Este archivo
```

## Base de datos

MultiTaller utiliza **SQLite** como motor de base de datos, lo que permite:

- Archivo único (`multitaller.db`)
- Sin configuración adicional
- Copia de seguridad = copiar el archivo
- Fácil restauración

## Actualizaciones

Para actualizar el sistema:

1. Realice una copia de seguridad de `instance/multitaller.db`
2. Reemplace los archivos del sistema
3. Ejecute nuevamente `install.bat` o `install.sh`
4. Los datos se conservarán automáticamente

## Consideraciones para Cuba

Este sistema ha sido diseñado específicamente para las condiciones de Cuba:

- **Sin dependencia de Internet** - Todo funciona offline
- **Hardware modesto** - Funciona en PCs antiguas
- **Resistente a apagones** - Escrituras mínimas en disco
- **Moneda local** - CUP como moneda principal
- **Tributos locales** - ISIP y Seguridad Social configurados
- **Proveedores informales** - Campos flexibles de registro

## Licencia de uso

Este software es **comercial**. Su distribución no autorizada está prohibida.

Copyright © 2026 MultiTaller. Todos los derechos reservados.

---

*Desarrollado con ❤️ para los talleres cubanos*
