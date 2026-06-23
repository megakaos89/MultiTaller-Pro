from flask import Blueprint, render_template, request, redirect, url_for, flash
from werkzeug.security import generate_password_hash
try:
    from ..models import db, Usuario, Configuracion
except Exception:
    from models import db, Usuario, Configuracion

setup_bp = Blueprint('setup', __name__, template_folder='..\templates')


@setup_bp.route('/setup', methods=['GET', 'POST'])
def setup():
    """Pantalla de configuración inicial: crear admin y datos del taller"""
    # Si ya existe administrador, redirigir
    if db.session.query(Usuario).filter_by(rol='admin').first():
        flash('La configuración inicial ya fue completada.', 'info')
        return redirect(url_for('auth.login'))

    if request.method == 'POST':
        username = request.form.get('username', 'admin').strip()
        password = request.form.get('password', '')
        password_confirm = request.form.get('password_confirm', '')

        nombre_taller = request.form.get('nombre_taller', '').strip()
        direccion_taller = request.form.get('direccion_taller', '').strip()
        telefono_taller = request.form.get('telefono_taller', '').strip()
        email_contacto = request.form.get('email_contacto', '').strip()

        if not username or not password:
            flash('Usuario y contraseña son obligatorios', 'warning')
            return render_template('setup.html')

        if password != password_confirm:
            flash('Las contraseñas no coinciden', 'warning')
            return render_template('setup.html')

        if len(password) < 6:
            flash('La contraseña debe tener al menos 6 caracteres', 'warning')
            return render_template('setup.html')

        # Crear usuario admin
        nuevo_admin = Usuario(
            username=username,
            password_hash=generate_password_hash(password),
            nombre_completo='Administrador',
            rol='admin',
            activo=True
        )
        db.session.add(nuevo_admin)

        # Guardar datos del taller en configuración
        def upsert_config(clave, valor, descripcion=''):
            if not valor:
                return
            existing = Configuracion.query.filter_by(clave=clave).first()
            if existing:
                existing.valor = valor
            else:
                conf = Configuracion(clave=clave, valor=valor, descripcion=descripcion)
                db.session.add(conf)

        upsert_config('nombre_taller', nombre_taller, 'Nombre del taller')
        upsert_config('direccion_taller', direccion_taller, 'Dirección del taller')
        upsert_config('telefono_taller', telefono_taller, 'Teléfono del taller')
        upsert_config('email_contacto', email_contacto, 'Email de contacto para licencias')

        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            flash(f'Error creando el usuario admin: {e}', 'danger')
            return render_template('setup.html')

        flash('Configuración inicial completada. Inicia sesión con el usuario administrador.', 'success')
        return redirect(url_for('auth.login'))

    return render_template('setup.html')
