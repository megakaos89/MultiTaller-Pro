"""
Blueprint para gestión de inventario de piezas
"""

from flask import Blueprint, render_template, redirect, url_for, flash, request, session, jsonify
from datetime import datetime, timezone
from models import db, Pieza, Proveedor, MovimientoInventario, PiezaCompatible, ModeloEquipo
from routes.auth import login_required, role_required

inventario_bp = Blueprint('inventario', __name__)


@inventario_bp.route('/inventario')
@login_required
def listar_piezas():
    """Listado de piezas de inventario"""
    busqueda = request.args.get('busqueda', '')
    categoria = request.args.get('categoria', '')
    bajo_stock = request.args.get('bajo_stock', '')
    pagina = request.args.get('pagina', 1, type=int)
    
    consulta = Pieza.query
    
    if busqueda:
        consulta = consulta.filter(
            (Pieza.nombre.ilike(f'%{busqueda}%')) |
            (Pieza.codigo_interno.ilike(f'%{busqueda}%'))
        )
    
    if categoria:
        consulta = consulta.filter_by(categoria=categoria)
    
    if bajo_stock == '1':
        consulta = consulta.filter(Pieza.cantidad <= Pieza.cantidad_minima)
    
    piezas = consulta.order_by(Pieza.nombre).paginate(page=pagina, per_page=20)
    
    categorias = ['Cartucho', 'Tóner', 'Cinta', 'Fusor', 'Rodillo', 'Chip', 
                 'Placa electrónica', 'Cable', 'Batería', 'Disco', 'Memoria', 'Otro']
    
    return render_template('inventario/listar.html', 
                         piezas=piezas, 
                         busqueda=busqueda,
                         categoria=categoria,
                         bajo_stock=bajo_stock,
                         categorias=categorias)


@inventario_bp.route('/pieza/nueva', methods=['GET', 'POST'])
@login_required
@role_required('admin', 'tecnico')
def nueva_pieza():
    """Crear nueva pieza"""
    if request.method == 'POST':
        nombre = request.form.get('nombre', '').strip()
        categoria = request.form.get('categoria', '').strip()
        codigo_interno = request.form.get('codigo_interno', '').strip()
        cantidad = request.form.get('cantidad', type=int, default=0)
        cantidad_minima = request.form.get('cantidad_minima', type=int, default=5)
        unidad = request.form.get('unidad', 'unidad').strip()
        precio_costo = request.form.get('precio_costo', type=float, default=0)
        precio_venta = request.form.get('precio_venta', type=float, default=0)
        proveedor_id = request.form.get('proveedor_id', type=int)
        descripcion = request.form.get('descripcion', '').strip()
        
        if not nombre or not categoria:
            flash('Nombre y categoría son obligatorios', 'warning')
            proveedores = Proveedor.query.filter_by(activo=True).all()
            return render_template('inventario/formulario.html', 
                                 pieza=None,
                                 proveedores=proveedores)
        
        pieza = Pieza(
            nombre=nombre,
            categoria=categoria,
            codigo_interno=codigo_interno,
            cantidad=cantidad,
            cantidad_minima=cantidad_minima,
            unidad=unidad,
            precio_costo=precio_costo,
            precio_venta=precio_venta,
            proveedor_id=proveedor_id if proveedor_id else None,
            descripcion=descripcion
        )
        
        db.session.add(pieza)
        db.session.flush()  # Para obtener el ID generado
        
        # Registrar movimiento de entrada inicial
        if cantidad > 0:
            movimiento = MovimientoInventario(
                pieza_id=pieza.id,
                tipo_movimiento='entrada',
                cantidad=cantidad,
                precio_unitario=precio_costo,
                proveedor_id=proveedor_id,
                usuario_id=session['usuario_id'],
                observaciones='Stock inicial'
            )
            db.session.add(movimiento)
        
        db.session.commit()
        flash('Pieza registrada correctamente', 'success')
        return redirect(url_for('inventario.listar_piezas'))
    
    proveedores = Proveedor.query.filter_by(activo=True).all()
    categorias = ['Cartucho', 'Tóner', 'Cinta', 'Fusor', 'Rodillo', 'Chip', 
                 'Placa electrónica', 'Cable', 'Batería', 'Disco', 'Memoria', 'Otro']
    
    return render_template('inventario/formulario.html', 
                         pieza=None,
                         proveedores=proveedores,
                         categorias=categorias)


