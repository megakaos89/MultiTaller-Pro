"""
Blueprint para reportes y exportaciones
"""

from flask import Blueprint, render_template, request, send_file, session
from datetime import datetime, timedelta
from models import db, Orden, Pieza, Cliente, Tecnico, Gasto, Configuracion
from routes.auth import login_required
import csv
from io import StringIO

reportes_bp = Blueprint('reportes', __name__)


@reportes_bp.route('/reportes')
@login_required
def menu_reportes():
    """Menú principal de reportes"""
    return render_template('reportes/menu.html')


@reportes_bp.route('/reporte/ingresos')
@login_required
def reporte_ingresos():
    """Reporte de ingresos por período"""
    periodo = request.args.get('periodo', 'mes')
    tipo_servicio = request.args.get('tipo_servicio', '')
    tecnico_id = request.args.get('tecnico_id', type=int)
    
    hoy = datetime.now(datetime.UTC)
    if periodo == 'hoy':
        fecha_inicio = hoy.replace(hour=0, minute=0, second=0, microsecond=0)
    elif periodo == 'semana':
        fecha_inicio = hoy - timedelta(days=hoy.weekday())
    elif periodo == 'mes':
        fecha_inicio = hoy.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    elif periodo == 'ano':
        fecha_inicio = hoy.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
    else:
        fecha_inicio = hoy - timedelta(days=30)
    
    # Obtener órdenes entregadas en el período
    consulta = Orden.query.filter(
        Orden.fecha_entrega_real >= fecha_inicio,
        Orden.fecha_entrega_real <= hoy,
        Orden.estado_general == 'Entregado'
    )
    
    if tipo_servicio:
        consulta = consulta.filter_by(tipo_servicio=tipo_servicio)
    
    if tecnico_id:
        consulta = consulta.filter_by(tecnico_id=tecnico_id)
    
    ordenes = consulta.all()
    
    # Agrupar por tipo de servicio
    ingresos_por_tipo = {}
    for orden in ordenes:
        tipo = orden.tipo_servicio or 'Sin clasificar'
        if tipo not in ingresos_por_tipo:
            ingresos_por_tipo[tipo] = {'cantidad': 0, 'total': 0}
        ingresos_por_tipo[tipo]['cantidad'] += 1
        ingresos_por_tipo[tipo]['total'] += orden.costo_total
    
    total_general = sum(o.costo_total for o in ordenes)
    
    tipos_servicio = ['Reparación', 'Mantenimiento preventivo', 'Instalación/Configuración', 
                     'Recuperación de datos', 'Limpieza', 'Diagnóstico', 'Otro']
    tecnicos = Tecnico.query.filter_by(activo=True).all()
    
    return render_template('reportes/ingresos.html',
                         ordenes=ordenes,
                         ingresos_por_tipo=ingresos_por_tipo,
                         total_general=total_general,
                         periodo=periodo,
                         tipo_servicio=tipo_servicio,
                         tecnico_id=tecnico_id,
                         tipos_servicio=tipos_servicio,
                         tecnicos=tecnicos)


