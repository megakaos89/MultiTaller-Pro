"""
Blueprint para configuración del sistema
"""

from flask import Blueprint, render_template, redirect, url_for, flash, request, session
from models import db, Configuracion
from routes.auth import login_required, admin_required
import json

configuracion_bp = Blueprint('configuracion', __name__)


@configuracion_bp.route('/configuracion')
@login_required
@admin_required
def ver_configuracion():
    """Ver configuración del sistema"""
    configs = Configuracion.query.all()
    configs_dict = {c.clave: c.valor for c in configs}
    
    return render_template('configuracion/ver.html', configs=configs_dict)


@configuracion_bp.route('/configuracion/editar', methods=['GET', 'POST'])
@login_required
@admin_required
def editar_configuracion():
    """Editar configuración del sistema"""
    if request.method == 'POST':
        # Configuración general
        configs_a_guardar = {
            'nombre_taller': request.form.get('nombre_taller', 'Mi Taller'),
            'direccion_taller': request.form.get('direccion_taller', ''),
            'telefono_taller': request.form.get('telefono_taller', ''),
            'moneda_principal': request.form.get('moneda_principal', 'CUP'),
            'moneda_secundaria': request.form.get('moneda_secundaria', 'MLC'),
            'tasa_cambio': request.form.get('tasa_cambio', '1.0'),
            'regimen_tributario': request.form.get('regimen_tributario', 'general'),
            'seguridad_social_porcentaje': request.form.get('seguridad_social_porcentaje', '5'),
            'cuota_fija_mensual': request.form.get('cuota_fija_mensual', '500'),
            'email_contacto': request.form.get('email_contacto', 'megashopsc20@gmail.com'),
            'telefono_contacto': request.form.get('telefono_contacto', '+53 50625350'),
            'qbapay_link': request.form.get('qbapay_link', ''),
            'btc_address': request.form.get('btc_address', ''),
            'usdt_address': request.form.get('usdt_address', '')
        }
        
        # Tramos ISIP (JSON)
        tramos_isip = []
        for i in range(5):
            hasta = request.form.get(f'isip_hasta_{i}', '').strip()
            porcentaje = request.form.get(f'isip_porcentaje_{i}', '').strip()
            
            if hasta and porcentaje:
                tramos_isip.append({
                    'hasta': float(hasta) if hasta else None,
                    'porcentaje': float(porcentaje)
                })
        
        configs_a_guardar['isip_tramos'] = json.dumps(tramos_isip)
        
        # Guardar cada configuración
        for clave, valor in configs_a_guardar.items():
            conf = Configuracion.query.filter_by(clave=clave).first()
            if conf:
                conf.valor = str(valor)
            else:
                conf = Configuracion(clave=clave, valor=str(valor))
                db.session.add(conf)
        
        db.session.commit()
        flash('Configuración actualizada correctamente', 'success')
        return redirect(url_for('configuracion.ver_configuracion'))
    
    configs = Configuracion.query.all()
    configs_dict = {c.clave: c.valor for c in configs}
    
    # Parsear tramos ISIP
    tramos_isip = []
    if 'isip_tramos' in configs_dict:
        try:
            tramos_isip = json.loads(configs_dict['isip_tramos'])
        except:
            tramos_isip = []
    
    # Asegurar 5 tramos
    while len(tramos_isip) < 5:
        tramos_isip.append({'hasta': '', 'porcentaje': 0})
    
    return render_template('configuracion/editar.html', 
                         configs=configs_dict,
                         tramos_isip=tramos_isip)


@configuracion_bp.route('/configuracion/restaurar_valores')
@login_required
@admin_required
def restaurar_valores():
    """Restaurar valores por defecto de configuración"""
    from app import inicializar_configuracion
    
    # Eliminar configuraciones existentes
    Configuracion.query.delete()
    db.session.commit()
    
    # Recrear con valores por defecto
    inicializar_configuracion()
    
    flash('Configuración restaurada a valores por defecto', 'success')
    return redirect(url_for('configuracion.ver_configuracion'))
