from flask import (
    Blueprint,
    render_template
)

auth_bp = Blueprint(
    "auth",
    __name__,
    url_prefix="/auth"
)

@auth_bp.route("/login")
def login():

    return render_template(
        "auth/login.html"
    )

from flask import request, redirect, url_for, flash
from flask_login import login_user, logout_user, current_user
from app.models.usuario import Usuario
from app.extensions import limiter


@auth_bp.route('/login', methods=['GET', 'POST'])
@limiter.limit('5 per minute')
def login_post():
    if request.method == 'GET':
        return render_template('auth/login.html')

    username = request.form.get('username', '').strip()
    password = request.form.get('password', '').strip()

    user = Usuario.query.filter_by(username=username).first()
    if not user or not user.check_password(password):
        flash('Usuario o contraseña inválidos.', 'danger')
        return redirect(url_for('auth.login'))

    if not user.activo:
        flash('Cuenta desactivada.', 'danger')
        return redirect(url_for('auth.login'))

    login_user(user)
    flash('Has iniciado sesión.', 'success')
    next_page = request.args.get('next') or url_for('admin.panel')
    return redirect(next_page)


@auth_bp.route('/logout')
def logout():
    logout_user()
    flash('Sesión cerrada.', 'success')
    return redirect(url_for('auth.login'))