from flask import Blueprint, render_template
from app.models.servicio import Servicio
from app.models.profesional import Profesional
from app.models.galeria import Galeria

landing_bp = Blueprint(
    "landing",
    __name__
)

@landing_bp.route("/")
def inicio():

    servicios = Servicio.query.filter_by(
        activo=True
    ).all()

    profesionales = Profesional.query.filter_by(
        activo=True
    ).all()

    resultados = Galeria.query.limit(
        12
    ).all()

    return render_template(
        "landing/index.html",
        servicios=servicios,
        resultados=resultados,
        profesionales=profesionales
    )