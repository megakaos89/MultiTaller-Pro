# Actualización de Interfaz Visual - MultiTaller

## Resumen
Esta actualización transforma la apariencia visual del sistema MultiTaller para que luzca moderna, limpia y profesional, siguiendo tendencias actuales de diseño (2025-2026), manteniendo la simplicidad y usabilidad en equipos de bajos recursos.

## Archivos Modificados/Creados

### Nuevos Archivos
1. `/static/css/custom.css` - Estilos modernos completos con temas claro/oscuro
2. `/static/js/app.js` - JavaScript para modo oscuro, sidebar colapsable y animaciones
3. `/static/css/bootstrap-icons.css` - CSS para íconos de Bootstrap

### Archivos Modificados
1. `/templates/base.html` - Nueva estructura con sidebar, topbar y menú moderno
2. `/templates/dashboard/index.html` - Dashboard rediseñado con tarjetas modernas

## Instrucciones de Instalación

### Paso 1: Copiar archivos CSS y JS
Los archivos `custom.css`, `app.js` y `bootstrap-icons.css` ya han sido creados en sus respectivas ubicaciones.

### Paso 2: Descargar Fuentes (IMPORTANTE)

Las fuentes deben descargarse y colocarse en `/static/fonts/`:

#### Fuente Inter (Google Fonts)
Descargar los siguientes archivos de https://github.com/rsms/inter/releases:
- `Inter-Regular.woff2` (peso 400)
- `Inter-Medium.woff2` (peso 500)
- `Inter-SemiBold.woff2` (peso 600)
- `Inter-Bold.woff2` (peso 700)

Colocarlos en: `/multitaller/static/fonts/`

#### Bootstrap Icons
Descargar el archivo `bootstrap-icons.woff2` de:
https://github.com/twbs/icons/blob/main/font/fonts/bootstrap-icons.woff2

O usar el CDN local alternativo descargando el kit completo de:
https://icons.getbootstrap.com/

Colocarlo en: `/multitaller/static/fonts/`

### Paso 3: Verificar la estructura de directorios

La estructura final debe ser:
```
multitaller/
├── static/
│   ├── css/
│   │   ├── bootstrap.min.css     (existente)
│   │   ├── custom.css            (nuevo)
│   │   ├── bootstrap-icons.css   (nuevo)
│   │   └── style.css             (puede eliminarse o mantenerse como backup)
│   ├── js/
│   │   ├── bootstrap.bundle.min.js  (existente)
│   │   ├── app.js                   (nuevo)
│   │   └── main.js                  (puede eliminarse o mantenerse como backup)
│   └── fonts/
│       ├── Inter-Regular.woff2      (descargar)
│       ├── Inter-Medium.woff2       (descargar)
│       ├── Inter-SemiBold.woff2     (descargar)
│       ├── Inter-Bold.woff2         (descargar)
│       └── bootstrap-icons.woff2    (descargar)
└── templates/
    ├── base.html                    (modificado)
    └── dashboard/
        └── index.html               (modificado)
```

### Paso 4: Reiniciar la aplicación

Detener y volver a iniciar MultiTaller:
```bash
# En Linux/Mac
cd /path/to/multitaller
./start.sh

# En Windows
cd C:\path\to\multitaller
start.bat
```

### Paso 5: Limpiar caché del navegador

Después de iniciar sesión:
1. Presionar Ctrl+F5 (Windows/Linux) o Cmd+Shift+R (Mac)
2. O limpiar completamente la caché del navegador

## Características Nuevas

### 1. Modo Oscuro
- Botón sol/luna en la barra superior
- Preferencia guardada en localStorage
- Respeta la preferencia del sistema operativo

### 2. Sidebar Colapsable
- Botón hamburguesa para colapsar/expandir
- Modo mini muestra solo íconos
- Estado guardado en localStorage
- Responsive: se oculta completamente en móviles

### 3. Diseño Moderno
- Paleta de colores: azul medianoche (#1e3a5f), cian vibrante (#00b4d8)
- Bordes redondeados (8px)
- Sombras sutiles para profundidad
- Transiciones suaves (0.2s-0.3s)

### 4. Tipografía Inter
- Fuente moderna y legible
- Pesos semibold para encabezados
- Mejor legibilidad en tablets

### 5. Dashboard Mejorado
- Tarjetas elevadas con iconos
- Animaciones de entrada (fadeInUp)
- Badges de estado con colores suaves
- Lista de mantenimientos con indicador de urgencia

## Solución de Problemas

### Las fuentes no se muestran
Verificar que los archivos .woff2 estén en `/static/fonts/` y que las rutas en `custom.css` sean correctas.

### Los íconos no aparecen
Asegurarse de que `bootstrap-icons.woff2` esté descargado y que `bootstrap-icons.css` esté vinculado en el HTML.

### El modo oscuro no funciona
Verificar que el navegador soporte localStorage y que JavaScript esté habilitado.

### El sidebar no se colapsa en móviles
En pantallas menores a 768px, el sidebar se comporta diferente (se desliza desde la izquierda).

## Notas Importantes

1. **Sin dependencias externas**: Todos los recursos son locales, el sistema funciona 100% offline.

2. **Compatibilidad**: Se mantiene Bootstrap 5, solo se sobrescriben estilos con CSS custom.

3. **Rendimiento**: Las animaciones son CSS puro, sin JavaScript pesado.

4. **Responsive**: Funciona desde 1024×768 hasta tablets y pantallas táctiles.

5. **Textos en español**: Todos los textos permanecen en español.

## Revertir Cambios

Si necesita volver al diseño anterior:
1. Restaurar `base.html` desde backup
2. Restaurar `dashboard/index.html` desde backup
3. Eliminar o renombrar `custom.css` y `app.js`
4. Volver a vincular `style.css` y `main.js` en las plantillas

## Soporte

Para problemas o preguntas sobre esta actualización, consultar la documentación de MultiTaller o contactar al equipo de desarrollo.
