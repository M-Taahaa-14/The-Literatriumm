from models import db, get_top_books_by_borrowings, get_top_books_by_ratings, get_borrowing_stats
from datetime import datetime
import calendar


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
