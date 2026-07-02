from app.extensions import db
from app.models.profesional_servicio import profesional_servicio

class Profesional(db.Model):
    __tablename__ = "profesionales"

    id = db.Column(db.Integer, primary_key=True)

    nombres = db.Column(db.String(150))

    telefono = db.Column(db.String(20))

    foto_url = db.Column(db.String(500))

    activo = db.Column(
        db.Boolean,
        default=True
    )

    disponibilidades = db.relationship(
        "DisponibilidadSemanal",
        back_populates="profesional",
        lazy=True
    )

    servicios = db.relationship(
        "Servicio",
        secondary=profesional_servicio,
        back_populates="profesionales",
        lazy=True
    )
    citas = db.relationship(
    "Cita",
    back_populates="profesional"
    )