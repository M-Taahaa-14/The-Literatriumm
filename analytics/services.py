"""
Analytics service layer for business logic.
Contains reusable functions for data processing and analysis.
"""

from sqlalchemy import func, extract
from database import db
from datetime import datetime, timedelta
import calendar

# Import models - these will be available after app initialization
def get_models():
    """Get model classes after app initialization to avoid circular imports."""
    from models import BorrowRecord, Book, BookCategory, User
    return BorrowRecord, Book, BookCategory, User


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
        
        try:
            # Get model classes
            BorrowRecord, Book, BookCategory, User = get_models()
            
            # Query to get monthly borrow counts
            monthly_data = db.session.query(
                extract('month', BorrowRecord.borrow_date).label('month'),
                func.count(BorrowRecord.id).label('count')
            ).filter(
                extract('year', BorrowRecord.borrow_date) == year
            ).group_by(
                extract('month', BorrowRecord.borrow_date)
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
                'total': sum(values),
                'peak_month': labels[values.index(max(values))] if max(values) > 0 else None,
                'peak_count': max(values)
            }
            
        except Exception as e:
            # Fallback data structure when database is not available
            labels = [calendar.month_name[i] for i in range(1, 13)]
            return {
                'labels': labels,
                'values': [0] * 12,
                'year': year,
                'total': 0,
                'peak_month': None,
                'peak_count': 0,
                'error': f'Database connection issue: {str(e)}',
                'note': 'This is mock data - configure PostgreSQL to see real analytics'
            }
    
    @staticmethod
    def get_top_books(limit=10):
        """
        Get most borrowed books.
        
        Args:
            limit (int): Number of top books to return
            
        Returns:
            dict: Labels (book titles) and values (borrow counts)
        """
        try:
            # Get model classes
            Borrowing, Book, Category, User = get_models()
            
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
            
        except Exception as e:
            return {
                'labels': [],
                'values': [],
                'total': 0,
                'error': f'Database connection issue: {str(e)}',
                'note': 'This is mock data - configure PostgreSQL to see real analytics'
            }
    
    @staticmethod
    def get_borrowed_by_category():
        """
        Get borrowing counts by book category.
        
        Returns:
            dict: Labels (category names) and values (borrow counts)
        """
        try:
            # Get model classes
            Borrowing, Book, Category, User = get_models()
            
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
            
        except Exception as e:
            return {
                'labels': [],
                'values': [],
                'total': 0,
                'error': f'Database connection issue: {str(e)}',
                'note': 'This is mock data - configure PostgreSQL to see real analytics'
            }
    
    @staticmethod
    def get_borrowed_vs_returned():
        """
        Get borrowed vs returned statistics.
        
        Returns:
            dict: Labels and values for borrowed vs returned comparison
        """
        try:
            # Get model classes
            Borrowing, Book, Category, User = get_models()
            
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
            
        except Exception as e:
            return {
                'labels': ['Returned', 'Currently Borrowed'],
                'values': [0, 0],
                'total': 0,
                'return_rate': 0,
                'error': f'Database connection issue: {str(e)}',
                'note': 'This is mock data - configure PostgreSQL to see real analytics'
            }
    
    @staticmethod
    def get_overdue_books():
        """
        Get statistics on overdue books.
        
        Returns:
            dict: Overdue book statistics
        """
        try:
            # Get model classes
            Borrowing, Book, Category, User = get_models()
            
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
            
        except Exception as e:
            return {
                'labels': ['On Time', 'Overdue'],
                'values': [0, 0],
                'total_borrowed': 0,
                'overdue_rate': 0,
                'error': f'Database connection issue: {str(e)}',
                'note': 'This is mock data - configure PostgreSQL to see real analytics'
            }
