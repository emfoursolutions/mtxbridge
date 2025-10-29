# ABOUTME: Flask application factory and initialization
# ABOUTME: Creates and configures the Flask app with all extensions and blueprints

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager

from config import config_by_name

# Initialize extensions
db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()


def create_app(config_name='default'):
    """Application factory pattern for creating Flask app instances"""
    app = Flask(__name__)

    # Load configuration
    app.config.from_object(config_by_name[config_name])

    # Initialize extensions with app
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)

    # Configure login manager
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Please log in to access this page.'

    # Register blueprints
    from app.auth import auth_bp
    from app.api import api_bp

    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(api_bp, url_prefix='/api')

    # Register user loader
    from app.models.user import User

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # Add root route
    from flask import redirect, url_for
    from flask_login import current_user

    @app.route('/')
    def index():
        """Root route - redirect to dashboard if logged in, otherwise to login"""
        if current_user.is_authenticated:
            return redirect(url_for('api.dashboard'))
        return redirect(url_for('auth.login'))

    return app
