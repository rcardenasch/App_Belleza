from app.extensions import db
class Cliente(db.Model):
    __tablename__ = "clientes"

    id = db.Column(db.Integer, primary_key=True)

    nombres = db.Column(db.String(200))

    telefono = db.Column(
        db.String(20),
        unique=True
    )

    email = db.Column(db.String(150))
    
    citas = db.relationship(
    "Cita",
    back_populates="cliente"
    )

