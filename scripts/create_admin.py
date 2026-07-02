from app import create_app
from app.extensions import db
from app.models.usuario import Usuario

app = create_app()
with app.app_context():
    u = Usuario.query.filter_by(username='admin').first()
    if not u:
        u = Usuario(username='admin', rol='admin', activo=True)
        u.set_password('43737510')
        db.session.add(u)
    else:
        u.set_password('43737510')
    db.session.commit()
    print('Usuario admin creado/actualizado con contraseña 43737510')
