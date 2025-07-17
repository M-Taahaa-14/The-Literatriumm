"""
Flask application factory and base routes for analytics microservice.

This file contains the application setup and will be extended with
analytics endpoints in separate feature branches.
"""

from flask import Flask, jsonify
from flask_cors import CORS
from models import db
from config import config

def create_app(config_name='default'):
    """
    Application factory pattern for creating Flask app.
    
    Args:
        config_name (str): Configuration environment ('development', 'production')
    
    Returns:
        Flask: Configured Flask application instance
    """
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    
    # Initialize extensions
    db.init_app(app)
    CORS(app)  # Enable CORS for React frontend
    
    # Register blueprints (will be added in feature branches)
    register_blueprints(app)
    
    # Create database tables
    with app.app_context():
        db.create_all()
    
    return app

def register_blueprints(app):
    """
    Register application blueprints.
    This function will be extended as we add analytics endpoints.
    """
    
    @app.route('/')
    def index():
        """Health check endpoint."""
        return jsonify({
            'message': 'Analytics Microservice is running',
            'status': 'healthy',
            'version': '1.0.0'
        })
    
    @app.route('/health')
    def health():
        """Detailed health check with database connectivity."""
        try:
            # Test database connection
            db.session.execute('SELECT 1')
            db_status = 'connected'
        except Exception as e:
            db_status = f'error: {str(e)}'
        
        return jsonify({
            'status': 'healthy',
            'database': db_status,
            'service': 'analytics'
        })

if __name__ == '__main__':
    app = create_app('development')
    app.run(host='0.0.0.0', port=5001, debug=True)
