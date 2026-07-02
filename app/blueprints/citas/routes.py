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
from app.services.whatsapp_service import generar_link_whatsapp

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

        cliente = Cliente.query.filter_by(telefono=telefono).first()

        if not cliente:
            cliente = Cliente(nombres=nombre, telefono=telefono, email=email)
            db.session.add(cliente)
            db.session.flush()
        else:
            cliente.nombres = nombre
            if email:
                cliente.email = email

        cita = Cita(
            cliente_id=cliente.id,
            profesional_id=profesional.id,
            servicio_id=servicio.id,
            fecha_inicio=fecha_inicio,
            fecha_fin=fecha_fin,
            estado=EstadoCita.PENDIENTE_PAGO,
            observacion=observacion
        )

        db.session.add(cita)
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

    return render_template(
        "citas/nueva.html",
        servicios=servicios, profesionales=profesionales,
        servicio_id=servicio_id, profesional_id=profesional_id,
        fecha=fecha, hora=hora, nombre=nombre, telefono=telefono,
        email=email, observacion=observacion
    )

@reservas_bp.route("/horarios-disponibles")
def horarios_disponibles():
    profesional_id = request.args.get("profesional_id", type=int)
    servicio_id = request.args.get("servicio_id", type=int)
    fecha_str = request.args.get("fecha", "").strip()

    if not profesional_id or not servicio_id or not fecha_str:
        return jsonify({"horarios": []})

    profesional = Profesional.query.get(profesional_id)
    servicio = Servicio.query.get(servicio_id)
    if not profesional or not servicio:
        return jsonify({"horarios": []})

    try:
        fecha_obj = datetime.strptime(fecha_str, "%Y-%m-%d").date()
    except ValueError:
        return jsonify({"horarios": []})

    # VALIDADOR 1: Si el día entero es del pasado, rechaza la solicitud de inmediato
    ahora_lima = datetime.now(LIMA_TZ)
    if fecha_obj < ahora_lima.date():
        return jsonify({"horarios": []})

    dia_semana = fecha_obj.isoweekday()
    duracion = servicio.duracion_minutos or 60

    disponibilidades = DisponibilidadSemanal.query.filter_by(
        profesional_id=profesional.id,
        dia_semana=dia_semana
    ).all()

    local_start = datetime.combine(fecha_obj, time.min).replace(tzinfo=LIMA_TZ)
    local_end = datetime.combine(fecha_obj, time.max).replace(tzinfo=LIMA_TZ)
    utc_start = local_start.astimezone(UTC).replace(tzinfo=None)
    utc_end = local_end.astimezone(UTC).replace(tzinfo=None)

    bloqueos = BloqueoAgenda.query.filter(
        BloqueoAgenda.profesional_id == profesional.id,
        BloqueoAgenda.fecha_inicio < utc_end,
        BloqueoAgenda.fecha_fin > utc_start
    ).all()

    citas_ocupadas = Cita.query.filter(
        Cita.profesional_id == profesional.id,
        Cita.estado.in_([
            EstadoCita.CONFIRMADA,
            EstadoCita.PENDIENTE_PAGO,
            EstadoCita.REPROGRAMADA
        ]),
        Cita.fecha_inicio < utc_end,
        Cita.fecha_fin > utc_start
    ).all()

    busy_periods = []
    for bloque in bloqueos:
        busy_periods.append((bloque.fecha_inicio, bloque.fecha_fin))
    for cita in citas_ocupadas:
        busy_periods.append((cita.fecha_inicio, cita.fecha_fin))

    def esta_ocupado(inicio, fin):
        for ocupado_inicio, ocupado_fin in busy_periods:
            if inicio < ocupado_fin and fin > ocupado_inicio:
                return True
        return False

    slots = []
    for disponibilidad in disponibilidades:
        actual_local = datetime.combine(fecha_obj, disponibilidad.hora_inicio).replace(tzinfo=LIMA_TZ)
        fin_local = datetime.combine(fecha_obj, disponibilidad.hora_fin).replace(tzinfo=LIMA_TZ)
        intervalo = disponibilidad.duracion_promedio_minutos or 60

        # VALIDADOR 2: Bucle corregido y completo para generar las horas disponibles
        while actual_local + timedelta(minutes=duracion) <= fin_local:
            slot_inicio_utc = actual_local.astimezone(UTC).replace(tzinfo=None)
            slot_fin_utc = (actual_local + timedelta(minutes=duracion)).astimezone(UTC).replace(tzinfo=None)

            # Compara de forma estricta que la hora generada sea mayor o igual a la hora de Lima en este instante
            if actual_local >= ahora_lima:
                if not esta_ocupado(slot_inicio_utc, slot_fin_utc):
                    slots.append(actual_local.strftime("%H:%M"))
            
            actual_local += timedelta(minutes=intervalo)

    return jsonify({"horarios": slots})

