"""
Analytics service layer for business logic.
Contains reusable functions for data processing and analysis.
"""

from models import db, get_top_books_by_borrowings, get_top_books_by_ratings, get_borrowing_stats
from datetime import datetime
import calendar


class AnalyticsService:
    """Service class for analytics business logic."""
    
    @staticmethod
    def get_top_books_by_borrowings(limit=10):
        """
        Get top books by number of borrowings with cover images.
        
        Args:
            limit (int): Number of top books to return
            
        Returns:
            dict: Book details with borrowing counts
        """
        try:
            top_books = get_top_books_by_borrowings(limit)
            
            books_data = []
            for book in top_books:
                books_data.append({
                    'id': book.id,
                    'title': book.title,
                    'author': book.author,
                    'cover_image': book.cover_image or '/media/book_covers/default.jpg',
                    'borrow_count': int(book.borrow_count),
                    'label': f"{book.title} by {book.author}"
                })
            
            return {
                'success': True,
                'books': books_data,
                'labels': [book['label'] for book in books_data],
                'values': [book['borrow_count'] for book in books_data],
                'total_borrowings': sum(book['borrow_count'] for book in books_data),
                'metric': 'borrowings'
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'books': [],
                'labels': [],
                'values': [],
                'total_borrowings': 0,
                'metric': 'borrowings'
            }
    
    @staticmethod
    def get_top_books_by_ratings(limit=10):
        """
        Get top books by average rating (minimum 2 reviews).
        
        Args:
            limit (int): Number of top books to return
            
        Returns:
            dict: Book details with average ratings
        """
        try:
            top_books = get_top_books_by_ratings(limit)
            
            books_data = []
            for book in top_books:
                books_data.append({
                    'id': book.id,
                    'title': book.title,
                    'author': book.author,
                    'cover_image': book.cover_image or '/media/book_covers/default.jpg',
                    'avg_rating': round(float(book.avg_rating), 1),
                    'review_count': int(book.review_count),
                    'label': f"{book.title} by {book.author}"
                })
            
            return {
                'success': True,
                'books': books_data,
                'labels': [book['label'] for book in books_data],
                'values': [book['avg_rating'] for book in books_data],
                'total_reviews': sum(book['review_count'] for book in books_data),
                'metric': 'ratings'
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'books': [],
                'labels': [],
                'values': [],
                'total_reviews': 0,
                'metric': 'ratings'
            }
