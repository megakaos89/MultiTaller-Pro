"""
Blueprint para gestión de órdenes de servicio
"""

from flask import Blueprint, render_template, redirect, url_for, flash, request, session, jsonify
from datetime import datetime, timedelta
from models import db, Orden, Cliente, Dispositivo, OrdenDispositivo, OrdenPieza, Pieza, Tecnico, OrdenHistorialEstado, OrdenNota
from routes.auth import login_required, role_required

ordenes_bp = Blueprint('ordenes', __name__)


@ordenes_bp.route('/ordenes')
@login_required
def listar_ordenes():
    """Listado de órdenes con filtros"""
    estado = request.args.get('estado', '')
    cliente_id = request.args.get('cliente_id', type=int)
    tecnico_id = request.args.get('tecnico_id', type=int)
    tipo_servicio = request.args.get('tipo_servicio', '')
    busqueda = request.args.get('busqueda', '')
    pagina = request.args.get('pagina', 1, type=int)
    
    consulta = Orden.query
    
    if estado:
        consulta = consulta.filter_by(estado_general=estado)
    
    if cliente_id:
        consulta = consulta.filter_by(cliente_id=cliente_id)
    
    if tecnico_id:
        consulta = consulta.filter_by(tecnico_id=tecnico_id)
    
    if tipo_servicio:
        consulta = consulta.filter_by(tipo_servicio=tipo_servicio)
    
    if busqueda:
        consulta = consulta.join(Cliente).filter(
            (Orden.numero_orden.ilike(f'%{busqueda}%')) |
            (Cliente.nombres.ilike(f'%{busqueda}%')) |
            (Cliente.apellidos.ilike(f'%{busqueda}%'))
        )
    
    ordenes = consulta.order_by(Orden.fecha_creacion.desc()).paginate(page=pagina, per_page=20)
    
    estados = ['Recibido', 'En diagnóstico', 'Esperando piezas', 'En reparación', 
               'Listo parcial', 'Listo para entregar', 'Entregado', 'Cancelado']
    tipos_servicio = ['Reparación', 'Mantenimiento preventivo', 'Instalación/Configuración', 
                     'Recuperación de datos', 'Limpieza', 'Diagnóstico', 'Presupuesto', 'Otro']
    clientes = Cliente.query.filter_by(activo=True).all()
    tecnicos = Tecnico.query.filter_by(activo=True).all()
    
    return render_template('ordenes/listar.html', 
                         ordenes=ordenes,
                         estados=estados,
                         tipos_servicio=tipos_servicio,
                         clientes=clientes,
                         tecnicos=tecnicos,
                         estado=estado,
                         cliente_id=cliente_id,
                         tecnico_id=tecnico_id,
                         tipo_servicio=tipo_servicio,
                         busqueda=busqueda)


@ordenes_bp.route('/orden/nueva', methods=['GET', 'POST'])
@login_required
def nueva_orden():
    """Crear nueva orden de servicio"""
    if request.method == 'POST':
        cliente_id = request.form.get('cliente_id', type=int)
        tipo_servicio = request.form.get('tipo_servicio', '')
        tecnico_id = request.form.get('tecnico_id', type=int)
        fecha_entrega_prevista = request.form.get('fecha_entrega_prevista')
        garantia_meses = request.form.get('garantia_meses', type=int, default=0)
        notas_internas = request.form.get('notas_internas', '').strip()
        notas_cliente = request.form.get('notas_cliente', '').strip()
        
        # IDs de dispositivos seleccionados
        dispositivo_ids = request.form.getlist('dispositivo_ids[]', type=int)
        problemas_reportados = request.form.getlist('problema_reportado[]', '')
        
        if not cliente_id or not dispositivo_ids:
            flash('Cliente y al menos un dispositivo son obligatorios', 'warning')
            return redirect(url_for('ordenes.nueva_orden'))
        
        # Generar número de orden
        ano = datetime.utcnow().year % 100
        ultima_orden = Orden.query.order_by(Orden.id.desc()).first()
        siguiente_numero = (ultima_orden.id + 1) if ultima_orden else 1
        numero_orden = f"OT-{ano:02d}-{siguiente_numero:04d}"
        
        # Crear orden
        orden = Orden(
            numero_orden=numero_orden,
            cliente_id=cliente_id,
            tipo_servicio=tipo_servicio,
            tecnico_id=tecnico_id if tecnico_id else None,
            fecha_entrega_prevista=datetime.fromisoformat(fecha_entrega_prevista) if fecha_entrega_prevista else None,
            garantia_meses=garantia_meses,
            notas_internas=notas_internas,
            notas_cliente=notas_cliente,
            estado_general='Recibido'
        )
        
        db.session.add(orden)
        db.session.flush()  # Para obtener el ID
        
        # Agregar dispositivos a la orden
        for i, disp_id in enumerate(dispositivo_ids):
            if disp_id:
                orden_disp = OrdenDispositivo(
                    orden_id=orden.id,
                    dispositivo_id=disp_id,
                    problema_reportado=problemas_reportados[i] if i < len(problemas_reportados) else '',
                    estado_individual='Recibido'
                )
                db.session.add(orden_disp)
        
        # Registrar en historial
        historial = OrdenHistorialEstado(
            orden_id=orden.id,
            estado_anterior=None,
            estado_nuevo='Recibido',
            usuario_id=session['usuario_id'],
            observaciones='Orden creada'
        )
        db.session.add(historial)
        
        db.session.commit()
        flash(f'Orden {numero_orden} creada correctamente', 'success')
        return redirect(url_for('ordenes.ver_orden', id=orden.id))
    
    clientes = Cliente.query.filter_by(activo=True).all()
    tecnicos = Tecnico.query.filter_by(activo=True).all()
    
    return render_template('ordenes/formulario.html', 
                         orden=None,
                         clientes=clientes,
                         tecnicos=tecnicos)


