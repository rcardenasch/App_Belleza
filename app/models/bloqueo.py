from app.extensions import db
from zoneinfo import ZoneInfo
from datetime import timezone,datetime


def obtener_ahora_lima():
    """Calcula la fecha y hora actual en la zona de Lima."""
    return datetime.now(ZoneInfo("America/Lima"))

class BloqueoAgenda(db.Model):

    __tablename__ = "bloqueos"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    profesional_id = db.Column(
        db.Integer,
        db.ForeignKey("profesionales.id")
    )

    # relación al profesional para usar en templates: item.profesional.nombres
    profesional = db.relationship("Profesional", backref="bloqueos", lazy=True)

    fecha_inicio = db.Column(
        db.DateTime
    )

    fecha_fin = db.Column(
        db.DateTime
    )

    motivo = db.Column(
        db.String(200)
    )

    repetir = db.Column(
        db.Boolean,
        default=False
    )

    fecha_creacion = db.Column(
        db.DateTime,
        default=obtener_ahora_lima
    )

    activo = db.Column(
        db.Boolean,
        default=True
    )

    @property
    def fecha_inicio_lima(self):
        """Devuelve `fecha_inicio` como aware datetime en America/Lima.

        Asume que `fecha_inicio` está almacenada en UTC (naive o aware).
        """
        if not self.fecha_inicio:
            return None
        lima = ZoneInfo("America/Lima")
        dt = self.fecha_inicio
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt.astimezone(lima)

    @property
    def fecha_fin_lima(self):
        """Devuelve `fecha_fin` como aware datetime en America/Lima."""
        if not self.fecha_fin:
            return None
        lima = ZoneInfo("America/Lima")
        dt = self.fecha_fin
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt.astimezone(lima)
    
    @property
    def fecha_creacion_lima(self):
        """Devuelve `fecha_creacion` como aware datetime en America/Lima."""
        if not self.fecha_creacion:
            return None
        lima = ZoneInfo("America/Lima")
        dt = self.fecha_creacion
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt.astimezone(lima)