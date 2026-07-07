from datetime import datetime, timedelta, time
from zoneinfo import ZoneInfo

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
from app.models.bloqueo import BloqueoAgenda
from app.models.cita import Cita, EstadoCita
from app.models.cliente import Cliente
from app.models.disponibilidad import DisponibilidadSemanal
from app.models.profesional import Profesional
from app.models.servicio import Servicio
from app.services.agenda_service import AgendaService
from app.services.database_service import DatabaseService
from app.services.notificacion_service import NotificacionService
from app.services.whatsapp_service import generar_link_whatsapp
import re

reservas_bp = Blueprint(
    "reservas",
    __name__,
    url_prefix="/reservar"
)

LIMA_TZ = ZoneInfo("America/Lima")
UTC = ZoneInfo("UTC")

@reservas_bp.route("/", methods=["GET", "POST"])
def nueva():
    servicios = Servicio.query.filter_by(activo=True).all()
    profesionales = Profesional.query.filter_by(activo=True).all()

    servicio_id = request.args.get("servicio_id", type=int)
    profesional_id = request.args.get("profesional_id", type=int)
    fecha = request.args.get("fecha", "")
    hora = request.args.get("hora", "")

    nombre = ""
    telefono = ""
    email = ""
    observacion = ""

    if request.method == "POST":
        nombre = request.form.get("nombre", "").strip()
        telefono = request.form.get("telefono", "").strip()
        email = request.form.get("email", "").strip()
        servicio_id = request.form.get("servicio_id", type=int)
        profesional_id = request.form.get("profesional_id", type=int)
        fecha = request.form.get("fecha", "").strip()
        hora = request.form.get("hora", "").strip()
        observacion = request.form.get("observacion", "").strip()

        # Normalizamos los datos de entrada
        nombre = " ".join(nombre.split()).strip().title()
        telefono = telefono.strip()
        email = email.strip().lower() if email else None

        if not re.fullmatch(r"9\d{8}", telefono):
            flash(
                "Número de teléfono inválido.",
                "warning"
            )
            return redirect(url_for("reservas.nueva", servicio_id=servicio_id, profesional_id=profesional_id, fecha=fecha, hora=hora,email=email, observacion=observacion))

        if not (nombre and telefono and servicio_id and profesional_id and fecha and hora):
            flash("Por favor completa todos los campos obligatorios.", "danger")
            return render_template(
                "citas/nueva.html",
                servicios=servicios, profesionales=profesionales,
                servicio_id=servicio_id, profesional_id=profesional_id,
                fecha=fecha, hora=hora, nombre=nombre, telefono=telefono,
                email=email, observacion=observacion
            )

        servicio = Servicio.query.get(servicio_id)
        profesional = Profesional.query.get(profesional_id)

        if not servicio or not profesional:
            flash("Servicio o profesional no válido.", "danger")
            return render_template(
                "citas/nueva.html",
                servicios=servicios, profesionales=profesionales,
                servicio_id=servicio_id, profesional_id=profesional_id,
                fecha=fecha, hora=hora, nombre=nombre, telefono=telefono,
                email=email, observacion=observacion
            )

        try:
            # Reconstruimos la fecha y hora enviada por el formulario en la zona de Lima
            fecha_inicio_local = datetime.strptime(
                f"{fecha} {hora}",
                "%Y-%m-%d %H:%M"
            ).replace(tzinfo=LIMA_TZ)
            
            # VALIDADOR CRÍTICO: Compara año, mes, día, hora y minuto contra el tiempo real de Lima
            ahora_lima = datetime.now(LIMA_TZ)
            if fecha_inicio_local < ahora_lima:
                flash("La fecha u hora seleccionada ya ha pasado. Por favor, elige un horario futuro.", "danger")
                return render_template(
                    "citas/nueva.html",
                    servicios=servicios, profesionales=profesionales,
                    servicio_id=servicio_id, profesional_id=profesional_id,
                    fecha=fecha, hora=hora, nombre=nombre, telefono=telefono,
                    email=email, observacion=observacion
                )
                
            fecha_inicio = fecha_inicio_local.astimezone(UTC).replace(tzinfo=None)
        except ValueError:
            flash("Fecha u hora no válidas.", "danger")
            return render_template(
                "citas/nueva.html",
                servicios=servicios, profesionales=profesionales,
                servicio_id=servicio_id, profesional_id=profesional_id,
                fecha=fecha, hora=hora, nombre=nombre, telefono=telefono,
                email=email, observacion=observacion
                )

        duracion = servicio.duracion_minutos or 60
        fecha_fin = fecha_inicio + timedelta(minutes=duracion)
        
        cliente = Cliente.query.filter_by(
            nombres=nombre,
            telefono=telefono
        ).first()

        if not cliente:

            cliente = Cliente(
                nombres=nombre,
                telefono=telefono,
                email=email
            )

            db.session.add(cliente)
            db.session.flush()


        ok, mensaje = AgendaService.validar_disponibilidad(
            profesional.id,
            fecha_inicio,
            fecha_fin

        )

        if not ok:

            flash(mensaje, "warning")

            return render_template(
                "citas/nueva.html",servicios=servicios, profesionales=profesionales,
                servicio_id=servicio_id, profesional_id=profesional_id,
                fecha=fecha, hora=hora, nombre=nombre, telefono=telefono,
                email=email, observacion=observacion
            )

        cita = Cita(

            cliente_id=cliente.id,
            cliente_nombre=nombre,
            cliente_telefono=telefono,
            cliente_email=email,
            profesional_id=profesional.id,
            servicio_id=servicio.id,
            fecha_inicio=fecha_inicio,
            fecha_fin=fecha_fin,
            estado=EstadoCita.PENDIENTE_PAGO,
            observacion=observacion
        )

        db.session.add(cita)

        if not DatabaseService.commit(
                error_message="No fue posible registrar la reserva."
        ):
            return render_template(...)

        NotificacionService.reserva_confirmada(cita) # para el cliente  
        NotificacionService.aviso_administrador(cita) # para el administrador

        db.session.commit()

        whatsapp_text = (
            f"¡Tu reserva está confirmada!\n"
            f"Servicio: {servicio.nombre}\n"
            f"Profesional: {profesional.nombres}\n"
            f"Fecha: {fecha}\n"
            f"Hora: {hora}\n"
            f"Observaciones: {observacion or 'Ninguna'}\n\n"
            f"Puedes tomar una captura de pantalla y enviarla a tu WhatsApp para guardar esta confirmación."
        )

        whatsapp_url = generar_link_whatsapp(None, whatsapp_text)

        return render_template(
            "citas/confirmacion.html",
            nombre=nombre, telefono=telefono, email=email,
            servicio=servicio, profesional=profesional,
            fecha=fecha, hora=hora, observacion=observacion,
            whatsapp_url=whatsapp_url
        )
    

    # ← Este return va fuera del if
    return render_template(
        "citas/nueva.html",
        servicios=servicios,
        profesionales=profesionales,
        servicio_id=servicio_id,
        profesional_id=profesional_id,
        fecha=fecha,
        hora=hora,
        nombre=nombre,
        telefono=telefono,
        email=email,
        observacion=observacion
    )

@reservas_bp.route("/horarios-disponibles")
def horarios_disponibles():

    profesional_id = request.args.get(
        "profesional_id",
        type=int
    )

    servicio_id = request.args.get(
        "servicio_id",
        type=int
    )

    fecha = request.args.get(
        "fecha",
        ""
    )

    horarios = AgendaService.obtener_horarios_disponibles(
        profesional_id,
        servicio_id,
        fecha
    )

    return jsonify({
        "horarios": horarios
    })

