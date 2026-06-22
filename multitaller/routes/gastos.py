"""
Blueprint para gestión de gastos operativos
"""

from flask import Blueprint, render_template, redirect, url_for, flash, request, session
from datetime import datetime, timezone
from models import db, Gasto, CategoriaGasto
from routes.auth import login_required, role_required

gastos_bp = Blueprint('gastos', __name__)


@gastos_bp.route('/gastos')
@login_required
def listar_gastos():
    """Listado de gastos operativos"""
    categoria_id = request.args.get('categoria_id', type=int)
    fecha_inicio = request.args.get('fecha_inicio', '')
    fecha_fin = request.args.get('fecha_fin', '')
    pagina = request.args.get('pagina', 1, type=int)
    
    consulta = Gasto.query
    
    if categoria_id:
        consulta = consulta.filter_by(categoria_id=categoria_id)
    
    if fecha_inicio:
        consulta = consulta.filter(Gasto.fecha >= datetime.fromisoformat(fecha_inicio))
    
    if fecha_fin:
        consulta = consulta.filter(Gasto.fecha <= datetime.fromisoformat(fecha_fin))
    
    gastos = consulta.order_by(Gasto.fecha.desc()).paginate(page=pagina, per_page=20)
    
    categorias = CategoriaGasto.query.all()
    
    return render_template('gastos/listar.html', 
                         gastos=gastos, 
                         categorias=categorias,
                         categoria_id=categoria_id,
                         fecha_inicio=fecha_inicio,
                         fecha_fin=fecha_fin)


@gastos_bp.route('/gasto/nuevo', methods=['GET', 'POST'])
@login_required
@role_required('admin')
def nuevo_gasto():
    """Registrar nuevo gasto"""
    if request.method == 'POST':
        categoria_id = request.form.get('categoria_id', type=int)
        descripcion = request.form.get('descripcion', '').strip()
        monto = request.form.get('monto', type=float)
        fecha = request.form.get('fecha')
        
        if not categoria_id or not descripcion or not monto:
            flash('Categoría, descripción y monto son obligatorios', 'warning')
            categorias = CategoriaGasto.query.all()
            return render_template('gastos/formulario.html', 
                                 gasto=None,
                                 categorias=categorias)
        
        gasto = Gasto(
            categoria_id=categoria_id,
            descripcion=descripcion,
            monto=monto,
            fecha=datetime.fromisoformat(fecha) if fecha else datetime.now(timezone.utc),
            usuario_id=session['usuario_id']
        )
        
        db.session.add(gasto)
        db.session.commit()
        
        flash('Gasto registrado correctamente', 'success')
        return redirect(url_for('gastos.listar_gastos'))
    
    categorias = CategoriaGasto.query.all()
    
    return render_template('gastos/formulario.html', 
                         gasto=None,
                         categorias=categorias)


@gastos_bp.route('/gasto/<int:id>/editar', methods=['GET', 'POST'])
@login_required
@role_required('admin')
def editar_gasto(id):
    """Editar gasto existente"""
    gasto = db.session.get(Gasto, id)
    if not gasto:
        flash('Registro no encontrado', 'danger')
        return redirect(url_for('dashboard.index'))
    
    if request.method == 'POST':
        gasto.categoria_id = request.form.get('categoria_id', type=int)
        gasto.descripcion = request.form.get('descripcion', '').strip()
        gasto.monto = request.form.get('monto', type=float)
        gasto.fecha = datetime.fromisoformat(request.form.get('fecha')) if request.form.get('fecha') else gasto.fecha
        
        db.session.commit()
        flash('Gasto actualizado correctamente', 'success')
        return redirect(url_for('gastos.listar_gastos'))
    
    categorias = CategoriaGasto.query.all()
    
    return render_template('gastos/formulario.html', 
                         gasto=gasto,
                         categorias=categorias)


@gastos_bp.route('/gasto/<int:id>/eliminar')
@login_required
@role_required('admin')
def eliminar_gasto(id):
    """Eliminar gasto (solo admin)"""
    gasto = db.session.get(Gasto, id)
    if not gasto:
        flash('Registro no encontrado', 'danger')
        return redirect(url_for('dashboard.index'))
    
    db.session.delete(gasto)
    db.session.commit()
    flash('Gasto eliminado correctamente', 'success')
    return redirect(url_for('gastos.listar_gastos'))


@gastos_bp.route('/categorias_gastos')
@login_required
@role_required('admin')
def gestionar_categorias():
    """Listado de categorías de gastos"""
    categorias = CategoriaGasto.query.all()
    return render_template('gastos/categorias.html', categorias=categorias)


@gastos_bp.route('/categoria_gasto/nueva', methods=['GET', 'POST'])
@login_required
@role_required('admin')
def nueva_categoria():
    """Crear nueva categoría de gasto"""
    if request.method == 'POST':
        nombre = request.form.get('nombre', '').strip()
        descripcion = request.form.get('descripcion', '').strip()
        
        if not nombre:
            flash('El nombre es obligatorio', 'warning')
            return render_template('gastos/categoria_formulario.html', categoria=None)
        
        categoria = CategoriaGasto(nombre=nombre, descripcion=descripcion)
        db.session.add(categoria)
        db.session.commit()
        
        flash('Categoría creada correctamente', 'success')
        return redirect(url_for('gastos.gestionar_categorias'))
    
    return render_template('gastos/categoria_formulario.html', categoria=None)


@gastos_bp.route('/categoria_gasto/<int:id>/eliminar')
@login_required
@role_required('admin')
def eliminar_categoria(id):
    """Eliminar categoría de gasto (solo admin)"""
    categoria = db.session.get(CategoriaGasto, id)
    if not categoria:
        flash('Registro no encontrado', 'danger')
        return redirect(url_for('dashboard.index'))
    
    # Verificar si tiene gastos asociados
    if categoria.gastos:
        flash('No se puede eliminar: hay gastos asociados a esta categoría', 'warning')
        return redirect(url_for('gastos.gestionar_categorias'))
    
    db.session.delete(categoria)
    db.session.commit()
    flash('Categoría eliminada correctamente', 'success')
    return redirect(url_for('gastos.gestionar_categorias'))
