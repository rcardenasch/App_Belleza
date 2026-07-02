from app.extensions import db


profesional_servicio = db.Table(

    "profesional_servicio",

    db.Column(
        "profesional_id",
        db.Integer,
        db.ForeignKey("profesionales.id")
    ),

    db.Column(
        "servicio_id",
        db.Integer,
        db.ForeignKey("servicios.id")
    )
)