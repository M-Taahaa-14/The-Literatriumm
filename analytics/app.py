"""
Flask Analytics Microservice
Main application factory and configuration
"""

from flask import Flask, jsonify
from flask_cors import CORS
from config import Config
from models import db


def create_app(config_class=Config):
    """
    Application factory pattern for Flask app creation.
    
    Args:
        config_class: Configuration class to use
        
    Returns:
        Flask: Configured Flask application instance
    """
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # Initialize extensions with app
    db.init_app(app)
    CORS(app)  # Enable CORS for React frontend
    
    # Register blueprints/routes
    register_routes(app)
    
    # Create database tables
    with app.app_context():
        db.create_all()
    
    return app


def register_routes(app):
    """Register all application routes."""
    
    @app.route('/health', methods=['GET'])
    def health_check():
        """Health check endpoint for monitoring."""
        return jsonify({
            'status': 'healthy',
            'service': 'analytics-microservice',
            'version': '1.0.0'
        })
    
    @app.route('/analytics', methods=['GET'])
    def analytics_info():
        """Analytics service information endpoint."""
        return jsonify({
            'service': 'Library Analytics API',
            'description': 'Microservice for library management analytics',
            'endpoints': [
                '/analytics/borrowed-per-month',
                '/analytics/top-10-books', 
                '/analytics/borrowed-by-category',
                '/analytics/borrowed-vs-returned'
            ],
            'database': 'PostgreSQL',
            'status': 'ready'
        })


if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, port=5001)  # Different port from Django
