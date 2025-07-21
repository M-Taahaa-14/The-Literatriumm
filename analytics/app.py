import os
from flask import Flask, jsonify
from flask_cors import CORS
from config import Config
from database import db
from dotenv import load_dotenv

load_dotenv()


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    db.init_app(app)
    CORS(app) 
    register_routes(app)
    
    # Create database tables
    with app.app_context():
        db.create_all()
    
    return app


def register_routes(app):
    @app.route('/health', methods=['GET'])

    def health_check():
        return jsonify({
            'status': 'healthy',
            'service': 'analytics-microservice',
            'version': '1.0.0'
        })
    
    @app.route('/analytics', methods=['GET'])
    def analytics_info():
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
    
    @app.route('/analytics/borrowed-per-month', methods=['GET'])
    def borrowed_per_month():
        from flask import request
        from services import AnalyticsService
        
        try:
            year = request.args.get('year', type=int)
            data = AnalyticsService.get_borrowed_per_month(year)
            
            return jsonify({
                'success': True,
                'data': data,
                'message': f'Monthly borrowing statistics for {data["year"]}'
            }), 200
            
        except Exception as e:
            return jsonify({
                'success': False,
                'error': str(e),
                'message': 'Failed to retrieve monthly borrowing statistics'
            }), 500

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, port=5001)  