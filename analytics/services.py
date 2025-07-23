from models import db, get_top_books_by_BorrowRecords, get_top_books_by_ratings, get_BorrowRecord_stats
from datetime import datetime
import calendar
from models import BorrowRecord, Book, Category, User, Review
from sqlalchemy import func, extract
from database import db

class AnalyticsService:
    @staticmethod
    def get_top_books_by_BorrowRecords(limit=10):
        """
        Get top books by number of BorrowRecords with cover images.

        Args:
            limit (int): Number of top books to return (only ones which have BorrowRecord records)

        Returns:
            dict: Labels (month names) and values (borrow counts)
        """
        if year is None:
            year = datetime.now().year
        
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
            'total': sum(values)
        }
    
    @staticmethod
    def get_top_books_by_ratings(limit=10):
        """
        Get top books by average rating (minimum 1 review).
        
        FLOW:
        1. Call SQL query to get books with average ratings
        2. Transform raw database results into structured data  
        3. Calculate overall statistics
        4. Return formatted response for React frontend
        
        Args:
            limit (int): Number of top books to return
            
        Returns:
            dict: Book details with average ratings
        """
        top_books = db.session.query(
            Book.title,
            Book.author,
            func.count(BorrowRecord.id).label('borrow_count')
        ).join(
            BorrowRecord, Book.id == BorrowRecord.book_id
        ).group_by(
            Book.id, Book.title, Book.author
        ).order_by(
            func.count(BorrowRecord.id).desc()
        ).limit(limit).all()
        
        labels = [f"{book.title} by {book.author}" for book in top_books]
        values = [int(book.borrow_count) for book in top_books]
        
        return {
            'labels': labels,
            'values': values,
            'total': sum(values)
        }
    
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