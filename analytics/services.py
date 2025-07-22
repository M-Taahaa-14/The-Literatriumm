"""
Analytics service layer for business logic.
Contains reusable functions for data processing and analysis.
"""

from sqlalchemy import func, extract
from models import db, Borrowing, Book, Category, User, Review
from datetime import datetime, timedelta
import calendar


class AnalyticsService:
    """Service class for analytics business logic."""
    
    @staticmethod
    def get_borrowed_per_month(year=None):
        """
        Get books borrowed per month for a given year.
        
        Args:
            year (int, optional): Year to analyze. Defaults to current year.
            
        Returns:
            dict: Labels (month names) and values (borrow counts)
        """
        if year is None:
            year = datetime.now().year
        
        # Query to get monthly borrow counts
        monthly_data = db.session.query(
            extract('month', Borrowing.borrow_date).label('month'),
            func.count(Borrowing.id).label('count')
        ).filter(
            extract('year', Borrowing.borrow_date) == year
        ).group_by(
            extract('month', Borrowing.borrow_date)
        ).order_by('month').all()
        
        # Initialize all months with 0 counts
        month_counts = {i: 0 for i in range(1, 13)}
        
        # Fill in actual data
        for month, count in monthly_data:
            month_counts[int(month)] = int(count)
        
        # Convert to labels and values for frontend
        labels = [calendar.month_name[i] for i in range(1, 13)]
        values = [month_counts[i] for i in range(1, 13)]
        
        return {
            'labels': labels,
            'values': values,
            'year': year,
            'total': sum(values)
        }
    
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
            top_books = db.session.query(
                Book.id,
                Book.title,
                Book.author,
                Book.cover_image,
                func.count(Borrowing.id).label('borrow_count')
            ).join(
                Borrowing, Book.id == Borrowing.book_id
            ).group_by(
                Book.id, Book.title, Book.author, Book.cover_image
            ).order_by(
                func.count(Borrowing.id).desc()
            ).limit(limit).all()
            
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
        Get top books by average rating with cover images.
        
        Args:
            limit (int): Number of top books to return
            
        Returns:
            dict: Book details with average ratings
        """
        try:
            # Subquery to calculate average ratings per book
            avg_ratings = db.session.query(
                Review.book_id,
                func.avg(Review.rating).label('avg_rating'),
                func.count(Review.id).label('review_count')
            ).group_by(Review.book_id).subquery()
            
            # Main query to get top rated books with at least 3 reviews
            top_books = db.session.query(
                Book.id,
                Book.title,
                Book.author,
                Book.cover_image,
                avg_ratings.c.avg_rating,
                avg_ratings.c.review_count
            ).join(
                avg_ratings, Book.id == avg_ratings.c.book_id
            ).filter(
                avg_ratings.c.review_count >= 3  # At least 3 reviews for reliability
            ).order_by(
                avg_ratings.c.avg_rating.desc()
            ).limit(limit).all()
            
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
                'avg_rating_overall': round(sum(book['avg_rating'] for book in books_data) / len(books_data), 1) if books_data else 0,
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
                'avg_rating_overall': 0,
                'metric': 'ratings'
            }
    
    @staticmethod
    def get_top_books(limit=10):
        """
        Get most borrowed books (legacy method for backward compatibility).
        
        Args:
            limit (int): Number of top books to return
            
        Returns:
            dict: Labels (book titles) and values (borrow counts)
        """
        top_books = db.session.query(
            Book.title,
            Book.author,
            func.count(Borrowing.id).label('borrow_count')
        ).join(
            Borrowing, Book.id == Borrowing.book_id
        ).group_by(
            Book.id, Book.title, Book.author
        ).order_by(
            func.count(Borrowing.id).desc()
        ).limit(limit).all()
        
        labels = [f"{book.title} by {book.author}" for book in top_books]
        values = [int(book.borrow_count) for book in top_books]
        
        return {
            'labels': labels,
            'values': values,
            'total': sum(values)
        }
    
    @staticmethod
    def get_borrowed_by_category():
        """
        Get borrowing counts by book category.
        
        Returns:
            dict: Labels (category names) and values (borrow counts)
        """
        category_data = db.session.query(
            Category.name,
            func.count(Borrowing.id).label('borrow_count')
        ).join(
            Book, Category.id == Book.category_id
        ).join(
            Borrowing, Book.id == Borrowing.book_id
        ).group_by(
            Category.id, Category.name
        ).order_by(
            func.count(Borrowing.id).desc()
        ).all()
        
        labels = [category.name for category in category_data]
        values = [int(category.borrow_count) for category in category_data]
        
        return {
            'labels': labels,
            'values': values,
            'total': sum(values)
        }
    
    @staticmethod
    def get_borrowed_vs_returned():
        """
        Get borrowed vs returned statistics.
        
        Returns:
            dict: Labels and values for borrowed vs returned comparison
        """
        total_borrowed = db.session.query(func.count(Borrowing.id)).scalar() or 0
        total_returned = db.session.query(func.count(Borrowing.id)).filter(
            Borrowing.is_returned == True
        ).scalar() or 0
        
        currently_borrowed = total_borrowed - total_returned
        
        return {
            'labels': ['Returned', 'Currently Borrowed'],
            'values': [total_returned, currently_borrowed],
            'total': total_borrowed,
            'return_rate': round((total_returned / total_borrowed * 100), 2) if total_borrowed > 0 else 0
        }
    
    @staticmethod
    def get_overdue_books():
        """
        Get statistics on overdue books.
        
        Returns:
            dict: Overdue book statistics
        """
        current_date = datetime.utcnow()
        
        # Books that are overdue (not returned and past due date)
        overdue_count = db.session.query(func.count(Borrowing.id)).filter(
            Borrowing.is_returned == False,
            Borrowing.due_date < current_date
        ).scalar() or 0
        
        # Books currently borrowed (not returned)
        currently_borrowed = db.session.query(func.count(Borrowing.id)).filter(
            Borrowing.is_returned == False
        ).scalar() or 0
        
        on_time = currently_borrowed - overdue_count
        
        return {
            'labels': ['On Time', 'Overdue'],
            'values': [on_time, overdue_count],
            'total_borrowed': currently_borrowed,
            'overdue_rate': round((overdue_count / currently_borrowed * 100), 2) if currently_borrowed > 0 else 0
        }