@inventario_bp.route('/pieza/<int:id>/editar', methods=['GET', 'POST'])
@login_required
@role_required('admin', 'tecnico')
def editar_pieza(id):
    """Editar pieza existente"""
    pieza = db.session.get(Pieza, id)
    if not pieza:
        flash('Registro no encontrado', 'danger')
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        pieza.nombre = request.form.get('nombre', '').strip()
        pieza.categoria = request.form.get('categoria', '').strip()
        pieza.codigo_interno = request.form.get('codigo_interno', '').strip()
        pieza.cantidad_minima = request.form.get('cantidad_minima', type=int, default=5)
        pieza.unidad = request.form.get('unidad', 'unidad').strip()
        pieza.precio_costo = request.form.get('precio_costo', type=float, default=0)
        pieza.precio_venta = request.form.get('precio_venta', type=float, default=0)
        pieza.proveedor_id = request.form.get('proveedor_id', type=int)
        pieza.descripcion = request.form.get('descripcion', '').strip()
        
        pieza.fecha_actualizacion = datetime.now(timezone.utc)
        
        db.session.commit()
        flash('Pieza actualizada correctamente', 'success')
        return redirect(url_for('inventario.listar_piezas'))
    
    proveedores = Proveedor.query.filter_by(activo=True).all()
    categorias = ['Cartucho', 'Tóner', 'Cinta', 'Fusor', 'Rodillo', 'Chip', 
                 'Placa electrónica', 'Cable', 'Batería', 'Disco', 'Memoria', 'Otro']
    
    return render_template('inventario/formulario.html', 
                         pieza=pieza,
                         proveedores=proveedores,
                         categorias=categorias)


@inventario_bp.route('/pieza/<int:id>')
@login_required
def ver_pieza(id):
    """Ver detalle de pieza con movimientos y compatibilidades"""
    pieza = db.session.get(Pieza, id)
    if not pieza:
        flash('Registro no encontrado', 'danger')
        return redirect(url_for('index'))
    movimientos = MovimientoInventario.query.filter_by(pieza_id=id).order_by(MovimientoInventario.fecha_movimiento.desc()).limit(50).all()
    compatibilidades = PiezaCompatible.query.filter_by(pieza_id=id).all()
    
    return render_template('inventario/detalle.html', 
                         pieza=pieza,
                         movimientos=movimientos,
                         compatibilidades=compatibilidades)


@inventario_bp.route('/pieza/<int:id>/eliminar')
@login_required
@role_required('admin')
def eliminar_pieza(id):
    """Eliminar pieza (solo admin)"""
    pieza = db.session.get(Pieza, id)
    if not pieza:
        flash('Registro no encontrado', 'danger')
        return redirect(url_for('index'))
    
    # Verificar si tiene movimientos o está en órdenes
    if pieza.movimientos or pieza.usos_en_ordenes:
        flash('No se puede eliminar: la pieza tiene movimientos o está en órdenes', 'warning')
        return redirect(url_for('inventario.listar_piezas'))
    
    db.session.delete(pieza)
    db.session.commit()
    flash('Pieza eliminada correctamente', 'success')
    return redirect(url_for('inventario.listar_piezas'))


@inventario_bp.route('/pieza/<int:id>/entrada', methods=['GET', 'POST'])
@login_required
@role_required('admin', 'tecnico')
def registrar_entrada(id):
    """Registrar entrada de pieza al inventario"""
    pieza = db.session.get(Pieza, id)
    if not pieza:
        flash('Registro no encontrado', 'danger')
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        cantidad = request.form.get('cantidad', type=int, default=0)
        precio_costo = request.form.get('precio_costo', type=float, default=pieza.precio_costo)
        proveedor_id = request.form.get('proveedor_id', type=int)
        observaciones = request.form.get('observaciones', '').strip()
        
        if cantidad <= 0:
            flash('La cantidad debe ser mayor a cero', 'warning')
            return redirect(url_for('inventario.registrar_entrada', id=id))
        
        # Actualizar stock
        pieza.cantidad += cantidad
        pieza.precio_costo = precio_costo  # Actualizar costo
        pieza.fecha_actualizacion = datetime.now(timezone.utc)
        
        # Registrar movimiento
        movimiento = MovimientoInventario(
            pieza_id=pieza.id,
            tipo_movimiento='entrada',
            cantidad=cantidad,
            precio_unitario=precio_costo,
            proveedor_id=proveedor_id if proveedor_id else pieza.proveedor_id,
            usuario_id=session['usuario_id'],
            observaciones=observaciones
        )
        db.session.add(movimiento)
        db.session.commit()
        
        flash(f'Entrada de {cantidad} unidades registrada correctamente', 'success')
        return redirect(url_for('inventario.ver_pieza', id=id))
    
    proveedores = Proveedor.query.filter_by(activo=True).all()
    return render_template('inventario/entrada.html', 
                         pieza=pieza,
                         proveedores=proveedores)


