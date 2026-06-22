"""
Blueprint para gestión de modelos de equipos
"""

from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from models import db, ModeloEquipo, PiezaCompatible
from routes.auth import login_required, role_required
import json

modelos_bp = Blueprint('modelos', __name__)


@modelos_bp.route('/modelos')
@login_required
def listar_modelos():
    """Listado de modelos de equipos"""
    busqueda = request.args.get('busqueda', '')
    tipo = request.args.get('tipo', '')
    pagina = request.args.get('pagina', 1, type=int)
    
    consulta = ModeloEquipo.query
    
    if busqueda:
        consulta = consulta.filter(
            (ModeloEquipo.marca.ilike(f'%{busqueda}%')) |
            (ModeloEquipo.modelo.ilike(f'%{busqueda}%'))
        )
    
    if tipo:
        consulta = consulta.filter_by(tipo=tipo)
    
    modelos = consulta.order_by(ModeloEquipo.marca, ModeloEquipo.modelo).paginate(page=pagina, per_page=20)
    
    tipos_equipo = ['PC escritorio', 'Laptop', 'Impresora', 'Contadora de billetes', 
                   'Escáner', 'Monitor', 'UPS', 'Otro']
    
    return render_template('modelos/listar.html', 
                         modelos=modelos, 
                         busqueda=busqueda,
                         tipo=tipo,
                         tipos_equipo=tipos_equipo)


@modelos_bp.route('/modelo/nuevo', methods=['GET', 'POST'])
@login_required
def nuevo_modelo():
    """Crear nuevo modelo de equipo"""
    if request.method == 'POST':
        marca = request.form.get('marca', '').strip()
        modelo = request.form.get('modelo', '').strip()
        tipo = request.form.get('tipo', '').strip()
        especificaciones = request.form.get('especificaciones', '').strip()
        problemas_frecuentes = request.form.get('problemas_frecuentes', '').strip()
        notas_servicio = request.form.get('notas_servicio', '').strip()
        
        if not marca or not modelo or not tipo:
            flash('Marca, modelo y tipo son obligatorios', 'warning')
            return render_template('modelos/formulario.html', modelo=None)
        
        nuevo = ModeloEquipo(
            marca=marca,
            modelo=modelo,
            tipo=tipo,
            especificaciones=especificaciones,
            problemas_frecuentes=problemas_frecuentes,
            notas_servicio=notas_servicio
        )
        
        db.session.add(nuevo)
        db.session.commit()
        
        flash('Modelo registrado correctamente', 'success')
        return redirect(url_for('modelos.listar_modelos'))
    
    tipos_equipo = ['PC escritorio', 'Laptop', 'Impresora', 'Contadora de billetes', 
                   'Escáner', 'Monitor', 'UPS', 'Otro']
    
    return render_template('modelos/formulario.html', modelo=None, tipos_equipo=tipos_equipo)


@modelos_bp.route('/modelo/<int:id>/editar', methods=['GET', 'POST'])
@login_required
def editar_modelo(id):
    """Editar modelo existente"""
    modelo = db.session.get(ModeloEquipo, id)
    if not modelo:
        flash('Registro no encontrado', 'danger')
        return redirect(url_for('dashboard.index'))
    
    if request.method == 'POST':
        modelo.marca = request.form.get('marca', '').strip()
        modelo.modelo = request.form.get('modelo', '').strip()
        modelo.tipo = request.form.get('tipo', '').strip()
        modelo.especificaciones = request.form.get('especificaciones', '').strip()
        modelo.problemas_frecuentes = request.form.get('problemas_frecuentes', '').strip()
        modelo.notas_servicio = request.form.get('notas_servicio', '').strip()
        
        db.session.commit()
        flash('Modelo actualizado correctamente', 'success')
        return redirect(url_for('modelos.listar_modelos'))
    
    tipos_equipo = ['PC escritorio', 'Laptop', 'Impresora', 'Contadora de billetes', 
                   'Escáner', 'Monitor', 'UPS', 'Otro']
    
    return render_template('modelos/formulario.html', modelo=modelo, tipos_equipo=tipos_equipo)


@modelos_bp.route('/modelo/<int:id>/eliminar')
@login_required
@role_required('admin')
def eliminar_modelo(id):
    """Eliminar modelo (solo admin)"""
    modelo = db.session.get(ModeloEquipo, id)
    if not modelo:
        flash('Registro no encontrado', 'danger')
        return redirect(url_for('dashboard.index'))
    
    # Verificar si tiene dispositivos asociados
    if modelo.dispositivos:
        flash('No se puede eliminar: hay dispositivos asociados a este modelo', 'warning')
        return redirect(url_for('modelos.listar_modelos'))
    
    db.session.delete(modelo)
    db.session.commit()
    flash('Modelo eliminado correctamente', 'success')
    return redirect(url_for('modelos.listar_modelos'))


@modelos_bp.route('/modelo/<int:id>')
@login_required
def ver_modelo(id):
    """Ver detalle del modelo con compatibilidades"""
    modelo = db.session.get(ModeloEquipo, id)
    if not modelo:
        flash('Registro no encontrado', 'danger')
        return redirect(url_for('dashboard.index'))
    piezas_compatibles = PiezaCompatible.query.filter_by(modelo_id=id).all()
    
    return render_template('modelos/detalle.html', 
                         modelo=modelo,
                         piezas_compatibles=piezas_compatibles)


@modelos_bp.route('/api/modelos/buscar')
@login_required
def api_buscar_modelos():
    """API para búsqueda AJAX de modelos"""
    termino = request.args.get('q', '')
    tipo = request.args.get('tipo', '')
    
    consulta = ModeloEquipo.query
    
    if termino:
        consulta = consulta.filter(
            (ModeloEquipo.marca.ilike(f'%{termino}%')) |
            (ModeloEquipo.modelo.ilike(f'%{termino}%'))
        )
    
    if tipo:
        consulta = consulta.filter_by(tipo=tipo)
    
    modelos = consulta.limit(20).all()
    
    resultados = []
    for m in modelos:
        resultados.append({
            'id': m.id,
            'texto': f"{m.marca} {m.modelo}",
            'tipo': m.tipo
        })
    
    return jsonify(resultados)
