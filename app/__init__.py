"""
Main Flask application factory
"""
from flask import Flask
from flask_wtf.csrf import CSRFProtect
from config import *
from app.models import db
from app.error_logging import setup_logging
from app.mongo_handler import MongoDBHandler
import logging

# CSRF protection
csrf = CSRFProtect()

# MongoDB handler
mongo_db = None


def create_app(config_name='development'):
    """
    Application factory function.
    Creates and configures the Flask application.
    """
    global mongo_db

    app = Flask(__name__, 
                template_folder='templates',
                static_folder='static')

    # Load configuration
    app.config.from_object('config')

    # Initialize extensions
    db.init_app(app)
    csrf.init_app(app)

    # Initialize logging
    setup_logging(app)
    logger = logging.getLogger(__name__)
    logger.info("Flask application initialized")

    # Initialize MongoDB handler
    mongo_db = MongoDBHandler(app.config.get('MONGO_URI'))

    # Create database tables
    with app.app_context():
        db.create_all()
        logger.info("Database tables created/verified")

    # Register blueprints
    from app.routes import auth_bp, patient_bp, main_bp
    app.register_blueprint(auth_bp)
    app.register_blueprint(patient_bp)
    app.register_blueprint(main_bp)

    # Error handlers
    @app.errorhandler(400)
    def bad_request(error):
        logger.warning(f"Bad request error: {str(error)}")
        return {'error': 'Bad Request'}, 400

    @app.errorhandler(401)
    def unauthorized(error):
        logger.warning(f"Unauthorized access attempt")
        return {'error': 'Unauthorized'}, 401

    @app.errorhandler(403)
    def forbidden(error):
        logger.warning(f"Forbidden access attempt")
        return {'error': 'Forbidden'}, 403

    @app.errorhandler(404)
    def not_found(error):
        return {'error': 'Not Found'}, 404

    @app.errorhandler(500)
    def internal_error(error):
        logger.error(f"Internal server error: {str(error)}")
        db.session.rollback()
        return {'error': 'Internal Server Error'}, 500

   


    return app



def get_mongo_db():
    """Get MongoDB handler instance"""
    global mongo_db
    return mongo_db