@reportes_bp.route('/reporte/productividad')
@login_required
def reporte_productividad():
    """Reporte de productividad por técnico"""
    periodo = request.args.get('periodo', 'mes')
    
    hoy = datetime.now(datetime.UTC)
    if periodo == 'semana':
        fecha_inicio = hoy - timedelta(days=7)
    elif periodo == 'mes':
        fecha_inicio = hoy.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    elif periodo == 'ano':
        fecha_inicio = hoy.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
    else:
        fecha_inicio = hoy - timedelta(days=30)
    
    tecnicos = Tecnico.query.filter_by(activo=True).all()
    productividad_data = []
    
    for tecnico in tecnicos:
        ordenes_periodo = Orden.query.filter(
            Orden.tecnico_id == tecnico.id,
            Orden.fecha_creacion >= fecha_inicio,
            Orden.fecha_creacion <= hoy
        ).all()
        
        completadas = [o for o in ordenes_periodo if o.estado_general == 'Entregado']
        ingresos_generados = sum(o.costo_total for o in completadas)
        
        # Calcular tiempo promedio
        tiempos = []
        for o in completadas:
            if o.fecha_entrada and o.fecha_entrega_real:
                dias = (o.fecha_entrega_real - o.fecha_entrada).days
                tiempos.append(dias)
        
        promedio_dias = sum(tiempos) / len(tiempos) if tiempos else 0
        
        productividad_data.append({
            'tecnico': tecnico,
            'ordenes_totales': len(ordenes_periodo),
            'ordenes_completadas': len(completadas),
            'ingresos_generados': ingresos_generados,
            'promedio_dias': round(promedio_dias, 1)
        })
    
    productividad_data.sort(key=lambda x: x['ordenes_completadas'], reverse=True)
    
    return render_template('reportes/productividad.html',
                         productividad_data=productividad_data,
                         periodo=periodo)


@reportes_bp.route('/reporte/piezas-utilizadas')
@login_required
def reporte_piezas_utilizadas():
    """Reporte de piezas más utilizadas"""
    periodo = request.args.get('periodo', 'mes')
    
    hoy = datetime.now(datetime.UTC)
    if periodo == 'mes':
        fecha_inicio = hoy.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    elif periodo == 'ano':
        fecha_inicio = hoy.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
    else:
        fecha_inicio = hoy - timedelta(days=30)
    
    # Obtener todas las piezas usadas en órdenes del período
    from models import OrdenPieza, OrdenDispositivo, Orden
    
    ordenes_periodo = Orden.query.filter(
        Orden.fecha_creacion >= fecha_inicio,
        Orden.fecha_creacion <= hoy
    ).all()
    
    orden_ids = [o.id for o in ordenes_periodo]
    
    # Contar piezas usadas
    piezas_count = {}
    for od in OrdenDispositivo.query.filter(OrdenDispositivo.orden_id.in_(orden_ids)).all():
        for op in od.piezas_usadas:
            pieza_nombre = op.pieza.nombre if op.pieza else 'Sin nombre'
            if pieza_nombre not in piezas_count:
                piezas_count[pieza_nombre] = {'cantidad': 0, 'ingreso': 0}
            piezas_count[pieza_nombre]['cantidad'] += op.cantidad
            piezas_count[pieza_nombre]['ingreso'] += op.cantidad * op.precio_unitario
    
    # Ordenar por cantidad
    piezas_lista = [(nombre, datos) for nombre, datos in piezas_count.items()]
    piezas_lista.sort(key=lambda x: x[1]['cantidad'], reverse=True)
    
    return render_template('reportes/piezas_utilizadas.html',
                         piezas_lista=piezas_lista[:20],  # Top 20
                         periodo=periodo)


