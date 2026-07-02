from flask import (
    Blueprint,
    flash,
    redirect,
    render_template,
    request,
    url_for
)
from decimal import Decimal, InvalidOperation
from app.extensions import db
from app.models.servicio import Servicio

# Se define como "admin" para empatar exactamente con url_for('admin.xxx') del HTML
admin_bp = Blueprint(
    "admin",
    __name__,
    url_prefix="/admin"
)

@admin_bp.route("/servicios", methods=["GET"])
def servicios_admin():
    """Muestra el listado de todos los servicios registrados."""
    servicios = Servicio.query.order_by(Servicio.nombre).all()
    
    # Renderiza la vista principal pasando la lista completa y servicio=None
    # (Al ser None, el formulario de edición en el HTML permanece oculto)
    return render_template(
        "admin/servicios.html", # Modifica la ruta de la plantilla si es otra carpeta
        servicios=servicios,
        servicio=None
    )

@admin_bp.route("/servicios/nuevo", methods=["POST"])
def nuevo_servicio():
    """Procesa la creación de un nuevo servicio."""
    nombre = request.form.get("nombre", "").strip()
    duracion_minutos = request.form.get("duracion_minutos", type=int)
    precio_raw = request.form.get("precio", "").strip()
    descripcion = request.form.get("descripcion", "").strip()
    color = request.form.get("color", "#3788d8").strip()
    imagen_url = request.form.get("imagen_url", "").strip()
    video_url = request.form.get("video_url", "").strip()
    
    # Manejo del checkbox de Bootstrap para el estado activo
    activo = True if request.form.get("activo") else False

    # Validaciones obligatorias de negocio
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

    # Creación del nuevo registro en la base de datos
    nuevo_serv = Servicio(
        nombre=nombre,
        descripcion=descripcion or None,
        duracion_minutos=duracion_minutos,
        precio=precio,
        color=color,
        imagen_url=imagen_url or None,
        video_url=video_url or None,
        activo=activo
    )

    db.session.add(nuevo_serv)
    db.session.commit()

    flash("Servicio agregado correctamente.", "success")
    return redirect(url_for("admin.servicios_admin"))

@admin_bp.route("/servicios/editar/<int:servicio_id>", methods=["GET", "POST"])
def editar_servicio(servicio_id):
    """Muestra el formulario de edición o procesa los cambios de un servicio."""
    servicio = Servicio.query.get_or_404(servicio_id)

    if request.method == "POST":
        nombre = request.form.get("nombre", "").strip()
        duracion_minutos = request.form.get("duracion_minutos", type=int)
        precio_raw = request.form.get("precio", "").strip()
        descripcion = request.form.get("descripcion", "").strip()
        color = request.form.get("color", "#3788d8").strip()
        imagen_url = request.form.get("imagen_url", "").strip()
        video_url = request.form.get("video_url", "").strip()
        activo = True if request.form.get("activo") else False

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

        # Actualización de propiedades del objeto persistido
        servicio.nombre = nombre
        servicio.descripcion = descripcion or None
        servicio.duracion_minutos = duracion_minutos
        servicio.precio = precio
        servicio.color = color
        servicio.imagen_url = imagen_url or None
        servicio.video_url = video_url or None
        servicio.activo = activo

        db.session.commit()
        flash("Servicio actualizado correctamente.", "success")
        return redirect(url_for("admin.servicios_admin"))

    # Si es GET, vuelve a renderizar la lista pero inyecta el objeto "servicio"
    # Esto provoca que el HTML dibuje el formulario superior de edición
    servicios = Servicio.query.order_by(Servicio.nombre).all()
    return render_template(
        "admin/servicios.html",
        servicios=servicios,
        servicio=servicio
    )

@admin_bp.route("/servicios/eliminar/<int:servicio_id>", methods=["POST"])
def eliminar_servicio(servicio_id):
    """Elimina permanentemente un servicio de la base de datos."""
    servicio = Servicio.query.get_or_404(servicio_id)
    
    db.session.delete(servicio)
    db.session.commit()
    
    flash("Servicio eliminado.", "success")
    return redirect(url_for("admin.servicios_admin"))