@ordenes_bp.route('/orden/<int:id>')
@login_required
def ver_orden(id):
    """Ver detalle de orden"""
    orden = Orden = db.session.get(Orden, id)
    if not Orden:
        flash('Registro no encontrado', 'danger')
        return redirect(url_for('index'))
    dispositivos_orden = OrdenDispositivo.query.filter_by(orden_id=id).all()
    historial = OrdenHistorialEstado.query.filter_by(orden_id=id).order_by(OrdenHistorialEstado.fecha_cambio.desc()).all()
    notas = OrdenNota.query.filter_by(orden_id=id).order_by(OrdenNota.fecha_creacion.desc()).all()
    
    estados = ['Recibido', 'En diagnóstico', 'Esperando piezas', 'En reparación', 
               'Listo parcial', 'Listo para entregar', 'Entregado', 'Cancelado']
    
    return render_template('ordenes/detalle.html', 
                         orden=orden,
                         dispositivos_orden=dispositivos_orden,
                         historial=historial,
                         notas=notas,
                         estados=estados)


@ordenes_bp.route('/orden/<int:id>/editar', methods=['GET', 'POST'])
@login_required
def editar_orden(id):
    """Editar orden existente"""
    orden = Orden = db.session.get(Orden, id)
    if not Orden:
        flash('Registro no encontrado', 'danger')
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        orden.tipo_servicio = request.form.get('tipo_servicio', '')
        orden.tecnico_id = request.form.get('tecnico_id', type=int)
        orden.fecha_entrega_prevista = datetime.fromisoformat(request.form.get('fecha_entrega_prevista')) if request.form.get('fecha_entrega_prevista') else None
        orden.garantia_meses = request.form.get('garantia_meses', type=int, default=0)
        orden.notas_internas = request.form.get('notas_internas', '').strip()
        orden.notas_cliente = request.form.get('notas_cliente', '').strip()
        
        # Calcular fecha fin garantía si se entrega
        if orden.estado_general == 'Entregado' and orden.garantia_meses > 0 and not orden.fecha_fin_garantia:
            orden.fecha_fin_garantia = datetime.utcnow() + timedelta(days=orden.garantia_meses * 30)
        
        db.session.commit()
        flash('Orden actualizada correctamente', 'success')
        return redirect(url_for('ordenes.ver_orden', id=orden.id))
    
    tecnicos = Tecnico.query.filter_by(activo=True).all()
    
    return render_template('ordenes/formulario.html', 
                         orden=orden,
                         tecnicos=tecnicos,
                         editando=True)


@ordenes_bp.route('/orden/<int:id>/actualizar_estado', methods=['POST'])
@login_required
def actualizar_estado(id):
    """Actualizar estado de la orden"""
    orden = Orden = db.session.get(Orden, id)
    if not Orden:
        flash('Registro no encontrado', 'danger')
        return redirect(url_for('index'))
    nuevo_estado = request.form.get('nuevo_estado', '')
    observaciones = request.form.get('observaciones', '').strip()
    
    if not nuevo_estado:
        flash('Estado es requerido', 'warning')
        return redirect(url_for('ordenes.ver_orden', id=orden.id))
    
    estado_anterior = orden.estado_general
    orden.estado_general = nuevo_estado
    
    # Si se entrega, registrar fecha
    if nuevo_estado == 'Entregado' and not orden.fecha_entrega_real:
        orden.fecha_entrega_real = datetime.utcnow()
        if orden.garantia_meses > 0:
            orden.fecha_fin_garantia = orden.fecha_entrega_real + timedelta(days=orden.garantia_meses * 30)
    
    # Registrar en historial
    historial = OrdenHistorialEstado(
        orden_id=orden.id,
        estado_anterior=estado_anterior,
        estado_nuevo=nuevo_estado,
        usuario_id=session['usuario_id'],
        observaciones=observaciones
    )
    db.session.add(historial)
    db.session.commit()
    
    flash('Estado actualizado correctamente', 'success')
    return redirect(url_for('ordenes.ver_orden', id=orden.id))


