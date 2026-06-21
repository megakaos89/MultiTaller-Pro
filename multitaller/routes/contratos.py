"""
Blueprint para gestión de contratos de mantenimiento
"""

from flask import Blueprint, render_template, redirect, url_for, flash, request
from datetime import datetime, timedelta
from models import db, Contrato, Cliente
from routes.auth import login_required, role_required

contratos_bp = Blueprint('contratos', __name__)


@contratos_bp.route('/contratos')
@login_required
def listar_contratos():
    """Listado de contratos de mantenimiento"""
    activo = request.args.get('activo', '1')
    pagina = request.args.get('pagina', 1, type=int)
    
    consulta = Contrato.query
    
    if activo == '1':
        consulta = consulta.filter_by(activo=True)
    elif activo == '0':
        consulta = consulta.filter_by(activo=False)
    
    contratos = consulta.order_by(Contrato.fecha_inicio.desc()).paginate(page=pagina, per_page=20)
    
    return render_template('contratos/listar.html', 
                         contratos=contratos, 
                         activo=activo)


@contratos_bp.route('/contrato/nuevo', methods=['GET', 'POST'])
@login_required
@role_required('admin')
def nuevo_contrato():
    """Crear nuevo contrato de mantenimiento"""
    if request.method == 'POST':
        cliente_id = request.form.get('cliente_id', type=int)
        frecuencia = request.form.get('frecuencia', '')
        fecha_inicio = request.form.get('fecha_inicio')
        fecha_fin = request.form.get('fecha_fin')
        precio = request.form.get('precio', type=float, default=0)
        cantidad_equipos = request.form.get('cantidad_equipos', type=int, default=1)
        
        if not cliente_id or not frecuencia or not fecha_inicio:
            flash('Cliente, frecuencia y fecha de inicio son obligatorios', 'warning')
            clientes = Cliente.query.filter_by(activo=True).all()
            return render_template('contratos/formulario.html', 
                                 contrato=None,
                                 clientes=clientes)
        
        contrato = Contrato(
            cliente_id=cliente_id,
            frecuencia=frecuencia,
            fecha_inicio=datetime.fromisoformat(fecha_inicio),
            fecha_fin=datetime.fromisoformat(fecha_fin) if fecha_fin else None,
            precio=precio,
            cantidad_equipos=cantidad_equipos
        )
        
        db.session.add(contrato)
        db.session.commit()
        
        flash('Contrato registrado correctamente', 'success')
        return redirect(url_for('contratos.listar_contratos'))
    
    clientes = Cliente.query.filter_by(activo=True).all()
    frecuencias = ['semanal', 'quincenal', 'mensual', 'trimestral', 'semestral', 'anual']
    
    return render_template('contratos/formulario.html', 
                         contrato=None,
                         clientes=clientes,
                         frecuencias=frecuencias)


@contratos_bp.route('/contrato/<int:id>/editar', methods=['GET', 'POST'])
@login_required
@role_required('admin')
def editar_contrato(id):
    """Editar contrato existente"""
    contrato = Contrato = db.session.get(Contrato, id)
    if not Contrato:
        flash('Registro no encontrado', 'danger')
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        contrato.cliente_id = request.form.get('cliente_id', type=int)
        contrato.frecuencia = request.form.get('frecuencia', '')
        contrato.fecha_inicio = datetime.fromisoformat(request.form.get('fecha_inicio'))
        contrato.fecha_fin = datetime.fromisoformat(request.form.get('fecha_fin')) if request.form.get('fecha_fin') else None
        contrato.precio = request.form.get('precio', type=float, default=0)
        contrato.cantidad_equipos = request.form.get('cantidad_equipos', type=int, default=1)
        
        db.session.commit()
        flash('Contrato actualizado correctamente', 'success')
        return redirect(url_for('contratos.listar_contratos'))
    
    clientes = Cliente.query.filter_by(activo=True).all()
    frecuencias = ['semanal', 'quincenal', 'mensual', 'trimestral', 'semestral', 'anual']
    
    return render_template('contratos/formulario.html', 
                         contrato=contrato,
                         clientes=clientes,
                         frecuencias=frecuencias)


@contratos_bp.route('/contrato/<int:id>/eliminar')
@login_required
@role_required('admin')
def eliminar_contrato(id):
    """Eliminar/Desactivar contrato (solo admin)"""
    contrato = Contrato = db.session.get(Contrato, id)
    if not Contrato:
        flash('Registro no encontrado', 'danger')
        return redirect(url_for('index'))
    
    # En lugar de eliminar, desactivamos
    contrato.activo = False
    db.session.commit()
    
    flash('Contrato desactivado correctamente', 'success')
    return redirect(url_for('contratos.listar_contratos'))


@contratos_bp.route('/contrato/<int:id>')
@login_required
def ver_contrato(id):
    """Ver detalle del contrato"""
    contrato = Contrato = db.session.get(Contrato, id)
    if not Contrato:
        flash('Registro no encontrado', 'danger')
        return redirect(url_for('index'))
    
    # Calcular próximo mantenimiento
    proximo_mantenimiento = contrato.get_proximo_mantenimiento()
    
    # Obtener órdenes asociadas al contrato
    ordenes = contrato.ordenes[:10] if contrato.ordenes else []
    
    return render_template('contratos/detalle.html', 
                         contrato=contrato,
                         proximo_mantenimiento=proximo_mantenimiento,
                         ordenes=ordenes)


@contratos_bp.route('/contrato/<int:id>/registrar_servicio', methods=['POST'])
@login_required
def registrar_servicio(id):
    """Registrar servicio realizado en el contrato"""
    contrato = Contrato = db.session.get(Contrato, id)
    if not Contrato:
        flash('Registro no encontrado', 'danger')
        return redirect(url_for('index'))
    
    fecha_servicio = request.form.get('fecha_servicio')
    
    if fecha_servicio:
        contrato.fecha_ultimo_servicio = datetime.fromisoformat(fecha_servicio)
        db.session.commit()
        flash('Servicio registrado correctamente', 'success')
    else:
        flash('Fecha de servicio es requerida', 'warning')
    
    return redirect(url_for('contratos.ver_contrato', id=id))
