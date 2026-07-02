from app.extensions import db
from app.models.profesional_servicio import profesional_servicio

class Servicio(db.Model):
    __tablename__ = "servicios"

    id = db.Column(db.Integer, primary_key=True)

    nombre = db.Column(db.String(150))
    descripcion = db.Column(db.Text)

    duracion_minutos = db.Column(db.Integer)

    precio = db.Column(db.Numeric(10,2))

    color = db.Column(db.String(20),
        default="#3788d8")

    imagen_url = db.Column(db.String(500))
    video_url = db.Column(db.String(500))

    activo = db.Column(db.Boolean, default=True)

    profesionales = db.relationship(
        "Profesional",
        secondary=profesional_servicio,
        back_populates="servicios",
        lazy=True
    )
    citas = db.relationship(
    "Cita",
    back_populates="servicio"
    )
