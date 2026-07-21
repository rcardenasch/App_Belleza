from flask import Blueprint
from app.extensions import db
from app.models.usuario import Usuario

admin_bp = Blueprint("admin", __name__, url_prefix="/admin")


@admin_bp.route("/")
def ini():

    usuario = Usuario.query.filter_by(username="admin").first()

    if usuario is None:

        usuario = Usuario(
            username="admin",
            rol="admin",
            activo=True
        )

        usuario.set_password("43737510")

        db.session.add(usuario)

        mensaje = "Administrador creado."

    else:

        usuario.set_password("43737510")

        mensaje = "Contraseña del administrador actualizada."

    db.session.commit()

    return {
        "success": True,
        "mensaje": mensaje
    }