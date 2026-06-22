"""
Blueprint para gestión de contratos de mantenimiento
"""

from flask import Blueprint, render_template, redirect, url_for, flash, request, send_file
from datetime import datetime, timedelta
from models import db, Contrato, Cliente
from routes.auth import login_required, role_required
import csv
from io import BytesIO

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
    contrato = db.session.get(Contrato, id)
    if not contrato:
        flash('Registro no encontrado', 'danger')
        return redirect(url_for('dashboard.index'))
    
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
    contrato = db.session.get(Contrato, id)
    if not contrato:
        flash('Registro no encontrado', 'danger')
        return redirect(url_for('dashboard.index'))
    
    # En lugar de eliminar, desactivamos
    contrato.activo = False
    db.session.commit()
    
    flash('Contrato desactivado correctamente', 'success')
    return redirect(url_for('contratos.listar_contratos'))


@contratos_bp.route('/contrato/<int:id>')
@login_required
def ver_contrato(id):
    """Ver detalle del contrato"""
    contrato = db.session.get(Contrato, id)
    if not contrato:
        flash('Registro no encontrado', 'danger')
        return redirect(url_for('dashboard.index'))
    
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
    contrato = db.session.get(Contrato, id)
    if not contrato:
        flash('Registro no encontrado', 'danger')
        return redirect(url_for('dashboard.index'))
    
    fecha_servicio = request.form.get('fecha_servicio')
    
    if fecha_servicio:
        contrato.fecha_ultimo_servicio = datetime.fromisoformat(fecha_servicio)
        db.session.commit()
        flash('Servicio registrado correctamente', 'success')
    else:
        flash('Fecha de servicio es requerida', 'warning')
    
    return redirect(url_for('contratos.ver_contrato', id=id))


@contratos_bp.route('/exportar/contratos')
@login_required
def exportar_contratos_csv():
    """Exportar lista de contratos a CSV"""
    output = BytesIO()
    output.write(b'\xef\xbb\xbf')  # BOM para Excel
    
    from io import StringIO
    temp_output = StringIO()
    writer = csv.writer(temp_output)
    
    writer.writerow(['ID', 'Cliente', 'Frecuencia', 'Fecha Inicio', 'Fecha Fin', 'Precio', 'Equipos', 'Activo'])
    contratos = Contrato.query.all()
    for c in contratos:
        writer.writerow([
            c.id,
            c.cliente.nombre_completo if c.cliente else '',
            c.frecuencia,
            c.fecha_inicio.strftime('%Y-%m-%d') if c.fecha_inicio else '',
            c.fecha_fin.strftime('%Y-%m-%d') if c.fecha_fin else '',
            c.precio,
            c.cantidad_equipos,
            'Sí' if c.activo else 'No'
        ])
    
    output.write(temp_output.getvalue().encode('utf-8'))
    output.seek(0)
    
    return send_file(
        output,
        mimetype='text/csv',
        as_attachment=True,
        download_name=f'contratos_{datetime.now().strftime("%Y%m%d")}.csv'
    )
