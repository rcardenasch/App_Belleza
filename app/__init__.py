from flask import Flask
from flask.cli import load_dotenv
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

from app.config.settings import Config
from app.services.scheduler.scheduler import iniciar_scheduler


load_dotenv()


def create_app():

    app = Flask(
        __name__,
        template_folder="../templates"
    )

    app.config.from_object(Config)

    #print("=" * 50)
    #print("EVOLUTION_URL:", app.config.get("EVOLUTION_URL"))
    #print("EVOLUTION_INSTANCE:", app.config.get("EVOLUTION_INSTANCE"))
    #print("EVOLUTION_TOKEN:", app.config.get("EVOLUTION_TOKEN"))
    #print("WHATSAPP_ADMIN:", app.config.get("WHATSAPP_ADMIN"))
    #print("=" * 50)

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

    # ← AQUÍ
    iniciar_scheduler(app)

    return app