"""
Blueprint para gestión de clientes
"""

from flask import Blueprint, render_template, redirect, url_for, flash, request, session
from models import db, Cliente, Dispositivo, Orden
from routes.auth import login_required, role_required

clientes_bp = Blueprint('clientes', __name__)


@clientes_bp.route('/clientes')
@login_required
def listar_clientes():
    """Listado de clientes con búsqueda y filtros"""
    busqueda = request.args.get('busqueda', '')
    tipo_cliente = request.args.get('tipo_cliente', '')
    pagina = request.args.get('pagina', 1, type=int)
    
    consulta = Cliente.query
    
    if busqueda:
        consulta = consulta.filter(
            (Cliente.nombres.ilike(f'%{busqueda}%')) |
            (Cliente.apellidos.ilike(f'%{busqueda}%')) |
            (Cliente.telefono_movil.ilike(f'%{busqueda}%')) |
            (Cliente.telefono_fijo.ilike(f'%{busqueda}%'))
        )
    
    if tipo_cliente:
        consulta = consulta.filter_by(tipo_cliente=tipo_cliente)
    
    consulta = consulta.filter_by(activo=True)
    clientes = consulta.order_by(Cliente.apellidos).paginate(page=pagina, per_page=20)
    
    return render_template('clientes/listar.html', 
                         clientes=clientes, 
                         busqueda=busqueda,
                         tipo_cliente=tipo_cliente)


@clientes_bp.route('/cliente/nuevo', methods=['GET', 'POST'])
@login_required
def nuevo_cliente():
    """Crear nuevo cliente"""
    if request.method == 'POST':
        nombres = request.form.get('nombres', '').strip()
        apellidos = request.form.get('apellidos', '').strip()
        telefono_fijo = request.form.get('telefono_fijo', '').strip()
        telefono_movil = request.form.get('telefono_movil', '').strip()
        direccion = request.form.get('direccion', '').strip()
        tipo_cliente = request.form.get('tipo_cliente', 'Particular')
        identificacion = request.form.get('identificacion', '').strip()
        
        if not nombres or not apellidos:
            flash('Nombres y apellidos son obligatorios', 'warning')
            return render_template('clientes/formulario.html', cliente=None)
        
        cliente = Cliente(
            nombres=nombres,
            apellidos=apellidos,
            telefono_fijo=telefono_fijo,
            telefono_movil=telefono_movil,
            direccion=direccion,
            tipo_cliente=tipo_cliente,
            identificacion=identificacion
        )
        
        db.session.add(cliente)
        db.session.commit()
        
        flash('Cliente registrado correctamente', 'success')
        return redirect(url_for('clientes.listar_clientes'))
    
    return render_template('clientes/formulario.html', cliente=None)


@clientes_bp.route('/cliente/<int:id>/editar', methods=['GET', 'POST'])
@login_required
def editar_cliente(id):
    """Editar cliente existente"""
    cliente = Cliente.query.get_or_404(id)
    
    if request.method == 'POST':
        cliente.nombres = request.form.get('nombres', '').strip()
        cliente.apellidos = request.form.get('apellidos', '').strip()
        cliente.telefono_fijo = request.form.get('telefono_fijo', '').strip()
        cliente.telefono_movil = request.form.get('telefono_movil', '').strip()
        cliente.direccion = request.form.get('direccion', '').strip()
        cliente.tipo_cliente = request.form.get('tipo_cliente', 'Particular')
        cliente.identificacion = request.form.get('identificacion', '').strip()
        
        db.session.commit()
        flash('Cliente actualizado correctamente', 'success')
        return redirect(url_for('clientes.listar_clientes'))
    
    return render_template('clientes/formulario.html', cliente=cliente)


@clientes_bp.route('/cliente/<int:id>/eliminar')
@login_required
@role_required('admin')
def eliminar_cliente(id):
    """Eliminar cliente (solo admin)"""
    cliente = Cliente.query.get_or_404(id)
    
    # Verificar si tiene órdenes
    if cliente.ordenes:
        flash('No se puede eliminar: el cliente tiene órdenes asociadas', 'warning')
        return redirect(url_for('clientes.listar_clientes'))
    
    cliente.activo = False
    db.session.commit()
    flash('Cliente eliminado correctamente', 'success')
    return redirect(url_for('clientes.listar_clientes'))


@clientes_bp.route('/cliente/<int:id>')
@login_required
def ver_cliente(id):
    """Ver detalle de cliente con historial"""
    cliente = Cliente.query.get_or_404(id)
    dispositivos = Dispositivo.query.filter_by(cliente_id=id).all()
    ordenes = Orden.query.filter_by(cliente_id=id).order_by(Orden.fecha_creacion.desc()).limit(20).all()
    
    return render_template('clientes/detalle.html', 
                         cliente=cliente, 
                         dispositivos=dispositivos,
                         ordenes=ordenes)
