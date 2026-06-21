"""
Blueprint para gestión de proveedores
"""

from flask import Blueprint, render_template, redirect, url_for, flash, request
from models import db, Proveedor, Pieza
from routes.auth import login_required, role_required

proveedores_bp = Blueprint('proveedores', __name__)


@proveedores_bp.route('/proveedores')
@login_required
def listar_proveedores():
    """Listado de proveedores"""
    busqueda = request.args.get('busqueda', '')
    tipo = request.args.get('tipo', '')
    pagina = request.args.get('pagina', 1, type=int)
    
    consulta = Proveedor.query
    
    if busqueda:
        consulta = consulta.filter(
            (Proveedor.nombre.ilike(f'%{busqueda}%')) |
            (Proveedor.contacto.ilike(f'%{busqueda}%')) |
            (Proveedor.telefono.ilike(f'%{busqueda}%'))
        )
    
    if tipo:
        consulta = consulta.filter_by(tipo=tipo)
    
    consulta = consulta.filter_by(activo=True)
    proveedores = consulta.order_by(Proveedor.nombre).paginate(page=pagina, per_page=20)
    
    return render_template('proveedores/listar.html', 
                         proveedores=proveedores, 
                         busqueda=busqueda,
                         tipo=tipo)


@proveedores_bp.route('/proveedor/nuevo', methods=['GET', 'POST'])
@login_required
@role_required('admin', 'tecnico')
def nuevo_proveedor():
    """Crear nuevo proveedor"""
    if request.method == 'POST':
        nombre = request.form.get('nombre', '').strip()
        contacto = request.form.get('contacto', '').strip()
        telefono = request.form.get('telefono', '').strip()
        tipo = request.form.get('tipo', 'formal')
        
        if not nombre:
            flash('El nombre es obligatorio', 'warning')
            return render_template('proveedores/formulario.html', proveedor=None)
        
        proveedor = Proveedor(
            nombre=nombre,
            contacto=contacto,
            telefono=telefono,
            tipo=tipo
        )
        
        db.session.add(proveedor)
        db.session.commit()
        
        flash('Proveedor registrado correctamente', 'success')
        return redirect(url_for('proveedores.listar_proveedores'))
    
    return render_template('proveedores/formulario.html', proveedor=None)


@proveedores_bp.route('/proveedor/<int:id>/editar', methods=['GET', 'POST'])
@login_required
@role_required('admin', 'tecnico')
def editar_proveedor(id):
    """Editar proveedor existente"""
    proveedor = Proveedor.query.get_or_404(id)
    
    if request.method == 'POST':
        proveedor.nombre = request.form.get('nombre', '').strip()
        proveedor.contacto = request.form.get('contacto', '').strip()
        proveedor.telefono = request.form.get('telefono', '').strip()
        proveedor.tipo = request.form.get('tipo', 'formal')
        
        db.session.commit()
        flash('Proveedor actualizado correctamente', 'success')
        return redirect(url_for('proveedores.listar_proveedores'))
    
    return render_template('proveedores/formulario.html', proveedor=proveedor)


@proveedores_bp.route('/proveedor/<int:id>/eliminar')
@login_required
@role_required('admin')
def eliminar_proveedor(id):
    """Eliminar proveedor (solo admin)"""
    proveedor = Proveedor.query.get_or_404(id)
    
    # Verificar si tiene piezas asociadas
    if proveedor.piezas:
        flash('No se puede eliminar: hay piezas asociadas a este proveedor', 'warning')
        return redirect(url_for('proveedores.listar_proveedores'))
    
    proveedor.activo = False
    db.session.commit()
    flash('Proveedor eliminado correctamente', 'success')
    return redirect(url_for('proveedores.listar_proveedores'))


@proveedores_bp.route('/proveedor/<int:id>')
@login_required
def ver_proveedor(id):
    """Ver detalle del proveedor"""
    proveedor = Proveedor.query.get_or_404(id)
    piezas = Pieza.query.filter_by(proveedor_id=id).all()
    
    return render_template('proveedores/detalle.html', 
                         proveedor=proveedor,
                         piezas=piezas)