@ordenes_bp.route('/orden/<int:id>/agregar_nota', methods=['POST'])
@login_required
def agregar_nota(id):
    """Agregar nota interna a la orden"""
    orden = Orden = db.session.get(Orden, id)
    if not Orden:
        flash('Registro no encontrado', 'danger')
        return redirect(url_for('index'))
    contenido = request.form.get('contenido', '').strip()
    
    if not contenido:
        flash('La nota no puede estar vacía', 'warning')
        return redirect(url_for('ordenes.ver_orden', id=orden.id))
    
    nota = OrdenNota(
        orden_id=orden.id,
        contenido=contenido,
        usuario_id=session['usuario_id']
    )
    db.session.add(nota)
    db.session.commit()
    
    flash('Nota agregada correctamente', 'success')
    return redirect(url_for('ordenes.ver_orden', id=orden.id))


@ordenes_bp.route('/orden/<int:id>/eliminar')
@login_required
@role_required('admin')
def eliminar_orden(id):
    """Eliminar orden (solo admin)"""
    orden = Orden = db.session.get(Orden, id)
    if not Orden:
        flash('Registro no encontrado', 'danger')
        return redirect(url_for('index'))
    
    # Verificar si está entregada
    if orden.estado_general == 'Entregado':
        flash('No se puede eliminar una orden entregada', 'warning')
        return redirect(url_for('ordenes.listar_ordenes'))
    
    db.session.delete(orden)
    db.session.commit()
    flash('Orden eliminada correctamente', 'success')
    return redirect(url_for('ordenes.listar_ordenes'))


@ordenes_bp.route('/orden/<int:orden_id>/dispositivo/<int:disp_id>/agregar_pieza', methods=['POST'])
@login_required
def agregar_pieza_a_orden(orden_id, disp_id):
    """Agregar pieza a un dispositivo de la orden"""
    orden_dispositivo = OrdenDispositivo.query.filter_by(
        orden_id=orden_id, 
        dispositivo_id=disp_id
    ).first_or_404()
    
    pieza_id = request.form.get('pieza_id', type=int)
    cantidad = request.form.get('cantidad', type=int, default=1)
    precio_unitario = request.form.get('precio_unitario', type=float)
    es_garantia = request.form.get('es_garantia') == 'on'
    
    if not pieza_id or not precio_unitario:
        flash('Pieza y precio son requeridos', 'warning')
        return redirect(url_for('ordenes.ver_orden', id=orden_id))
    
    pieza = db.session.get(Pieza, pieza_id)
    if not pieza:
        flash('Pieza no encontrada', 'danger')
        return redirect(url_for('ordenes.ver_orden', id=orden_id))
    
    # Verificar stock si no es garantía
    if not es_garantia and pieza.cantidad < cantidad:
        flash(f'Stock insuficiente. Disponible: {pieza.cantidad}', 'warning')
        return redirect(url_for('ordenes.ver_orden', id=orden_id))
    
    # Agregar pieza a la orden
    orden_pieza = OrdenPieza(
        orden_dispositivo_id=orden_dispositivo.id,
        pieza_id=pieza_id,
        cantidad=cantidad,
        precio_unitario=precio_unitario,
        es_garantia=es_garantia
    )
    db.session.add(orden_pieza)
    
    # Descontar del inventario si no es garantía
    if not es_garantia:
        pieza.cantidad -= cantidad
        pieza.fecha_actualizacion = datetime.utcnow()
    
    # Recalcular costo total de la orden
    recalcular_costo_orden(orden_dispositivo.orden)
    
    db.session.commit()
    flash('Pieza agregada correctamente', 'success')
    return redirect(url_for('ordenes.ver_orden', id=orden_id))


def recalcular_costo_orden(orden):
    """Recalcula el costo total de una orden"""
    dispositivos_orden = OrdenDispositivo.query.filter_by(orden_id=orden.id).all()
    
    costo_piezas = 0
    for od in dispositivos_orden:
        for op in od.piezas_usadas:
            total = op.cantidad * op.precio_unitario * (1 - op.descuento_aplicado / 100)
            costo_piezas += total
    
    orden.costo_total = orden.mano_obra_costo + costo_piezas


@ordenes_bp.route('/api/piezas/disponibles')
@login_required
def api_piezas_disponibles():
    """API para obtener piezas disponibles"""
    termino = request.args.get('q', '')
    
    consulta = Pieza.query.filter(Pieza.cantidad > 0)
    
    if termino:
        consulta = consulta.filter(
            (Pieza.nombre.ilike(f'%{termino}%')) |
            (Pieza.codigo_interno.ilike(f'%{termino}%'))
        )
    
    piezas = consulta.limit(20).all()
    
    resultados = []
    for p in piezas:
        resultados.append({
            'id': p.id,
            'texto': f"{p.nombre} (Stock: {p.cantidad})",
            'precio_venta': p.precio_venta,
            'stock': p.cantidad
        })
    
    return jsonify(resultados)
