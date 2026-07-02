from app.extensions import db
from datetime import datetime

class Galeria(db.Model):
    __tablename__ = "galeria_resultados"

    id = db.Column(db.Integer, primary_key=True)

    servicio_id = db.Column(
        db.Integer,
        db.ForeignKey("servicios.id")
    )

    imagen_antes_url = db.Column(db.String(500))
    imagen_despues_url = db.Column(db.String(500))

    instagram_url = db.Column(db.String(500))
    tiktok_url = db.Column(db.String(500))
    testimonio = db.Column(db.Text)

    servicio = db.relationship("Servicio")

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )
