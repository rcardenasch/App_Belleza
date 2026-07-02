from flask import (
    Blueprint,
    flash,
    jsonify,
    redirect,
    render_template,
    request,
    url_for
)

from app.extensions import db
from app.models.disponibilidad import DisponibilidadSemanal
from app.models.profesional import Profesional
from app.models.servicio import Servicio

profesionales_bp = Blueprint(
    "profesionales",
    __name__,
    url_prefix="/profesionales"
)

DIA_SEMANA = {
    1: "Lunes",
    2: "Martes",
    3: "Miércoles",
    4: "Jueves",
    5: "Viernes",
    6: "Sábado",
    7: "Domingo"
}

@profesionales_bp.route("/horarios", methods=["GET", "POST"])
def horarios():

    profesionales = Profesional.query.filter_by(
        activo=True
    ).all()

    if request.method == "POST":
        profesional_id = request.form.get("profesional_id", type=int)
        dia_semana = request.form.get("dia_semana", type=int)
        hora_inicio = request.form.get("hora_inicio", "").strip()
        hora_fin = request.form.get("hora_fin", "").strip()
        duracion_promedio = request.form.get("duracion_promedio", type=int)

        profesional = Profesional.query.get(profesional_id)

        if not profesional:
            flash("Profesional no válido.", "danger")
            return redirect(url_for("profesionales.horarios"))

        if not (dia_semana and hora_inicio and hora_fin):
            flash("Completa todos los campos del horario.", "danger")
            return redirect(url_for("profesionales.horarios"))

        if hora_inicio >= hora_fin:
            flash("La hora de inicio debe ser anterior a la hora de fin.", "danger")
            return redirect(url_for("profesionales.horarios"))

        disponibilidad = DisponibilidadSemanal(
            profesional_id=profesional.id,
            dia_semana=dia_semana,
            hora_inicio=hora_inicio,
            hora_fin=hora_fin,
            duracion_promedio_minutos=duracion_promedio or 60
        )

        db.session.add(disponibilidad)
        db.session.commit()

        flash("Horario agregado correctamente.", "success")
        return redirect(url_for("profesionales.horarios"))

    horarios = DisponibilidadSemanal.query.join(
        Profesional,
        DisponibilidadSemanal.profesional_id == Profesional.id
    ).order_by(
        Profesional.nombres,
        DisponibilidadSemanal.dia_semana,
        DisponibilidadSemanal.hora_inicio
    ).all()

    return render_template(
        "profesionales/horarios.html",
        profesionales=profesionales,
        horarios=horarios,
        dia_semana=DIA_SEMANA
    )

@profesionales_bp.route("/horarios-profesional", methods=["GET", "POST"])
def horarios_profesional():
    profesionales = Profesional.query.filter_by(activo=True).order_by(Profesional.nombres).all()
    servicios = Servicio.query.filter_by(activo=True).order_by(Servicio.nombre).all()

    if request.method == "POST":
        profesional_id = request.form.get("profesional_id", type=int)
        servicio_id = request.form.get("servicio_id", type=int)
        action = request.form.get("action", "add")

        profesional = Profesional.query.get_or_404(profesional_id)
        servicio = Servicio.query.get_or_404(servicio_id)

        if action == "add":
            if servicio in profesional.servicios:
                flash("El servicio ya está asignado a este profesional.", "warning")
            else:
                profesional.servicios.append(servicio)
                db.session.commit()
                flash("Servicio asignado al profesional.", "success")
        elif action == "remove":
            if servicio in profesional.servicios:
                profesional.servicios.remove(servicio)
                db.session.commit()
                flash("Asignación eliminada.", "success")
            else:
                flash("La asignación no existe.", "warning")
        return redirect(url_for("profesionales.horarios_profesional"))

    return render_template(
        "profesionales/horarios_profesional.html",
        profesionales=profesionales,
        servicios=servicios
    )

@profesionales_bp.route("/admin/horarios")
def horarios_admin():
    return redirect(url_for("profesionales.horarios"))

@profesionales_bp.route("/horarios/eliminar/<int:horario_id>")
def eliminar_horario(horario_id):

    horario = DisponibilidadSemanal.query.get_or_404(horario_id)
    db.session.delete(horario)
    db.session.commit()
    flash("Horario eliminado.", "success")
    return redirect(url_for("profesionales.horarios"))

@profesionales_bp.route("/<int:profesional_id>/horarios-json")
def horarios_json(profesional_id):

    horarios = DisponibilidadSemanal.query.filter_by(
        profesional_id=profesional_id
    ).order_by(
        DisponibilidadSemanal.dia_semana,
        DisponibilidadSemanal.hora_inicio
    ).all()

    return jsonify({
        "horarios": [
            {
                "dia_semana": horario.dia_semana,
                "hora_inicio": horario.hora_inicio.strftime("%H:%M"),
                "hora_fin": horario.hora_fin.strftime("%H:%M")
            }
            for horario in horarios
        ]
    })
