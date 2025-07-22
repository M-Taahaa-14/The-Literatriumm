from flask import Flask, jsonify
from flask_cors import CORS
from config import Config
from models import db


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    db.init_app(app)
    CORS(app)  

    register_routes(app)
    
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
                '/analytics/top-books-by-borrowings', 
                '/analytics/top-books-by-ratings',
                '/analytics/borrowed-by-category',
                '/analytics/borrowed-vs-returned'
            ],
            'database': 'PostgreSQL',
            'status': 'ready'
        })
    
    @app.route('/analytics/borrowed-per-month', methods=['GET'])
    def borrowed_per_month():
        """Get monthly borrowing statistics for a specific year."""
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

    @app.route('/analytics/top-books-by-borrowings', methods=['GET'])
    def top_books_by_borrowings():
        """Get top books ranked by number of borrowings."""
        from flask import request
        from services import AnalyticsService
        
        try:
            limit = request.args.get('limit', default=10, type=int)
            if limit > 50:  # Prevent excessive queries
                limit = 50
                
            data = AnalyticsService.get_top_books_by_borrowings(limit)
            
            if data['success']:
                return jsonify({
                    'success': True,
                    'data': data,
                    'message': f'Top {len(data["books"])} books by borrowings'
                }), 200
            else:
                return jsonify({
                    'success': False,
                    'error': data['error'],
                    'message': 'Failed to retrieve top books by borrowings'
                }), 500
                
        except Exception as e:
            return jsonify({
                'success': False,
                'error': str(e),
                'message': 'Failed to retrieve top books by borrowings'
            }), 500

    @app.route('/analytics/top-books-by-ratings', methods=['GET'])
    def top_books_by_ratings():
        """Get top books ranked by average ratings."""
        from flask import request
        from services import AnalyticsService
        
        try:
            limit = request.args.get('limit', default=10, type=int)
            if limit > 50:  # Prevent excessive queries
                limit = 50
                
            data = AnalyticsService.get_top_books_by_ratings(limit)
            
            if data['success']:
                return jsonify({
                    'success': True,
                    'data': data,
                    'message': f'Top {len(data["books"])} books by ratings'
                }), 200
            else:
                return jsonify({
                    'success': False,
                    'error': data['error'],
                    'message': 'Failed to retrieve top books by ratings'
                }), 500
                
        except Exception as e:
            return jsonify({
                'success': False,
                'error': str(e),
                'message': 'Failed to retrieve top books by ratings'
            }), 500


if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, port=5001)  
