"""
Blueprint para gestión de dispositivos de clientes
"""

from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify, current_app
from models import db, Dispositivo, Cliente, ModeloEquipo, OrdenDispositivo
from routes.auth import login_required, role_required
import os
from werkzeug.utils import secure_filename

dispositivos_bp = Blueprint('dispositivos', __name__)


def allowed_file(filename):
    """Verificar si el archivo tiene extensión permitida"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in current_app.config.get('ALLOWED_EXTENSIONS', {'png', 'jpg', 'jpeg', 'gif', 'pdf'})


@dispositivos_bp.route('/dispositivos')
@login_required
def listar_dispositivos():
    """Listado de dispositivos"""
    busqueda = request.args.get('busqueda', '')
    cliente_id = request.args.get('cliente_id', type=int)
    tipo = request.args.get('tipo', '')
    pagina = request.args.get('pagina', 1, type=int)
    
    consulta = Dispositivo.query
    
    if busqueda:
        consulta = consulta.filter(
            (Dispositivo.marca.ilike(f'%{busqueda}%')) |
            (Dispositivo.modelo_texto.ilike(f'%{busqueda}%')) |
            (Dispositivo.numero_serie.ilike(f'%{busqueda}%'))
        )
    
    if cliente_id:
        consulta = consulta.filter_by(cliente_id=cliente_id)
    
    if tipo:
        consulta = consulta.filter_by(tipo=tipo)
    
    dispositivos = consulta.order_by(Dispositivo.marca).paginate(page=pagina, per_page=20)
    
    # Obtener clientes para el filtro
    clientes = Cliente.query.filter_by(activo=True).order_by(Cliente.apellidos).all()
    
    return render_template('dispositivos/listar.html', 
                         dispositivos=dispositivos, 
                         busqueda=busqueda,
                         cliente_id=cliente_id,
                         tipo=tipo,
                         clientes=clientes)


@dispositivos_bp.route('/dispositivo/nuevo', methods=['GET', 'POST'])
@login_required
def nuevo_dispositivo():
    """Crear nuevo dispositivo"""
    if request.method == 'POST':
        cliente_id = request.form.get('cliente_id', type=int)
        modelo_id = request.form.get('modelo_id', type=int)
        marca = request.form.get('marca', '').strip()
        modelo_texto = request.form.get('modelo_texto', '').strip()
        numero_serie = request.form.get('numero_serie', '').strip()
        tipo = request.form.get('tipo', '').strip()
        especificaciones_extra = request.form.get('especificaciones_extra', '').strip()
        
        # Manejo de foto
        foto_path = None
        if 'foto' in request.files:
            archivo = request.files['foto']
            if archivo and archivo.filename and allowed_file(archivo.filename):
                filename = secure_filename(archivo.filename)
                filepath = os.path.join('static', 'uploads', f'dispositivo_{filename}')
                archivo.save(filepath)
                foto_path = filepath
            elif archivo and archivo.filename:
                flash('Extensión de archivo no permitida. Solo png, jpg, jpeg, gif, pdf', 'warning')
        
        if not cliente_id or not marca:
            flash('Cliente y marca son obligatorios', 'warning')
            clientes = Cliente.query.filter_by(activo=True).all()
            return render_template('dispositivos/formulario.html', 
                                 dispositivo=None, 
                                 clientes=clientes,
                                 modelos=[])
        
        # Si se seleccionó modelo, obtener tipo del modelo
        if modelo_id:
            modelo = db.session.get(ModeloEquipo, modelo_id)
            if modelo:
                tipo = modelo.tipo
        
        dispositivo = Dispositivo(
            cliente_id=cliente_id,
            modelo_id=modelo_id if modelo_id else None,
            marca=marca,
            modelo_texto=modelo_texto,
            numero_serie=numero_serie,
            tipo=tipo,
            especificaciones_extra=especificaciones_extra,
            foto_path=foto_path
        )
        
        db.session.add(dispositivo)
        db.session.commit()
        
        flash('Dispositivo registrado correctamente', 'success')
        return redirect(url_for('dispositivos.listar_dispositivos'))
    
    clientes = Cliente.query.filter_by(activo=True).all()
    modelos = ModeloEquipo.query.all()
    
    return render_template('dispositivos/formulario.html', 
                         dispositivo=None, 
                         clientes=clientes,
                         modelos=modelos)


@dispositivos_bp.route('/dispositivo/<int:id>/editar', methods=['GET', 'POST'])
@login_required
def editar_dispositivo(id):
    """Editar dispositivo existente"""
    dispositivo = db.session.get(Dispositivo, id)
    if not dispositivo:
        flash('Registro no encontrado', 'danger')
        return redirect(url_for('dashboard.index'))
    
    if request.method == 'POST':
        dispositivo.cliente_id = request.form.get('cliente_id', type=int)
        dispositivo.modelo_id = request.form.get('modelo_id', type=int)
        dispositivo.marca = request.form.get('marca', '').strip()
        dispositivo.modelo_texto = request.form.get('modelo_texto', '').strip()
        dispositivo.numero_serie = request.form.get('numero_serie', '').strip()
        dispositivo.tipo = request.form.get('tipo', '').strip()
        dispositivo.especificaciones_extra = request.form.get('especificaciones_extra', '').strip()
        
        # Manejo de foto
        if 'foto' in request.files:
            archivo = request.files['foto']
            if archivo and archivo.filename and allowed_file(archivo.filename):
                # Eliminar foto anterior si existe
                if dispositivo.foto_path and os.path.exists(dispositivo.foto_path):
                    os.remove(dispositivo.foto_path)
                
                filename = secure_filename(archivo.filename)
                filepath = os.path.join('static', 'uploads', f'dispositivo_{filename}')
                archivo.save(filepath)
                dispositivo.foto_path = filepath
            elif archivo and archivo.filename:
                flash('Extensión de archivo no permitida. Solo png, jpg, jpeg, gif, pdf', 'warning')
                return redirect(url_for('dispositivos.editar_dispositivo', id=dispositivo.id))
        
        db.session.commit()
        flash('Dispositivo actualizado correctamente', 'success')
        return redirect(url_for('dispositivos.listar_dispositivos'))
    
    clientes = Cliente.query.filter_by(activo=True).all()
    modelos = ModeloEquipo.query.all()
    
    return render_template('dispositivos/formulario.html', 
                         dispositivo=dispositivo, 
                         clientes=clientes,
                         modelos=modelos)


@dispositivos_bp.route('/dispositivo/<int:id>/eliminar')
@login_required
@role_required('admin')
def eliminar_dispositivo(id):
    """Eliminar dispositivo (solo admin)"""
    dispositivo = db.session.get(Dispositivo, id)
    if not dispositivo:
        flash('Registro no encontrado', 'danger')
        return redirect(url_for('dashboard.index'))
    
    # Verificar si tiene órdenes asociadas
    if dispositivo.ordenes:
        flash('No se puede eliminar: el dispositivo tiene órdenes asociadas', 'warning')
        return redirect(url_for('dispositivos.listar_dispositivos'))
    
    # Eliminar foto si existe
    if dispositivo.foto_path and os.path.exists(dispositivo.foto_path):
        os.remove(dispositivo.foto_path)
    
    db.session.delete(dispositivo)
    db.session.commit()
    flash('Dispositivo eliminado correctamente', 'success')
    return redirect(url_for('dispositivos.listar_dispositivos'))


@dispositivos_bp.route('/dispositivo/<int:id>')
@login_required
def ver_dispositivo(id):
    """Ver detalle del dispositivo con historial"""
    dispositivo = db.session.get(Dispositivo, id)
    if not dispositivo:
        flash('Registro no encontrado', 'danger')
        return redirect(url_for('dashboard.index'))
    
    # Obtener historial de órdenes
    ordenes_dispositivo = OrdenDispositivo.query.filter_by(dispositivo_id=id).all()
    ordenes = [od.orden for od in ordenes_dispositivo]
    
    return render_template('dispositivos/detalle.html', 
                         dispositivo=dispositivo,
                         ordenes=ordenes)


@dispositivos_bp.route('/api/dispositivos/buscar')
@login_required
def api_buscar_dispositivos():
    """API para búsqueda AJAX de dispositivos por cliente"""
    cliente_id = request.args.get('cliente_id', type=int)
    termino = request.args.get('q', '')
    
    consulta = Dispositivo.query
    
    if cliente_id:
        consulta = consulta.filter_by(cliente_id=cliente_id)
    
    if termino:
        consulta = consulta.filter(
            (Dispositivo.marca.ilike(f'%{termino}%')) |
            (Dispositivo.modelo_texto.ilike(f'%{termino}%')) |
            (Dispositivo.numero_serie.ilike(f'%{termino}%'))
        )
    
    dispositivos = consulta.limit(20).all()
    
    resultados = []
    for d in dispositivos:
        resultados.append({
            'id': d.id,
            'texto': f"{d.marca} {d.modelo_texto or ''} ({d.tipo or 'Sin tipo'})",
            'tipo': d.tipo
        })
    
    return jsonify(resultados)
