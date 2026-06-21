"""
Blueprint para autenticación de usuarios
"""

from flask import Blueprint, render_template, redirect, url_for, flash, session, request
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
from models import db, Usuario

auth_bp = Blueprint('auth', __name__)


def login_required(f):
    """Decorador para requerir autenticación"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'usuario_id' not in session:
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function


def admin_required(f):
    """Decorador para requerir rol de administrador"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'usuario_id' not in session:
            return redirect(url_for('auth.login'))
        usuario = Usuario.query.get(session['usuario_id'])
        if not usuario or usuario.rol != 'admin':
            flash('Acceso denegado. Se requiere rol de administrador.', 'danger')
            return redirect(url_for('dashboard.index'))
        return f(*args, **kwargs)
    return decorated_function


def role_required(*roles):
    """Decorador para requerir roles específicos"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'usuario_id' not in session:
                return redirect(url_for('auth.login'))
            usuario = Usuario.query.get(session['usuario_id'])
            if not usuario or usuario.rol not in roles:
                flash('Acceso denegado. No tiene permisos suficientes.', 'danger')
                return redirect(url_for('dashboard.index'))
            return f(*args, **kwargs)
        return decorated_function
    return decorator


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Formulario de inicio de sesión"""
    if 'usuario_id' in session:
        return redirect(url_for('dashboard.index'))
    
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        
        if not username or not password:
            flash('Usuario y contraseña son obligatorios', 'warning')
            return render_template('auth/login.html')
        
        usuario = Usuario.query.filter_by(username=username).first()
        
        if usuario and check_password_hash(usuario.password_hash, password):
            if not usuario.activo:
                flash('Usuario desactivado. Contacte al administrador.', 'danger')
                return render_template('auth/login.html')
            
            session['usuario_id'] = usuario.id
            session['usuario_nombre'] = usuario.nombre_completo
            session['usuario_rol'] = usuario.rol
            
            flash(f'Bienvenido, {usuario.nombre_completo}', 'success')
            return redirect(url_for('dashboard.index'))
        else:
            flash('Usuario o contraseña incorrectos', 'danger')
    
    return render_template('auth/login.html')


@auth_bp.route('/logout')
def logout():
    """Cerrar sesión"""
    session.clear()
    flash('Sesión cerrada correctamente', 'info')
    return redirect(url_for('auth.login'))


@auth_bp.route('/usuarios', methods=['GET', 'POST'])
@login_required
@admin_required
def gestionar_usuarios():
    """Gestión de usuarios (solo admin)"""
    if request.method == 'POST':
        # Crear o editar usuario
        usuario_id = request.form.get('id')
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        nombre_completo = request.form.get('nombre_completo', '').strip()
        rol = request.form.get('rol', 'tecnico')
        activo = request.form.get('activo') == 'on'
        
        if not username or not nombre_completo:
            flash('Username y nombre completo son obligatorios', 'warning')
            return redirect(url_for('auth.gestionar_usuarios'))
        
        if usuario_id:
            # Editar existente
            usuario = Usuario.query.get(usuario_id)
            if usuario:
                usuario.username = username
                usuario.nombre_completo = nombre_completo
                usuario.rol = rol
                usuario.activo = activo
                if password:
                    usuario.password_hash = generate_password_hash(password)
                flash('Usuario actualizado correctamente', 'success')
        else:
            # Crear nuevo
            if Usuario.query.filter_by(username=username).first():
                flash('El username ya existe', 'warning')
                return redirect(url_for('auth.gestionar_usuarios'))
            
            if not password:
                flash('La contraseña es obligatoria para nuevos usuarios', 'warning')
                return redirect(url_for('auth.gestionar_usuarios'))
            
            nuevo_usuario = Usuario(
                username=username,
                password_hash=generate_password_hash(password),
                nombre_completo=nombre_completo,
                rol=rol,
                activo=activo
            )
            db.session.add(nuevo_usuario)
            flash('Usuario creado correctamente', 'success')
        
        db.session.commit()
        return redirect(url_for('auth.gestionar_usuarios'))
    
    usuarios = Usuario.query.all()
    return render_template('auth/usuarios.html', usuarios=usuarios)


@auth_bp.route('/usuarios/eliminar/<int:id>')
@login_required
@admin_required
def eliminar_usuario(id):
    """Eliminar usuario (solo admin)"""
    if id == session.get('usuario_id'):
        flash('No puede eliminar su propio usuario', 'warning')
        return redirect(url_for('auth.gestionar_usuarios'))
    
    usuario = Usuario.query.get(id)
    if usuario:
        db.session.delete(usuario)
        db.session.commit()
        flash('Usuario eliminado correctamente', 'success')
    else:
        flash('Usuario no encontrado', 'danger')
    
    return redirect(url_for('auth.gestionar_usuarios'))


@auth_bp.route('/perfil', methods=['GET', 'POST'])
@login_required
def perfil():
    """Editar perfil del usuario actual"""
    usuario = Usuario.query.get(session['usuario_id'])
    
    if request.method == 'POST':
        nombre_completo = request.form.get('nombre_completo', '').strip()
        password_actual = request.form.get('password_actual', '')
        password_nuevo = request.form.get('password_nuevo', '')
        
        if not nombre_completo:
            flash('El nombre completo es obligatorio', 'warning')
            return render_template('auth/perfil.html', usuario=usuario)
        
        usuario.nombre_completo = nombre_completo
        
        if password_actual:
            if not check_password_hash(usuario.password_hash, password_actual):
                flash('Contraseña actual incorrecta', 'danger')
                return render_template('auth/perfil.html', usuario=usuario)
            
            if password_nuevo:
                usuario.password_hash = generate_password_hash(password_nuevo)
                flash('Contraseña actualizada correctamente', 'success')
        
        db.session.commit()
        flash('Perfil actualizado correctamente', 'success')
        return redirect(url_for('auth.perfil'))
    
    return render_template('auth/perfil.html', usuario=usuario)
