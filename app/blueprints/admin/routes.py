from flask import (
    Blueprint,
    flash,
    redirect,
    render_template,
    request,
    url_for
)
from app.extensions import db
from datetime import datetime, timedelta, time
from zoneinfo import ZoneInfo
from app.models.bloqueo import BloqueoAgenda
from app.models.disponibilidad import DisponibilidadSemanal
from app.models.profesional import Profesional
from app.models.cita import Cita, EstadoCita
from app.models.servicio import Servicio
from app.models.galeria import Galeria
from app.models.cliente import Cliente
from app.models.usuario import Usuario
from flask_login import current_user, login_required
from flask import request
from decimal import Decimal, InvalidOperation

admin_bp = Blueprint(
    "admin",
    __name__,
    url_prefix="/admin"
)


@admin_bp.before_request
def admin_protect():
    # Proteger todo el blueprint admin: requiere autentificación y rol 'admin'
    if not current_user.is_authenticated:
        return redirect(url_for('auth.login', next=request.path))
    if getattr(current_user, 'rol', None) != 'admin':
        flash('Acceso denegado: se requieren permisos de administrador.', 'danger')
        return redirect(url_for('landing.index'))

DIA_SEMANA = {
    1: "Lunes",
    2: "Martes",
    3: "Miércoles",
    4: "Jueves",
    5: "Viernes",
    6: "Sábado",
    7: "Domingo"
}

@admin_bp.route("/")
def panel():
    profesionales = Profesional.query.filter_by(activo=True).all()
    servicios = Servicio.query.filter_by(activo=True).all()
    resultados = Galeria.query.order_by(Galeria.created_at.desc()).limit(8).all()
    clientes = Cliente.query.order_by(Cliente.id.desc()).limit(8).all()
    bloqueos = BloqueoAgenda.query.order_by(BloqueoAgenda.fecha_inicio.desc()).limit(8).all()

    return render_template(
        "admin/panel.html",
        profesionales=profesionales,
        servicios=servicios,
        resultados=resultados,
        clientes=clientes,
        bloqueos=bloqueos
    )
#========================================
# CRUD Profesionales
#========================================

@admin_bp.route("/profesionales")
def profesionales_admin():
    profesionales = Profesional.query.order_by(Profesional.nombres).all()
    return render_template("admin/profesionales.html", profesionales=profesionales, profesional=None)

@admin_bp.route("/profesionales/nuevo", methods=["POST"])
def nuevo_profesional():
    nombres = request.form.get("nombres", "").strip()
    telefono = request.form.get("telefono", "").strip()
    foto_url = request.form.get("foto_url", "").strip()
    activo = request.form.get("activo") == "on"

    if not nombres:
        flash("El nombre es obligatorio.", "danger")
        return redirect(url_for("admin.profesionales_admin"))

    profesional = Profesional(
        nombres=nombres,
        telefono=telefono,
        foto_url=foto_url,
        activo=activo
    )
    db.session.add(profesional)
    db.session.commit()

    flash("Profesional creado correctamente.", "success")
    return redirect(url_for("admin.profesionales_admin"))

@admin_bp.route("/profesionales/editar/<int:profesional_id>", methods=["GET", "POST"])
def editar_profesional(profesional_id):
    profesional = Profesional.query.get_or_404(profesional_id)
    if request.method == "POST":
        profesional.nombres = request.form.get("nombres", "").strip()
        profesional.telefono = request.form.get("telefono", "").strip()
        profesional.foto_url = request.form.get("foto_url", "").strip()
        profesional.activo = request.form.get("activo") == "on"

        if not profesional.nombres:
            flash("El nombre es obligatorio.", "danger")
            return redirect(url_for("admin.editar_profesional", profesional_id=profesional.id))

        db.session.commit()
        flash("Profesional actualizado correctamente.", "success")
        return redirect(url_for("admin.profesionales_admin"))

    profesionales = Profesional.query.order_by(Profesional.nombres).all()
    return render_template(
        "admin/profesionales.html",
        profesionales=profesionales,
        profesional=profesional
    )

@admin_bp.route("/profesionales/eliminar/<int:profesional_id>", methods=["POST"])
def eliminar_profesional(profesional_id):
    profesional = Profesional.query.get_or_404(profesional_id)
    db.session.delete(profesional)
    db.session.commit()
    flash("Profesional eliminado.", "success")
    return redirect(url_for("admin.profesionales_admin"))

LIMA_TZ = ZoneInfo("America/Lima")
UTC = ZoneInfo("UTC")

# =====================================
# CRUD Servicios
# =====================================

