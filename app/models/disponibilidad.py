from app.extensions import db


class DisponibilidadSemanal(db.Model):

    __tablename__ = "disponibilidades"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    profesional_id = db.Column(
        db.Integer,
        db.ForeignKey("profesionales.id"),
        nullable=False
    )

    dia_semana = db.Column(
        db.Integer,
        nullable=False
    )

    hora_inicio = db.Column(
        db.Time,
        nullable=False
    )

    hora_fin = db.Column(
        db.Time,
        nullable=False
    )

    duracion_promedio_minutos = db.Column(
        db.Integer,
        default=60
    )

    profesional = db.relationship(
        "Profesional",
        back_populates="disponibilidades"
    )