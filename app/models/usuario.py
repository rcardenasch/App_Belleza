from flask_login import UserMixin 
from app.extensions import db 
from werkzeug.security import (generate_password_hash,check_password_hash)


class Usuario( UserMixin, db.Model ): 
    __tablename__ = "usuarios" 
    id = db.Column( db.Integer, primary_key=True ) 
    username = db.Column( db.String(100), unique=True, nullable=False ) 
    password_hash = db.Column( db.String(255), nullable=False ) 
    rol = db.Column( db.String(50) ) 
    activo = db.Column( db.Boolean, default=True )
    
    def set_password(self, password: str):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password_hash, password)



from app.extensions import ( login_manager ) 
@login_manager.user_loader 
def load_user(user_id): 
    return Usuario.query.get( int(user_id) )



