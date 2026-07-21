from app import create_app
from app.extensions import db
from app.models.usuario import Usuario

app = create_app()

with app.app_context():

    admin = Usuario.query.filter_by(username="admin").first()

    if admin is None:
        admin = Usuario(
            username="admin",
            rol="admin",
            activo=True
        )

        admin.set_password("43737510")

        db.session.add(admin)

    db.session.commit()

    print("Administrador creado.")