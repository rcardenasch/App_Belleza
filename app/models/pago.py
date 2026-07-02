from app.extensions import db
from zoneinfo import ZoneInfo
from datetime import timezone
from datetime import datetime


def obtener_ahora_lima():
    """Calcula la fecha y hora actual en la zona de Lima."""
    return datetime.now(ZoneInfo("America/Lima"))

class Pago(db.Model):

    __tablename__ = "pagos"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    cita_id = db.Column(
        db.Integer,
        db.ForeignKey("citas.id")
    )

    monto = db.Column(
        db.Numeric(10,2)
    )

    metodo_pago = db.Column(
        db.String(50)
    )

    numero_operacion = db.Column(
        db.String(100)
    )

    comprobante_url = db.Column(
        db.String(500)
    )

    observacion = db.Column(
        db.Text
    )

    validado = db.Column(
        db.Boolean,
        default=False
    )

    fecha_pago = db.Column(
        db.DateTime,
        default=obtener_ahora_lima
    )

    cita = db.relationship(
        "Cita",
        back_populates="pagos"
    )

    @property
    def fecha_pago_lima(self):
        """Devuelve `fecha_pago` como aware datetime en America/Lima."""
        if not self.fecha_pago:
            return None
        lima = ZoneInfo("America/Lima")
        dt = self.fecha_pago
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt.astimezone(lima)
    