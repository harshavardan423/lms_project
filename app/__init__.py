from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from config import Config

db = SQLAlchemy()
login_manager = LoginManager()

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message_category = 'info'

    from app.routes.auth import auth_bp
    from app.routes.admin import admin_bp
    from app.routes.teacher import teacher_bp
    from app.routes.student import student_bp
    from app.routes.parent import parent_bp
    from app.routes.ai import ai_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(admin_bp, url_prefix='/admin')
    app.register_blueprint(teacher_bp, url_prefix='/teacher')
    app.register_blueprint(student_bp, url_prefix='/student')
    app.register_blueprint(parent_bp, url_prefix='/parent')
    app.register_blueprint(ai_bp, url_prefix='/api/ai')

    import os, json
    from datetime import datetime
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

    @app.template_filter('from_json')
    def from_json_filter(value):
        try:
            return json.loads(value)
        except Exception:
            return []

    @app.context_processor
    def inject_now():
        return {'now': datetime.utcnow()}

    @app.errorhandler(403)
    def forbidden(e):
        return '<h2>403 — Access Forbidden</h2><p>You do not have permission to view this page.</p><a href="/">Home</a>', 403

    @app.errorhandler(404)
    def not_found(e):
        return '<h2>404 — Page Not Found</h2><a href="/">Home</a>', 404

    return app