@admin_bp.route("/servicios")
def servicios_admin():
    servicios = Servicio.query.order_by(Servicio.nombre).all()
    return render_template("admin/servicios.html", servicios=servicios, servicio=None)

@admin_bp.route("/servicios/nuevo", methods=["POST"])
def nuevo_servicio():
    nombre = request.form.get("nombre", "").strip()
    descripcion = request.form.get("descripcion", "").strip()
    duracion_minutos = request.form.get("duracion_minutos", type=int)
    precio_raw = request.form.get("precio", "").strip()
    color = request.form.get("color", "#3788d8").strip()
    imagen_url = request.form.get("imagen_url", "").strip()
    video_url = request.form.get("video_url", "").strip()
    activo = request.form.get("activo") == "on"

    if not nombre:
        flash("El nombre del servicio es obligatorio.", "danger")
        return redirect(url_for("admin.servicios_admin"))

    if not duracion_minutos or duracion_minutos <= 0:
        flash("La duración debe ser un número entero mayor a 0.", "danger")
        return redirect(url_for("admin.servicios_admin"))

    try:
        precio = Decimal(precio_raw)
        if precio < 0:
            raise ValueError
    except (InvalidOperation, ValueError):
        flash("El precio debe ser un número válido igual o mayor a 0.", "danger")
        return redirect(url_for("admin.servicios_admin"))

    servicio = Servicio(
        nombre=nombre,
        descripcion=descripcion or None,
        duracion_minutos=duracion_minutos,
        precio=precio,
        color=color,
        imagen_url=imagen_url or None,
        video_url=video_url or None,
        activo=activo
    )
    db.session.add(servicio)
    db.session.commit()

    flash("Servicio creado correctamente.", "success")
    return redirect(url_for("admin.servicios_admin"))

@admin_bp.route("/servicios/editar/<int:servicio_id>", methods=["GET", "POST"])
def editar_servicio(servicio_id):
    servicio = Servicio.query.get_or_404(servicio_id)
    if request.method == "POST":
        nombre = request.form.get("nombre", "").strip()
        duracion_minutos = request.form.get("duracion_minutos", type=int)
        precio_raw = request.form.get("precio", "").strip()
        
        if not nombre:
            flash("El nombre del servicio es obligatorio.", "danger")
            return redirect(url_for("admin.editar_servicio", servicio_id=servicio.id))

        if not duracion_minutos or duracion_minutos <= 0:
            flash("La duración debe ser un número entero mayor a 0.", "danger")
            return redirect(url_for("admin.editar_servicio", servicio_id=servicio.id))

        try:
            precio = Decimal(precio_raw)
            if precio < 0:
                raise ValueError
        except (InvalidOperation, ValueError):
            flash("El precio debe ser un número válido igual o mayor a 0.", "danger")
            return redirect(url_for("admin.editar_servicio", servicio_id=servicio.id))

        servicio.nombre = nombre
        servicio.descripcion = request.form.get("descripcion", "").strip() or None
        servicio.duracion_minutos = duracion_minutos
        servicio.precio = precio
        servicio.color = request.form.get("color", "#3788d8").strip()
        servicio.imagen_url = request.form.get("imagen_url", "").strip() or None
        servicio.video_url = request.form.get("video_url", "").strip() or None
        servicio.activo = request.form.get("activo") == "on"

        db.session.commit()
        flash("Servicio actualizado correctamente.", "success")
        return redirect(url_for("admin.servicios_admin"))

    servicios = Servicio.query.order_by(Servicio.nombre).all()
    return render_template(
        "admin/servicios.html",
        servicios=servicios,
        servicio=servicio
    )

@admin_bp.route("/servicios/eliminar/<int:servicio_id>", methods=["POST"])
def eliminar_servicio(servicio_id):
    servicio = Servicio.query.get_or_404(servicio_id)
    db.session.delete(servicio)
    db.session.commit()
    flash("Servicio eliminado.", "success")
    return redirect(url_for("admin.servicios_admin"))

LIMA_TZ = ZoneInfo("America/Lima")
UTC = ZoneInfo("UTC")

