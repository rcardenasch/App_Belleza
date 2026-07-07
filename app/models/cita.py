import enum
from datetime import datetime, timezone
from zoneinfo import ZoneInfo

from app.extensions import db

from app.models.pago import Pago 

from app.models.reprogramacion import Reprogramacion 


class EstadoCita(enum.Enum):
    PENDIENTE = "Pendiente"
    PENDIENTE_PAGO = "Pendiente Pago"
    CONFIRMADA = "Confirmada"
    EN_CURSO = "En Curso"
    FINALIZADA = "Finalizada"
    CANCELADA = "Cancelada"
    NO_ASISTIO = "No asistió"
    REPROGRAMADA = "Reprogramada"


def obtener_ahora_lima():
    return datetime.now(ZoneInfo("America/Lima"))


class Cita(db.Model):

    __tablename__ = "citas"

    id = db.Column(db.Integer, primary_key=True)

    cliente_id = db.Column(
        db.Integer,
        db.ForeignKey("clientes.id"),
        nullable=False
    )

    profesional_id = db.Column(
        db.Integer,
        db.ForeignKey("profesionales.id"),
        nullable=False
    )

    servicio_id = db.Column(
        db.Integer,
        db.ForeignKey("servicios.id"),
        nullable=False
    )

    fecha_inicio = db.Column(db.DateTime, nullable=False)

    fecha_fin = db.Column(db.DateTime, nullable=False)

    # guardamos el nombre, teléfono y correo del cliente en la cita para tener un registro histórico
    cliente_nombre = db.Column(db.String(150))
    cliente_telefono = db.Column(db.String(20))
    cliente_email = db.Column(db.String(120))


    estado = db.Column(
        db.Enum(EstadoCita),
        default=EstadoCita.PENDIENTE_PAGO
    )

    observacion = db.Column(db.Text)

    fecha_creacion = db.Column(
        db.DateTime,
        default=obtener_ahora_lima
    )

    fecha_actualizacion = db.Column(
        db.DateTime,
        default=obtener_ahora_lima,
        onupdate=obtener_ahora_lima
    )

    # ANTES: back_populates="cita" -> ERROR: Cliente tiene "citas"
    cliente = db.relationship(
        "Cliente",
        back_populates="citas" # Corregido a plural
    )

    # ANTES: back_populates="cita" -> ERROR: Profesional tiene "citas"
    profesional = db.relationship(
        "Profesional",
        back_populates="citas" # Corregido a plural
    )

    # ANTES: back_populates="cita" -> ERROR: Asegúrate que Servicio tenga "citas"
    servicio = db.relationship(
        "Servicio",
        back_populates="citas" # Corregido a plural
    )

    pagos = db.relationship(
        "Pago",
        back_populates="cita",
        lazy=True
    )

    reprogramaciones = db.relationship(
        "Reprogramacion",
        back_populates="cita",
        cascade="all, delete-orphan"
    )

    @property
    def fecha_creacion_lima(self):
        if not self.fecha_creacion:
            return None

        dt = self.fecha_creacion

        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)

        return dt.astimezone(ZoneInfo("America/Lima"))

    @property
    def fecha_actualizacion_lima(self):
        if not self.fecha_actualizacion:
            return None

        dt = self.fecha_actualizacion

        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)

        return dt.astimezone(ZoneInfo("America/Lima"))

    @property
    def fecha_inicio_lima(self):
        if not self.fecha_inicio:
            return None

        dt = self.fecha_inicio

        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)

        return dt.astimezone(ZoneInfo("America/Lima"))

    @property
    def fecha_fin_lima(self):
        if not self.fecha_fin:
            return None

        dt = self.fecha_fin

        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)

        return dt.astimezone(ZoneInfo("America/Lima"))