"""
Blueprint para sistema de ayuda en línea
"""

from flask import Blueprint, render_template, request, flash, redirect, url_for
from routes.auth import login_required

ayuda_bp = Blueprint('ayuda', __name__)


@ayuda_bp.route('/ayuda')
@login_required
def index():
    """Página principal de ayuda"""
    return render_template('ayuda/index.html')


@ayuda_bp.route('/ayuda/<modulo>')
@login_required
def ayuda_modulo(modulo):
    """Ayuda específica por módulo"""
    modulos_ayuda = {
        'dashboard': {
            'titulo': 'Panel de Control',
            'contenido': '''
                <h3>Panel de Control (Dashboard)</h3>
                <p>El panel de control le muestra una vista general del estado actual de su taller.</p>
                
                <h4>Secciones principales:</h4>
                <ul>
                    <li><strong>Órdenes activas:</strong> Número total de órdenes que no han sido entregadas o canceladas.</li>
                    <li><strong>Pendientes de diagnóstico:</strong> Órdenes que están esperando ser diagnosticadas por el técnico.</li>
                    <li><strong>Listas para entregar:</strong> Órdenes completadas que esperan ser retiradas por el cliente.</li>
                    <li><strong>Piezas bajo stock:</strong> Lista de piezas cuya existencia está por debajo del mínimo configurado.</li>
                </ul>
                
                <h4>Próximos mantenimientos:</h4>
                <p>Muestra los contratos de mantenimiento cuya próxima fecha de servicio está dentro de la semana actual.</p>
                
                <h4>Garantías por vencer:</h4>
                <p>Lista las órdenes entregadas cuya garantía expirará en los próximos 15 días.</p>
                
                <h4>Panel financiero:</h4>
                <p>Muestra indicadores financieros del período seleccionado (ingresos, gastos, ganancia neta, tributos estimados).</p>
                
                <h4>Filtros de período:</h4>
                <p>Puede seleccionar diferentes períodos para ver los datos: Hoy, Semana, Mes, Año o personalizado.</p>
            '''
        },
        'clientes': {
            'titulo': 'Gestión de Clientes',
            'contenido': '''
                <h3>Gestión de Clientes</h3>
                <p>Este módulo le permite administrar la información de sus clientes.</p>
                
                <h4>Registrar nuevo cliente:</h4>
                <ol>
                    <li>Vaya a Clientes > Nuevo Cliente</li>
                    <li>Complete los campos obligatorios: Nombres, Apellidos</li>
                    <li>Opcionalmente agregue teléfonos, dirección y tipo de cliente</li>
                    <li>Haga clic en Guardar</li>
                </ol>
                
                <h4>Tipos de cliente:</h4>
                <ul>
                    <li><strong>Persona natural:</strong> Personas naturales</li>
                    <li><strong>Mipyme:</strong> Micro, pequeñas y medianas empresas</li>
                    <li><strong>Empresa estatal:</strong> Entidades estatales</li>
                    <li><strong>CPA:</strong> Cooperativas de Producción Agropecuaria</li>
                    <li><strong>CNA:</strong> Campesinos No Asociados</li>
                    <li><strong>PDL:</strong> Pequeños Detallistas</li>
                </ul>
                
                <h4>Buscar cliente:</h4>
                <p>Puede buscar clientes por nombre, apellidos o número de teléfono utilizando el campo de búsqueda en el listado.</p>
                
                <h4>Historial del cliente:</h4>
                <p>Al hacer clic en un cliente, podrá ver su historial completo de dispositivos y órdenes de servicio.</p>
            '''
        },
        'ordenes': {
            'titulo': 'Órdenes de Servicio',
            'contenido': '''
                <h3>Órdenes de Servicio</h3>
                <p>Las órdenes de servicio son el núcleo del sistema. Permiten gestionar las reparaciones y mantenimientos.</p>
                
                <h4>Crear nueva orden:</h4>
                <ol>
                    <li>Vaya a Órdenes > Nueva Orden</li>
                    <li>Seleccione el cliente</li>
                    <li>Agregue uno o varios dispositivos (multiequipo)</li>
                    <li>Para cada dispositivo, describa el problema reportado</li>
                    <li>Seleccione el tipo de servicio</li>
                    <li>Asigne un técnico (opcional)</li>
                    <li>Indique la garantía en meses (si aplica)</li>
                    <li>Agregue notas internas y para el cliente</li>
                </ol>
                
                <h4>Estados de la orden:</h4>
                <ul>
                    <li><strong>Recibido:</strong> Orden creada, equipo en taller</li>
                    <li><strong>En diagnóstico:</strong> Técnico evaluando el equipo</li>
                    <li><strong>Esperando piezas:</strong> Pendiente de llegada de repuestos</li>
                    <li><strong>En reparación:</strong> Trabajo técnico en curso</li>
                    <li><strong>Listo parcial:</strong> Algunos dispositivos listos</li>
                    <li><strong>Listo para entregar:</strong> Orden completa, lista para retiro</li>
                    <li><strong>Entregado:</strong> Equipo retirado por el cliente</li>
                    <li><strong>Cancelado:</strong> Orden cancelada</li>
                </ul>
                
                <h4>Agregar piezas:</h4>
                <p>Desde el detalle de la orden, puede agregar piezas utilizadas. El sistema descontará automáticamente del inventario (excepto en garantías).</p>
                
                <h4>Garantías y reingresos:</h4>
                <p>Si un cliente regresa con el mismo problema dentro del período de garantía, el sistema le alertará y permitirá marcar la orden como reingreso por garantía.</p>
            '''
        },
        'inventario': {
            'titulo': 'Inventario de Piezas',
            'contenido': '''
                <h3>Inventario de Piezas</h3>
                <p>Gestione el stock de piezas y consumibles de su taller.</p>
                
                <h4>Registrar nueva pieza:</h4>
                <ol>
                    <li>Vaya a Inventario > Nueva Pieza</li>
                    <li>Complete nombre, categoría y código interno</li>
                    <li>Defina la cantidad inicial y cantidad mínima</li>
                    <li>Establezca precio de costo y precio de venta</li>
                    <li>Seleccione el proveedor habitual</li>
                </ol>
                
                <h4>Categorías de piezas:</h4>
                <ul>
                    <li>Cartucho, Tóner, Cinta (para impresoras)</li>
                    <li>Fusor, Rodillo, Chip (componentes de impresora)</li>
                    <li>Placa electrónica, Cable</li>
                    <li>Batería, Disco, Memoria</li>
                    <li>Otro</li>
                </ul>
                
                <h4>Entradas y salidas:</h4>
                <p>Puede registrar entradas adicionales de piezas (compras) y salidas manuales (mermas, uso interno).</p>
                
                <h4>Compatibilidad:</h4>
                <p>Asocie piezas con modelos de equipos compatibles para facilitar la búsqueda al momento de reparar.</p>
                
                <h4>Alertas de stock:</h4>
                <p>El sistema resaltará en rojo las piezas cuya existencia esté por debajo del mínimo configurado.</p>
            '''
        },
        'reportes': {
            'titulo': 'Reportes',
            'contenido': '''
                <h3>Reportes y Exportaciones</h3>
                <p>Genere informes detallados sobre la operación de su taller.</p>
                
                <h4>Tipos de reportes disponibles:</h4>
                <ul>
                    <li><strong>Ingresos:</strong> Total facturado por período, desglosado por tipo de servicio.</li>
                    <li><strong>Productividad:</strong> Rendimiento por técnico (órdenes completadas, tiempo promedio).</li>
                    <li><strong>Piezas utilizadas:</strong> Ranking de las piezas más usadas en el período.</li>
                    <li><strong>Fiscal:</strong> Cálculo estimado de ISIP y Seguridad Social según régimen tributario.</li>
                </ul>
                
                <h4>Exportar a CSV:</h4>
                <p>Todos los reportes pueden exportarse a formato CSV para abrir en Excel u otras aplicaciones.</p>
                
                <h4>Filtros:</h4>
                <p>La mayoría de los reportes permiten filtrar por período (hoy, semana, mes, año) y otros criterios específicos.</p>
            '''
        },
        'licencias': {
            'titulo': 'Licencias',
            'contenido': '''
                <h3>Sistema de Licencias</h3>
                <p>MultiTaller requiere activación para continuar operando después del período de prueba.</p>
                
                <h4>Período de prueba:</h4>
                <p>Al instalar el sistema por primera vez, dispone de 15 días de uso completo sin necesidad de activación.</p>
                
                <h4>Activar el sistema:</h4>
                <ol>
                    <li>En la pantalla de activación, copie el ID de máquina que se muestra</li>
                    <li>Envíe este ID al vendedor junto con sus datos</li>
                    <li>Reciba el código de activación generado</li>
                    <li>Ingrese el código en el campo correspondiente</li>
                    <li>Haga clic en Activar</li>
                </ol>
                
                <h4>Tipos de licencia:</h4>
                <ul>
                    <li><strong>Estándar:</strong> 1 taller, 1 PC - 3500 CUP / 15 USD</li>
                    <li><strong>Ampliada:</strong> 2 PCs mismo taller - 6000 CUP / 25 USD</li>
                    <li><strong>Sucursales:</strong> Hasta 5 instalaciones - 12000 CUP / 50 USD</li>
                </ul>
                
                <h4>Contacto para licencias:</h4>
                <ul>
                    <li>Email: megashopsc20@gmail.com</li>
                    <li>Teléfono: +53 50625350</li>
                </ul>
            '''
        },
        'backup': {
            'titulo': 'Copia de Seguridad',
            'contenido': '''
                <h3>Copia de Seguridad y Restauración</h3>
                <p>Proteja la información de su taller realizando copias de seguridad periódicas.</p>
                
                <h4>Crear respaldo:</h4>
                <ol>
                    <li>Vaya a Configuración > Crear Respaldo</li>
                    <li>Seleccione la ubicación donde guardar (recomendado: memoria USB)</li>
                    <li>El sistema copiará la base de datos completa</li>
                    <li>Guarde el archivo en un lugar seguro</li>
                </ol>
                
                <h4>Restaurar respaldo:</h4>
                <ol>
                    <li>Vaya a Configuración > Restaurar Respaldo</li>
                    <li>Seleccione el archivo de respaldo previamente creado</li>
                    <li>Confirme la operación (se sobrescribirán todos los datos actuales)</li>
                    <li>El sistema se reiniciará con los datos restaurados</li>
                </ol>
                
                <h4>Recomendaciones:</h4>
                <ul>
                    <li>Realice copias de seguridad al menos una vez por semana</li>
                    <li>Guarde las copias en un dispositivo externo (USB)</li>
                    <li>Mantenga múltiples versiones de respaldos</li>
                    <li>Verifique periódicamente que los respaldos sean legibles</li>
                </ul>
            '''
        }
    }
    
    if modulo in modulos_ayuda:
        return render_template('ayuda/modulo.html', 
                             ayuda=modulos_ayuda[modulo],
                             modulo_actual=modulo)
    else:
        flash('Módulo de ayuda no encontrado', 'warning')
        return redirect(url_for('ayuda.index'))