@reportes_bp.route('/reporte/fiscal')
@login_required
def reporte_fiscal():
    """Reporte fiscal con cálculo de tributos"""
    periodo = request.args.get('periodo', 'mes')
    
    hoy = datetime.now(datetime.UTC)
    if periodo == 'mes':
        fecha_inicio = hoy.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    elif periodo == 'ano':
        fecha_inicio = hoy.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
    else:
        fecha_inicio = hoy - timedelta(days=30)
    
    # Ingresos
    ordenes_periodo = Orden.query.filter(
        Orden.fecha_entrega_real >= fecha_inicio,
        Orden.fecha_entrega_real <= hoy,
        Orden.estado_general == 'Entregado'
    ).all()
    
    ingresos_brutos = sum(o.costo_total for o in ordenes_periodo)
    
    # Gastos operativos
    gastos_periodo = Gasto.query.filter(
        Gasto.fecha >= fecha_inicio,
        Gasto.fecha <= hoy
    ).all()
    
    gastos_operativos = sum(g.monto for g in gastos_periodo)
    
    # Costo piezas (estimado 40%)
    costo_piezas = ingresos_brutos * 0.4
    
    # Ganancia neta
    ganancia_neta = ingresos_brutos - costo_piezas - gastos_operativos
    
    # Tributos
    regimen = Configuracion.query.filter_by(clave='regimen_tributario').first()
    ss_percentage = Configuracion.query.filter_by(clave='seguridad_social_porcentaje').first()
    
    regimen_tipo = regimen.valor if regimen else 'general'
    ss_porcentaje = float(ss_percentage.valor) if ss_percentage else 5
    
    seguridad_social = ganancia_neta * (ss_porcentaje / 100) if ganancia_neta > 0 else 0
    
    isip_estimado = 0
    if regimen_tipo == 'general':
        import json
        tramos_conf = Configuracion.query.filter_by(clave='isip_tramos').first()
        if tramos_conf:
            tramos = json.loads(tramos_conf.valor)
            ganancia_restante = ganancia_neta
            for tramo in sorted(tramos, key=lambda x: x['hasta'] or float('inf')):
                limite = tramo['hasta'] if tramo['hasta'] else ganancia_neta
                if ganancia_restante > 0:
                    monto_tramo = min(ganancia_restante, limite)
                    isip_estimado += monto_tramo * (tramo['porcentaje'] / 100)
                    ganancia_restante -= monto_tramo
    else:
        cuota_fija_conf = Configuracion.query.filter_by(clave='cuota_fija_mensual').first()
        if cuota_fija_conf:
            isip_estimado = float(cuota_fija_conf.valor)
    
    total_tributos = isip_estimado + seguridad_social
    ganancia_final = ganancia_neta - total_tributos
    
    moneda_principal = Configuracion.query.filter_by(clave='moneda_principal').first()
    
    return render_template('reportes/fiscal.html',
                         ingresos_brutos=ingresos_brutos,
                         costo_piezas=costo_piezas,
                         gastos_operativos=gastos_operativos,
                         ganancia_neta=ganancia_neta,
                         isip_estimado=isip_estimado,
                         seguridad_social=seguridad_social,
                         total_tributos=total_tributos,
                         ganancia_final=ganancia_final,
                         periodo=periodo,
                         moneda=moneda_principal.valor if moneda_principal else 'CUP')


@reportes_bp.route('/exportar/<tipo>')
@login_required
def exportar_csv(tipo):
    """Exportar reportes a CSV"""
    output = StringIO()
    writer = csv.writer(output)
    
    if tipo == 'ordenes':
        writer.writerow(['Número Orden', 'Cliente', 'Tipo Servicio', 'Estado', 'Fecha Entrada', 'Total'])
        ordenes = Orden.query.limit(100).all()
        for o in ordenes:
            writer.writerow([
                o.numero_orden,
                o.cliente.nombre_completo if o.cliente else '',
                o.tipo_servicio,
                o.estado_general,
                o.fecha_entrada.strftime('%Y-%m-%d') if o.fecha_entrada else '',
                o.costo_total
            ])
    
    elif tipo == 'clientes':
        writer.writerow(['Nombre', 'Apellidos', 'Teléfono', 'Tipo Cliente', 'Dirección'])
        clientes = Cliente.query.limit(100).all()
        for c in clientes:
            writer.writerow([
                c.nombres,
                c.apellidos,
                c.telefono_movil or c.telefono_fijo,
                c.tipo_cliente,
                c.direccion
            ])
    
    elif tipo == 'piezas':
        writer.writerow(['Nombre', 'Categoría', 'Código', 'Cantidad', 'Precio Costo', 'Precio Venta'])
        piezas = Pieza.query.limit(100).all()
        for p in piezas:
            writer.writerow([
                p.nombre,
                p.categoria,
                p.codigo_interno,
                p.cantidad,
                p.precio_costo,
                p.precio_venta
            ])
    
    output.seek(0)
    
    return send_file(
        output,
        mimetype='text/csv',
        as_attachment=True,
        download_name=f'{tipo}_{datetime.now().strftime("%Y%m%d")}.csv'
    )
