from app.extensions import db
from zoneinfo import ZoneInfo
from datetime import timezone
from datetime import datetime


def obtener_ahora_lima():
    """Calcula la fecha y hora actual en la zona de Lima."""
    return datetime.now(ZoneInfo("America/Lima"))


class Reprogramacion(db.Model):

    __tablename__ = "reprogramaciones"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    cita_id = db.Column(
        db.Integer,
        db.ForeignKey("citas.id")
    )

    fecha_anterior_inicio = db.Column(db.DateTime)

    fecha_anterior_fin = db.Column(db.DateTime)

    fecha_nueva_inicio = db.Column(db.DateTime)

    fecha_nueva_fin = db.Column(db.DateTime)

    profesional_anterior_id = db.Column(
        db.Integer,
        db.ForeignKey("profesionales.id")
    )

    profesional_nuevo_id = db.Column(
        db.Integer,
        db.ForeignKey("profesionales.id")
    )

    motivo = db.Column(db.Text)

    usuario = db.Column(db.String(100))

    fecha = db.Column(
        db.DateTime,
        default=obtener_ahora_lima
    )

    profesional_anterior = db.relationship(
        "Profesional",
        foreign_keys=[profesional_anterior_id]
    )

    profesional_nuevo = db.relationship(
        "Profesional",
        foreign_keys=[profesional_nuevo_id]
    )
    # Añade esta relación al final de la clase:
    cita = db.relationship(
        "Cita",
        back_populates="reprogramaciones"
    )

    @property
    def fecha_lima(self):
        """Devuelve `fecha` como aware datetime en America/Lima."""
        if not self.fecha:
            return None
        lima = ZoneInfo("America/Lima")
        dt = self.fecha
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt.astimezone(lima)
    
    @property
    def fecha_anterior_inicio_lima(self):
        """Devuelve `fecha_anterior_inicio` como aware datetime en America/Lima."""
        if not self.fecha_anterior_inicio:
            return None
        lima = ZoneInfo("America/Lima")
        dt = self.fecha_anterior_inicio
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt.astimezone(lima)
    
    @property
    def fecha_anterior_fin_lima(self):
        """Devuelve `fecha_anterior_fin` como aware datetime en America/Lima."""
        if not self.fecha_anterior_fin:
            return None
        lima = ZoneInfo("America/Lima")
        dt = self.fecha_anterior_fin
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt.astimezone(lima)
    
    @property
    def fecha_nueva_inicio_lima(self):
        """Devuelve `fecha_nueva_inicio` como aware datetime en America/Lima."""
        if not self.fecha_nueva_inicio:
            return None
        lima = ZoneInfo("America/Lima")
        dt = self.fecha_nueva_inicio
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt.astimezone(lima)
    
    @property
    def fecha_nueva_fin_lima(self):
        """Devuelve `fecha_nueva_fin` como aware datetime en America/Lima."""
        if not self.fecha_nueva_fin:
            return None
        lima = ZoneInfo("America/Lima")
        dt = self.fecha_nueva_fin
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt.astimezone(lima)
    