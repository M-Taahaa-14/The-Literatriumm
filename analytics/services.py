from models import db, BorrowRecord, get_top_books_by_borrowings, get_top_books_by_ratings, get_borrowing_stats
from datetime import datetime
import calendar
from sqlalchemy import func, extract

class AnalyticsService:

    @staticmethod
    def get_top_books_by_borrowings(limit=10):
        """
        Get top books by number of borrowings with cover images.

        Args:
            limit (int): Number of top books to return (only ones which have borrowing records)

        Returns:
            dict: Book details with borrowing counts
        """
        try:
            # STEP 1: Fetch data from database
            top_books = get_top_books_by_borrowings(limit)
            
            # STEP 2: Transform each book record into frontend-friendly format
            books_data = []
            for book in top_books:
                books_data.append({
                    'id': book.id,
                    'title': book.title,
                    'author': book.author,
                    'cover_image': book.cover_image,
                    'borrow_count': int(book.borrow_count),
                    'label': f"{book.title} by {book.author}"  
                })
            
            # STEP 3: Return structured response for React
            return {
                'success': True,
                'books': books_data,              # List of book objects
                'labels': [book['label'] for book in books_data],    # For Chart.js labels
                'values': [book['borrow_count'] for book in books_data],  # For Chart.js data
                'total_borrowings': sum(book['borrow_count'] for book in books_data),  # Statistics
                'metric': 'borrowings'            # Identifies this as borrowing data
            }
            
        except Exception as e:
            # STEP 4: Error handling - return safe empty response
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
        Get top books by average ratings.

        Args:
            limit (int): Number of top books to return (only ones which have ratings)

        Returns:
            dict: Book details with average ratings
        """

        try:
            # STEP 1: Get raw data from database
            top_books = get_top_books_by_ratings(limit)

            # STEP 2: Transform each book record into frontend-friendly format
            books_data = []
            for book in top_books:
                books_data.append({
                    'id': book.id,                    
                    'title': book.title,              
                    'author': book.author,             
                    'cover_image': book.cover_image,  
                    'avg_rating': round(float(book.avg_rating), 1),  
                    'review_count': int(book.review_count),          
                    'label': f"{book.title} by {book.author}"       
                })

            # STEP 3: Return structured response with statistics for React
            return {
                'success': True,
                'books': books_data,              # List of book objects
                'labels': [book['label'] for book in books_data],    # For Chart.js labels
                'values': [book['avg_rating'] for book in books_data],  # For Chart.js data (ratings)
                'total_reviews': sum(book['review_count'] for book in books_data),  # Total review count
                'avg_rating_overall': round(sum(book['avg_rating'] for book in books_data) / len(books_data), 1) if books_data else 0,  # Average of all averages
                'metric': 'ratings'               # Identifies this as rating data
            }

        except Exception as e:
            # STEP 4: Error handling - return safe empty response

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