# ======================================
# CRUD Horarios
# ========================================
@admin_bp.route("/horarios", methods=["GET", "POST"])
def horarios_admin():
    profesionales = Profesional.query.order_by(Profesional.nombres).all()
    horarios = DisponibilidadSemanal.query.order_by(
        DisponibilidadSemanal.dia_semana,
        DisponibilidadSemanal.hora_inicio
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
            return redirect(url_for("admin.horarios_admin"))

        if not (dia_semana and hora_inicio and hora_fin):
            flash("Completa todos los campos del horario.", "danger")
            return redirect(url_for("admin.horarios_admin"))

        if hora_inicio >= hora_fin:
            flash("La hora de inicio debe ser anterior a la hora de fin.", "danger")
            return redirect(url_for("admin.horarios_admin"))

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
        return redirect(url_for("admin.horarios_admin"))

    return render_template(
        "admin/horarios.html",
        profesionales=profesionales,
        horarios=horarios,
        dia_semana=DIA_SEMANA,
        horario=None
    )

# ======================================
# CRUD bloqueos
# ========================================

@admin_bp.route("/bloqueos", methods=["GET", "POST"])
def bloqueos_admin():
    profesionales = Profesional.query.order_by(Profesional.nombres).all()
    bloqueos = BloqueoAgenda.query.order_by(BloqueoAgenda.fecha_inicio.desc()).all()

    if request.method == "POST":
        profesional_id = request.form.get("profesional_id", type=int)
        fecha_inicio_fecha = request.form.get("fecha_inicio_fecha", "").strip()
        fecha_inicio_hora = request.form.get("fecha_inicio_hora", "").strip()
        fecha_fin_fecha = request.form.get("fecha_fin_fecha", "").strip()
        fecha_fin_hora = request.form.get("fecha_fin_hora", "").strip()
        motivo = request.form.get("motivo", "").strip()

        profesional = Profesional.query.get(profesional_id)
        if not profesional:
            flash("Profesional no válido.", "danger")
            return redirect(url_for("admin.bloqueos_admin"))

        if not (fecha_inicio_fecha and fecha_inicio_hora and fecha_fin_fecha and fecha_fin_hora):
            flash("Completa todas las fechas y horas.", "danger")
            return redirect(url_for("admin.bloqueos_admin"))

        try:
            inicio_local = datetime.strptime(
                f"{fecha_inicio_fecha} {fecha_inicio_hora}",
                "%Y-%m-%d %H:%M"
            ).replace(tzinfo=LIMA_TZ)
            fin_local = datetime.strptime(
                f"{fecha_fin_fecha} {fecha_fin_hora}",
                "%Y-%m-%d %H:%M"
            ).replace(tzinfo=LIMA_TZ)
        except ValueError:
            flash("Fecha u hora de bloqueo no válidas.", "danger")
            return redirect(url_for("admin.bloqueos_admin"))

        if fin_local <= inicio_local:
            flash("El fin del bloqueo debe ser posterior al inicio.", "danger")
            return redirect(url_for("admin.bloqueos_admin"))

        inicio_utc = inicio_local.astimezone(UTC).replace(tzinfo=None)
        fin_utc = fin_local.astimezone(UTC).replace(tzinfo=None)

        # Validar solapamiento con otros bloqueos
        conflict_bloqueos = BloqueoAgenda.query.filter(
            BloqueoAgenda.profesional_id == profesional.id,
            BloqueoAgenda.fecha_inicio < fin_utc,
            BloqueoAgenda.fecha_fin > inicio_utc
        ).all()
        if conflict_bloqueos:
            flash("El bloqueo se superpone con otro bloqueo existente.", "danger")
            return redirect(url_for("admin.bloqueos_admin"))

        # Validar solapamiento con citas existentes (pendientes/confirmadas/reprogramadas)
        conflict_citas = Cita.query.filter(
            Cita.profesional_id == profesional.id,
            Cita.estado.in_([
                EstadoCita.CONFIRMADA,
                EstadoCita.PENDIENTE_PAGO,
                EstadoCita.REPROGRAMADA
            ]),
            Cita.fecha_inicio < fin_utc,
            Cita.fecha_fin > inicio_utc
        ).all()
        if conflict_citas:
            flash("No se puede crear el bloqueo: existen citas programadas en ese intervalo.", "danger")
            return redirect(url_for("admin.bloqueos_admin"))

        bloqueo = BloqueoAgenda(
            profesional_id=profesional.id,
            fecha_inicio=inicio_utc,
            fecha_fin=fin_utc,
            motivo=motivo
        )
        db.session.add(bloqueo)
        db.session.commit()

        flash("Bloqueo agregado correctamente.", "success")
        return redirect(url_for("admin.bloqueos_admin"))

    return render_template(
        "admin/bloqueos.html",
        profesionales=profesionales,
        bloqueos=bloqueos
    )

@admin_bp.route("/bloqueos/editar/<int:bloqueo_id>", methods=["GET", "POST"])
def editar_bloqueo(bloqueo_id):
    bloqueo = BloqueoAgenda.query.get_or_404(bloqueo_id)
    profesionales = Profesional.query.order_by(Profesional.nombres).all()

    if request.method == "POST":
        bloqueo.profesional_id = request.form.get("profesional_id", type=int)
        fecha_inicio_fecha = request.form.get("fecha_inicio_fecha", "").strip()
        fecha_inicio_hora = request.form.get("fecha_inicio_hora", "").strip()
        fecha_fin_fecha = request.form.get("fecha_fin_fecha", "").strip()
        fecha_fin_hora = request.form.get("fecha_fin_hora", "").strip()
        bloqueo.motivo = request.form.get("motivo", "").strip()

        try:
            inicio_local = datetime.strptime(
                f"{fecha_inicio_fecha} {fecha_inicio_hora}",
                "%Y-%m-%d %H:%M"
            ).replace(tzinfo=LIMA_TZ)
            fin_local = datetime.strptime(
                f"{fecha_fin_fecha} {fecha_fin_hora}",
                "%Y-%m-%d %H:%M"
            ).replace(tzinfo=LIMA_TZ)
        except ValueError:
            flash("Fecha u hora de bloqueo no válidas.", "danger")
            return redirect(url_for("admin.editar_bloqueo", bloqueo_id=bloqueo.id))

        if fin_local <= inicio_local:
            flash("El fin del bloqueo debe ser posterior al inicio.", "danger")
            return redirect(url_for("admin.editar_bloqueo", bloqueo_id=bloqueo.id))

        inicio_utc = inicio_local.astimezone(UTC).replace(tzinfo=None)
        fin_utc = fin_local.astimezone(UTC).replace(tzinfo=None)

        # Validar solapamiento con otros bloqueos (excluir el actual)
        conflict_bloqueos = BloqueoAgenda.query.filter(
            BloqueoAgenda.profesional_id == bloqueo.profesional_id,
            BloqueoAgenda.id != bloqueo.id,
            BloqueoAgenda.fecha_inicio < fin_utc,
            BloqueoAgenda.fecha_fin > inicio_utc
        ).all()
        if conflict_bloqueos:
            flash("El bloqueo se superpone con otro bloqueo existente.", "danger")
            return redirect(url_for("admin.editar_bloqueo", bloqueo_id=bloqueo.id))

        # Validar solapamiento con citas existentes
        conflict_citas = Cita.query.filter(
            Cita.profesional_id == bloqueo.profesional_id,
            Cita.estado.in_([
                EstadoCita.CONFIRMADA,
                EstadoCita.PENDIENTE_PAGO,
                EstadoCita.REPROGRAMADA
            ]),
            Cita.fecha_inicio < fin_utc,
            Cita.fecha_fin > inicio_utc
        ).all()
        if conflict_citas:
            flash("No se puede actualizar el bloqueo: existen citas programadas en ese intervalo.", "danger")
            return redirect(url_for("admin.editar_bloqueo", bloqueo_id=bloqueo.id))

        bloqueo.fecha_inicio = inicio_utc
        bloqueo.fecha_fin = fin_utc

        db.session.commit()
        flash("Bloqueo actualizado correctamente.", "success")
        return redirect(url_for("admin.bloqueos_admin"))

    return render_template(
        "admin/bloqueos.html",
        profesionales=profesionales,
        bloqueos=BloqueoAgenda.query.order_by(BloqueoAgenda.fecha_inicio.desc()).all(),
        bloqueo=bloqueo
    )

@admin_bp.route("/bloqueos/eliminar/<int:bloqueo_id>")
def eliminar_bloqueo(bloqueo_id):
    bloqueo = BloqueoAgenda.query.get_or_404(bloqueo_id)
    db.session.delete(bloqueo)
    db.session.commit()
    flash("Bloqueo eliminado.", "success")
    return redirect(url_for("admin.bloqueos_admin"))

# ======================================
# Listar agenda
# ========================================
@admin_bp.route("/agenda")
def agenda_admin():
    """Vista administrativa para ver la agenda por fecha y profesional.

    Muestra una grilla de slots (paso 30 minutos) indicando estados:
    - available: dentro de disponibilidad y sin citas ni bloqueos
    - booked: existe una cita
    - blocked: existe un bloqueo
    - conflict: cita y bloqueo se superponen o cita fuera de disponibilidad
    - service_conflict: la cita tiene un servicio no asignado al profesional
    """
    fecha_str = request.args.get("fecha", datetime.now().date().isoformat())
    profesional_id = request.args.get("profesional_id", type=int)
    servicio_id = request.args.get("servicio_id", type=int)

    try:
        fecha_obj = datetime.strptime(fecha_str, "%Y-%m-%d").date()
    except ValueError:
        fecha_obj = datetime.now().date()

    profesionales = Profesional.query.order_by(Profesional.nombres).all()

    # preparar rango UTC del día
    local_start = datetime.combine(fecha_obj, time.min).replace(tzinfo=LIMA_TZ)
    local_end = datetime.combine(fecha_obj, time.max).replace(tzinfo=LIMA_TZ)
    utc_start = local_start.astimezone(UTC).replace(tzinfo=None)
    utc_end = local_end.astimezone(UTC).replace(tzinfo=None)

    agenda = []

    profs = [p for p in profesionales if (not profesional_id or p.id == profesional_id)]
    for prof in profs:
        # disponibilidades para el día
        dia = fecha_obj.isoweekday()
        disponibilidades = DisponibilidadSemanal.query.filter_by(
            profesional_id=prof.id,
            dia_semana=dia
        ).all()

        # bloqueos y citas del día
        bloqueos = BloqueoAgenda.query.filter(
            BloqueoAgenda.profesional_id == prof.id,
            BloqueoAgenda.fecha_inicio < utc_end,
            BloqueoAgenda.fecha_fin > utc_start
        ).all()

        citas = Cita.query.filter(
            Cita.profesional_id == prof.id,
            Cita.fecha_inicio < utc_end,
            Cita.fecha_fin > utc_start
        ).all()

        # determinar rango de visualización: usar disponibilidades si existen, sino 08:00-20:00
        if disponibilidades:
            min_start = min(d.hora_inicio for d in disponibilidades)
            max_end = max(d.hora_fin for d in disponibilidades)
        else:
            min_start = time(8, 0)
            max_end = time(20, 0)

        slots = []
        cursor_local = datetime.combine(fecha_obj, min_start).replace(tzinfo=LIMA_TZ)
        end_local = datetime.combine(fecha_obj, max_end).replace(tzinfo=LIMA_TZ)
        step = timedelta(minutes=30)

        # helper para verificar solapamientos
        busy_periods = []
        for b in bloqueos:
            busy_periods.append((b.fecha_inicio, b.fecha_fin, 'bloqueo', b))
        for c in citas:
            busy_periods.append((c.fecha_inicio, c.fecha_fin, 'cita', c))

        def overlaps(start_utc, end_utc, period):
            a_start, a_end = period[0], period[1]
            return start_utc < a_end and end_utc > a_start

        while cursor_local < end_local:
            slot_start_local = cursor_local
            slot_end_local = cursor_local + step
            slot_start_utc = slot_start_local.astimezone(UTC).replace(tzinfo=None)
            slot_end_utc = slot_end_local.astimezone(UTC).replace(tzinfo=None)

            # verificar si dentro de alguna disponibilidad
            inside_availability = any(
                datetime.combine(fecha_obj, d.hora_inicio).replace(tzinfo=LIMA_TZ) <= slot_start_local
                and datetime.combine(fecha_obj, d.hora_fin).replace(tzinfo=LIMA_TZ) >= slot_end_local
                for d in disponibilidades
            )

            status = 'outside'
            note = None

            # buscar bloqueos y citas que se superpongan
            slot_blocked = [b for b in bloqueos if overlaps(slot_start_utc, slot_end_utc, (b.fecha_inicio, b.fecha_fin))]
            slot_citas = [c for c in citas if overlaps(slot_start_utc, slot_end_utc, (c.fecha_inicio, c.fecha_fin))]

            if slot_blocked and slot_citas:
                status = 'conflict'
                note = 'Cita y bloqueo se superponen'
            elif slot_blocked:
                status = 'blocked'
                note = slot_blocked[0].motivo
            elif slot_citas:
                # verificar si servicio de la cita pertenece al profesional
                c = slot_citas[0]
                servicio_ok = any(s.id == c.servicio_id for s in prof.servicios)
                if not servicio_ok:
                    status = 'service_conflict'
                    note = f"Servicio no asignado: {c.servicio_id}"
                else:
                    status = 'booked'
                    note = f"Cita #{c.id}"
            elif inside_availability:
                status = 'available'

            slots.append({
                'start': slot_start_local.strftime('%H:%M'),
                'end': slot_end_local.strftime('%H:%M'),
                'status': status,
                'note': note
            })

            cursor_local += step

        agenda.append({
            'profesional': prof,
            'slots': slots
        })

    servicios = Servicio.query.filter_by(activo=True).all()

    return render_template('admin/agenda.html',
                           fecha=fecha_obj.isoformat(),
                           profesionales=profesionales,
                           agenda=agenda,
                           servicios=servicios)


# ======================================
# CRUD horario
# ========================================
@admin_bp.route("/horarios/editar/<int:horario_id>", methods=["GET", "POST"])
def editar_horario(horario_id):
    horario = DisponibilidadSemanal.query.get_or_404(horario_id)
    profesionales = Profesional.query.order_by(Profesional.nombres).all()
    if request.method == "POST":
        horario.profesional_id = request.form.get("profesional_id", type=int)
        horario.dia_semana = request.form.get("dia_semana", type=int)
        horario.hora_inicio = request.form.get("hora_inicio", "").strip()
        horario.hora_fin = request.form.get("hora_fin", "").strip()
        horario.duracion_promedio_minutos = request.form.get("duracion_promedio", type=int) or 60

        if horario.hora_inicio >= horario.hora_fin:
            flash("La hora de inicio debe ser anterior a la hora de fin.", "danger")
            return redirect(url_for("admin.editar_horario", horario_id=horario.id))

        db.session.commit()
        flash("Horario actualizado correctamente.", "success")
        return redirect(url_for("admin.horarios_admin"))

    return render_template(
        "admin/horarios.html",
        profesionales=profesionales,
        horarios=DisponibilidadSemanal.query.order_by(
            DisponibilidadSemanal.dia_semana,
            DisponibilidadSemanal.hora_inicio
        ).all(),
        dia_semana=DIA_SEMANA,
        horario=horario
    )

@admin_bp.route("/horarios/eliminar/<int:horario_id>")
def eliminar_horario(horario_id):
    horario = DisponibilidadSemanal.query.get_or_404(horario_id)
    db.session.delete(horario)
    db.session.commit()
    flash("Horario eliminado.", "success")
    return redirect(url_for("admin.horarios_admin"))

@admin_bp.route("/galeria")
def galeria_admin():
    resultados = Galeria.query.order_by(Galeria.created_at.desc()).all()
    servicios = Servicio.query.filter_by(activo=True).all()
    return render_template("admin/galeria.html", resultados=resultados, servicios=servicios, item=None)

# ======================================
# CRUD Usuario
# ========================================
@admin_bp.route('/usuarios')
def usuarios_admin():
    usuarios = Usuario.query.order_by(Usuario.username).all()
    return render_template('admin/usuarios.html', usuarios=usuarios, usuario=None)


@admin_bp.route('/usuarios/nuevo', methods=['POST'])
def nuevo_usuario():
    username = request.form.get('username', '').strip()
    password = request.form.get('password', '').strip()
    rol = request.form.get('rol', '').strip() or 'user'
    activo = request.form.get('activo') == 'on'

    if not username or not password:
        flash('Usuario y contraseña son obligatorios.', 'danger')
        return redirect(url_for('admin.usuarios_admin'))

    if Usuario.query.filter_by(username=username).first():
        flash('El nombre de usuario ya existe.', 'danger')
        return redirect(url_for('admin.usuarios_admin'))

    user = Usuario(username=username, rol=rol, activo=activo)
    user.set_password(password)
    db.session.add(user)
    db.session.commit()
    flash('Usuario creado correctamente.', 'success')
    return redirect(url_for('admin.usuarios_admin'))


@admin_bp.route('/usuarios/editar/<int:usuario_id>', methods=['GET', 'POST'])
def editar_usuario(usuario_id):
    user = Usuario.query.get_or_404(usuario_id)
    if request.method == 'POST':
        user.username = request.form.get('username', user.username).strip()
        user.rol = request.form.get('rol', user.rol).strip()
        user.activo = request.form.get('activo') == 'on'
        db.session.commit()
        flash('Usuario actualizado.', 'success')
        return redirect(url_for('admin.usuarios_admin'))

    usuarios = Usuario.query.order_by(Usuario.username).all()
    return render_template('admin/usuarios.html', usuarios=usuarios, usuario=user)


@admin_bp.route('/usuarios/eliminar/<int:usuario_id>', methods=['POST'])
def eliminar_usuario(usuario_id):
    user = Usuario.query.get_or_404(usuario_id)
    if user.id == current_user.id:
        flash('No puedes eliminar tu propia cuenta.', 'danger')
        return redirect(url_for('admin.usuarios_admin'))
    db.session.delete(user)
    db.session.commit()
    flash('Usuario eliminado.', 'success')
    return redirect(url_for('admin.usuarios_admin'))


@admin_bp.route('/usuarios/password/<int:usuario_id>', methods=['POST'])
def cambiar_password_usuario(usuario_id):
    user = Usuario.query.get_or_404(usuario_id)
    new_password = request.form.get('new_password', '').strip()
    if not new_password or len(new_password) < 6:
        flash('La nueva contraseña debe tener al menos 6 caracteres.', 'danger')
        return redirect(url_for('admin.usuarios_admin'))
    user.set_password(new_password)
    db.session.commit()
    flash('Contraseña actualizada.', 'success')
    return redirect(url_for('admin.usuarios_admin'))

# ======================================
# CRUD Galeria
# ========================================
@admin_bp.route("/galeria/nuevo", methods=["POST"])
def nuevo_galeria():
    servicio_id = request.form.get("servicio_id", type=int)
    imagen_antes_url = request.form.get("imagen_antes_url", "").strip()
    imagen_despues_url = request.form.get("imagen_despues_url", "").strip()
    instagram_url = request.form.get("instagram_url", "").strip()
    tiktok_url = request.form.get("tiktok_url", "").strip()
    testimonio = request.form.get("testimonio", "").strip()

    if not servicio_id or not imagen_antes_url or not imagen_despues_url:
        flash("Completa el servicio y ambas imágenes.", "danger")
        return redirect(url_for("admin.galeria_admin"))

    galeria = Galeria(
        servicio_id=servicio_id,
        imagen_antes_url=imagen_antes_url,
        imagen_despues_url=imagen_despues_url,
        instagram_url=instagram_url,
        tiktok_url=tiktok_url,
        testimonio=testimonio
    )
    db.session.add(galeria)
    db.session.commit()

    flash("Resultado agregado a la galería.", "success")
    return redirect(url_for("admin.galeria_admin"))

@admin_bp.route("/galeria/editar/<int:item_id>", methods=["GET", "POST"])
def editar_galeria(item_id):
    item = Galeria.query.get_or_404(item_id)
    servicios = Servicio.query.filter_by(activo=True).all()
    if request.method == "POST":
        item.servicio_id = request.form.get("servicio_id", type=int)
        item.imagen_antes_url = request.form.get("imagen_antes_url", "").strip()
        item.imagen_despues_url = request.form.get("imagen_despues_url", "").strip()
        item.instagram_url = request.form.get("instagram_url", "").strip()
        item.tiktok_url = request.form.get("tiktok_url", "").strip()
        item.testimonio = request.form.get("testimonio", "").strip()

        if not item.servicio_id or not item.imagen_antes_url or not item.imagen_despues_url:
            flash("Completa el servicio y ambas imágenes.", "danger")
            return redirect(url_for("admin.editar_galeria", item_id=item.id))

        db.session.commit()
        flash("Galería actualizada correctamente.", "success")
        return redirect(url_for("admin.galeria_admin"))

    resultados = Galeria.query.order_by(Galeria.created_at.desc()).all()
    return render_template("admin/galeria.html", resultados=resultados, servicios=servicios, item=item)

@admin_bp.route("/galeria/eliminar/<int:item_id>")
def eliminar_galeria(item_id):
    item = Galeria.query.get_or_404(item_id)
    db.session.delete(item)
    db.session.commit()
    flash("Resultado de galería eliminado.", "success")
    return redirect(url_for("admin.galeria_admin"))

# ======================================
# CRUD CLientes
# ========================================
@admin_bp.route("/clientes")
def clientes_admin():
    clientes = Cliente.query.order_by(Cliente.id.desc()).all()
    return render_template("admin/clientes.html", clientes=clientes, cliente=None)

@admin_bp.route("/clientes/nuevo", methods=["POST"])
def nuevo_cliente():
    nombres = request.form.get("nombres", "").strip()
    telefono = request.form.get("telefono", "").strip()
    email = request.form.get("email", "").strip()

    if not nombres:
        flash("El nombre del cliente es obligatorio.", "danger")
        return redirect(url_for("admin.clientes_admin"))

    cliente = Cliente(
        nombres=nombres,
        telefono=telefono,
        email=email
    )
    db.session.add(cliente)
    db.session.commit()

    flash("Cliente agregado correctamente.", "success")
    return redirect(url_for("admin.clientes_admin"))

@admin_bp.route("/clientes/editar/<int:cliente_id>", methods=["GET", "POST"])
def editar_cliente(cliente_id):
    cliente = Cliente.query.get_or_404(cliente_id)
    if request.method == "POST":
        cliente.nombres = request.form.get("nombres", "").strip()
        cliente.telefono = request.form.get("telefono", "").strip()
        cliente.email = request.form.get("email", "").strip()

        if not cliente.nombres:
            flash("El nombre del cliente es obligatorio.", "danger")
            return redirect(url_for("admin.editar_cliente", cliente_id=cliente.id))

        db.session.commit()
        flash("Cliente actualizado correctamente.", "success")
        return redirect(url_for("admin.clientes_admin"))

    clientes = Cliente.query.order_by(Cliente.id.desc()).all()
    return render_template("admin/clientes.html", clientes=clientes, cliente=cliente)

@admin_bp.route("/clientes/eliminar/<int:cliente_id>")
def eliminar_cliente(cliente_id):
    cliente = Cliente.query.get_or_404(cliente_id)
    db.session.delete(cliente)
    db.session.commit()
    flash("Cliente eliminado.", "success")
    return redirect(url_for("admin.clientes_admin"))


#===============================
# CRUD Reservas (Citas)
#=============================== 
@admin_bp.route("/reservas")
@login_required
def reservas_admin():

    reservas = (
        Cita.query
        .join(Cita.cliente)
        .join(Cita.profesional)
        .join(Cita.servicio)
        .order_by(Cita.fecha_inicio.desc())
        .all()
    )

    return render_template(

        "admin/reservas.html",

        reservas=reservas,

        EstadoCita=EstadoCita

    )

@admin_bp.route("/reservas/<int:cita_id>")
@login_required
def ver_reserva(cita_id):

    cita = Cita.query.get_or_404(cita_id)

    return render_template(
        "admin/ver_reserva.html",
        cita=cita
    )
from datetime import timedelta

@admin_bp.route("/reservas/nueva", methods=["GET","POST"])
@login_required
def nueva_reserva():

    clientes = Cliente.query.order_by(
        Cliente.nombres
    ).all()

    profesionales = Profesional.query.filter_by(
        activo=True
    ).all()

    servicios = Servicio.query.filter_by(
        activo=True
    ).all()

    if request.method == "POST":

        cliente_id = request.form["cliente_id"]

        profesional_id = request.form["profesional_id"]

        servicio_id = request.form["servicio_id"]

        fecha = request.form["fecha"]

        hora = request.form["hora"]

        servicio = Servicio.query.get(servicio_id)

        fecha_inicio = datetime.strptime(
            f"{fecha} {hora}",
            "%Y-%m-%d %H:%M"
        )

        fecha_fin = fecha_inicio + timedelta(
            minutes=servicio.duracion_minutos
        )

        nueva = Cita(

            cliente_id=cliente_id,

            profesional_id=profesional_id,

            servicio_id=servicio_id,

            fecha_inicio=fecha_inicio,

            fecha_fin=fecha_fin,

            estado=EstadoCita.PENDIENTE_PAGO

        )

        db.session.add(nueva)

        db.session.commit()

        flash(
            "Reserva creada correctamente.",
            "success"
        )

        return redirect(
            url_for("admin.reservas_admin")
        )

    return render_template(

        "admin/nueva_reserva.html",

        clientes=clientes,

        profesionales=profesionales,

        servicios=servicios

    )

@admin_bp.route(
    "/reservas/<int:cita_id>/reprogramar",
    methods=["GET","POST"]
)
@login_required
def reprogramar_reserva(cita_id):

    cita = Cita.query.get_or_404(cita_id)

    if request.method == "POST":

        fecha = request.form["fecha"]

        hora = request.form["hora"]

        fecha_inicio = datetime.strptime(

            f"{fecha} {hora}",

            "%Y-%m-%d %H:%M"

        )

        duracion = (
            cita.fecha_fin -
            cita.fecha_inicio
        )

        fecha_fin = fecha_inicio + duracion

        historial = Reprogramacion(

            cita_id=cita.id,

            fecha_anterior=cita.fecha_inicio,

            fecha_nueva=fecha_inicio,

            motivo=request.form.get(
                "motivo"
            )

        )

        cita.fecha_inicio = fecha_inicio

        cita.fecha_fin = fecha_fin

        cita.estado = EstadoCita.REPROGRAMADA

        db.session.add(historial)

        db.session.commit()

        flash(

            "Reserva reprogramada correctamente.",

            "success"

        )

        return redirect(

            url_for("admin.reservas_admin")

        )

    return render_template(

        "admin/reprogramar_reserva.html",

        cita=cita

    )

@admin_bp.route(
    "/reservas/<int:cita_id>/confirmar-pago"
)
@login_required
def confirmar_pago(cita_id):

    cita = Cita.query.get_or_404(cita_id)

    cita.estado = EstadoCita.CONFIRMADA

    db.session.commit()

    flash(
        "Pago confirmado.",
        "success"
    )

    return redirect(
        url_for("admin.reservas_admin")
    )

@admin_bp.route(
    "/reservas/<int:cita_id>/cancelar",
    methods=["POST"]
)
@login_required
def cancelar_reserva(cita_id):

    cita = Cita.query.get_or_404(cita_id)

    cita.estado = EstadoCita.CANCELADA

    db.session.commit()

    flash(
        "Reserva cancelada.",
        "warning"
    )

    return redirect(
        url_for("admin.reservas_admin")
    )