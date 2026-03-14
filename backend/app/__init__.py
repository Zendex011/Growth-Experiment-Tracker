from flask import Flask
from .extensions import db, migrate
from .errors import register_error_handlers
from .config import config_map


def create_app(config_name: str = "development") -> Flask:
    app = Flask(__name__)
    app.config.from_object(config_map[config_name])

    db.init_app(app)
    migrate.init_app(app, db)

    from .routes.experiments import experiments_bp
    from .routes.results import results_bp
    from .routes.ai import ai_bp

    app.register_blueprint(experiments_bp, url_prefix="/api/experiments")
    app.register_blueprint(results_bp, url_prefix="/api/experiments")
    app.register_blueprint(ai_bp, url_prefix="/api/ai")

    register_error_handlers(app)

    return app