@inventario_bp.route('/pieza/<int:id>/salida', methods=['GET', 'POST'])
@login_required
@role_required('admin', 'tecnico')
def registrar_salida(id):
    """Registrar salida de pieza del inventario"""
    pieza = db.session.get(Pieza, id)
    if not pieza:
        flash('Registro no encontrado', 'danger')
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        cantidad = request.form.get('cantidad', type=int, default=0)
        observaciones = request.form.get('observaciones', '').strip()
        
        if cantidad <= 0:
            flash('La cantidad debe ser mayor a cero', 'warning')
            return redirect(url_for('inventario.registrar_salida', id=id))
        
        if cantidad > pieza.cantidad:
            flash(f'Stock insuficiente. Disponible: {pieza.cantidad}', 'warning')
            return redirect(url_for('inventario.registrar_salida', id=id))
        
        # Actualizar stock
        pieza.cantidad -= cantidad
        pieza.fecha_actualizacion = datetime.now(timezone.utc)
        
        # Registrar movimiento
        movimiento = MovimientoInventario(
            pieza_id=pieza.id,
            tipo_movimiento='salida',
            cantidad=cantidad,
            precio_unitario=pieza.precio_costo,
            usuario_id=session['usuario_id'],
            observaciones=observaciones
        )
        db.session.add(movimiento)
        db.session.commit()
        
        flash(f'Salida de {cantidad} unidades registrada correctamente', 'success')
        return redirect(url_for('inventario.ver_pieza', id=id))
    
    return render_template('inventario/salida.html', pieza=pieza)


@inventario_bp.route('/pieza/<int:id>/compatibilidad', methods=['GET', 'POST'])
@login_required
@role_required('admin', 'tecnico')
def gestionar_compatibilidad(id):
    """Gestionar compatibilidad de pieza con modelos"""
    pieza = db.session.get(Pieza, id)
    if not pieza:
        flash('Registro no encontrado', 'danger')
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        modelo_id = request.form.get('modelo_id', type=int)
        notas = request.form.get('notas', '').strip()
        accion = request.form.get('accion')
        
        if accion == 'agregar' and modelo_id:
            # Verificar si ya existe
            existente = PiezaCompatible.query.filter_by(pieza_id=id, modelo_id=modelo_id).first()
            if not existente:
                compatibilidad = PiezaCompatible(
                    pieza_id=id,
                    modelo_id=modelo_id,
                    notas_compatibilidad=notas
                )
                db.session.add(compatibilidad)
                db.session.commit()
                flash('Compatibilidad agregada correctamente', 'success')
        
        elif accion == 'eliminar':
            compat_id = request.form.get('compatibilidad_id', type=int)
            compatibilidad = db.session.get(PiezaCompatible, compat_id)
            if compatibilidad and compatibilidad.pieza_id == id:
                db.session.delete(compatibilidad)
                db.session.commit()
                flash('Compatibilidad eliminada correctamente', 'success')
        
        return redirect(url_for('inventario.gestionar_compatibilidad', id=id))
    
    compatibilidades = PiezaCompatible.query.filter_by(pieza_id=id).all()
    modelos = ModeloEquipo.query.all()
    
    return render_template('inventario/compatibilidad.html', 
                         pieza=pieza,
                         compatibilidades=compatibilidades,
                         modelos=modelos)


@inventario_bp.route('/api/piezas/buscar')
@login_required
def api_buscar_piezas():
    """API para búsqueda AJAX de piezas"""
    termino = request.args.get('q', '')
    
    consulta = Pieza.query
    
    if termino:
        consulta = consulta.filter(
            (Pieza.nombre.ilike(f'%{termino}%')) |
            (Pieza.codigo_interno.ilike(f'%{termino}%'))
        )
    
    piezas = consulta.filter(Pieza.cantidad > 0).limit(20).all()
    
    resultados = []
    for p in piezas:
        resultados.append({
            'id': p.id,
            'texto': f"{p.nombre} (Stock: {p.cantidad})",
            'precio_venta': p.precio_venta,
            'stock': p.cantidad
        })
    
    return jsonify(resultados)
