"""
Blueprint para gestión de técnicos y productividad
"""

from flask import Blueprint, render_template, redirect, url_for, flash, request
from models import db, Tecnico, Orden
from routes.auth import login_required, role_required

tecnicos_bp = Blueprint('tecnicos', __name__)


@tecnicos_bp.route('/tecnicos')
@login_required
def listar_tecnicos():
    """Listado de técnicos"""
    pagina = request.args.get('pagina', 1, type=int)
    
    tecnicos = Tecnico.query.filter_by(activo=True).order_by(Tecnico.nombre).paginate(page=pagina, per_page=20)
    
    return render_template('tecnicos/listar.html', tecnicos=tecnicos)


@tecnicos_bp.route('/tecnico/nuevo', methods=['GET', 'POST'])
@login_required
@role_required('admin')
def nuevo_tecnico():
    """Crear nuevo técnico"""
    if request.method == 'POST':
        nombre = request.form.get('nombre', '').strip()
        especialidad = request.form.get('especialidad', '').strip()
        costo_hora = request.form.get('costo_hora', type=float, default=0)
        
        if not nombre:
            flash('El nombre es obligatorio', 'warning')
            return render_template('tecnicos/formulario.html', tecnico=None)
        
        tecnico = Tecnico(
            nombre=nombre,
            especialidad=especialidad,
            costo_hora=costo_hora
        )
        
        db.session.add(tecnico)
        db.session.commit()
        
        flash('Técnico registrado correctamente', 'success')
        return redirect(url_for('tecnicos.listar_tecnicos'))
    
    return render_template('tecnicos/formulario.html', tecnico=None)


@tecnicos_bp.route('/tecnico/<int:id>/editar', methods=['GET', 'POST'])
@login_required
@role_required('admin')
def editar_tecnico(id):
    """Editar técnico existente"""
    tecnico = Tecnico = db.session.get(Tecnico, id)
    if not Tecnico:
        flash('Registro no encontrado', 'danger')
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        tecnico.nombre = request.form.get('nombre', '').strip()
        tecnico.especialidad = request.form.get('especialidad', '').strip()
        tecnico.costo_hora = request.form.get('costo_hora', type=float, default=0)
        
        db.session.commit()
        flash('Técnico actualizado correctamente', 'success')
        return redirect(url_for('tecnicos.listar_tecnicos'))
    
    return render_template('tecnicos/formulario.html', tecnico=tecnico)


@tecnicos_bp.route('/tecnico/<int:id>/eliminar')
@login_required
@role_required('admin')
def eliminar_tecnico(id):
    """Eliminar técnico (solo admin)"""
    tecnico = Tecnico = db.session.get(Tecnico, id)
    if not Tecnico:
        flash('Registro no encontrado', 'danger')
        return redirect(url_for('index'))
    
    # Verificar si tiene órdenes asignadas
    if tecnico.ordenes_asignadas:
        flash('No se puede eliminar: el técnico tiene órdenes asociadas', 'warning')
        return redirect(url_for('tecnicos.listar_tecnicos'))
    
    tecnico.activo = False
    db.session.commit()
    flash('Técnico eliminado correctamente', 'success')
    return redirect(url_for('tecnicos.listar_tecnicos'))


@tecnicos_bp.route('/tecnico/<int:id>')
@login_required
def ver_tecnico(id):
    """Ver detalle del técnico con estadísticas"""
    tecnico = Tecnico = db.session.get(Tecnico, id)
    if not Tecnico:
        flash('Registro no encontrado', 'danger')
        return redirect(url_for('index'))
    
    # Estadísticas básicas
    ordenes_asignadas = Orden.query.filter_by(tecnico_id=id).all()
    ordenes_activas = [o for o in ordenes_asignadas if o.estado_general not in ['Entregado', 'Cancelado']]
    ordenes_completadas = [o for o in ordenes_asignadas if o.estado_general == 'Entregado']
    
    return render_template('tecnicos/detalle.html', 
                         tecnico=tecnico,
                         ordenes_activas=ordenes_activas,
                         ordenes_completadas=ordenes_completadas)


@tecnicos_bp.route('/productividad')
@login_required
def productividad():
    """Reporte de productividad por técnico"""
    periodo = request.args.get('periodo', 'mes')
    
    from datetime import datetime, timedelta, timezone
    
    hoy = datetime.now(timezone.utc)
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
        
        productividad_data.append({
            'tecnico': tecnico,
            'ordenes_totales': len(ordenes_periodo),
            'ordenes_completadas': len(completadas),
            'ingresos_generados': ingresos_generados
        })
    
    # Ordenar por órdenes completadas
    productividad_data.sort(key=lambda x: x['ordenes_completadas'], reverse=True)
    
    return render_template('tecnicos/productividad.html', 
                         productividad_data=productividad_data,
                         periodo=periodo)
