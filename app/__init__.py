from flask import Flask
from app.config.settings import Config
from app.extensions import db, migrate, login_manager, csrf, limiter
from flask_wtf.csrf import generate_csrf
from app.blueprints.landing.routes import landing_bp
from app.blueprints.auth.routes import auth_bp
from app.blueprints.citas.routes import reservas_bp
from app.blueprints.profesionales.routes import profesionales_bp
from app.blueprints.admin.routes import admin_bp
import app.models.usuario
from app.config.cloudinary_config import *

def create_app():

    app = Flask(
        __name__,
        template_folder="../templates"
    )

    app.config.from_object(Config)

    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    csrf.init_app(app)
    limiter.init_app(app)

    # make csrf_token() available in templates
    app.jinja_env.globals['csrf_token'] = generate_csrf

    app.register_blueprint(landing_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(reservas_bp)
    app.register_blueprint(profesionales_bp)
    app.register_blueprint(admin_bp)

    return app