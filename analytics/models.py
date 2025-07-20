"""
SQLAlchemy models for Analytics microservice.
These models mirror the Django models for analytics purposes.
"""

from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from sqlalchemy import func

# Initialize db here to avoid circular imports
db = SQLAlchemy()


class User(db.Model):
    """User model - mirrors Django User for analytics."""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    email = db.Column(db.String(254), unique=True, nullable=False)
    first_name = db.Column(db.String(30))
    last_name = db.Column(db.String(30))
    is_staff = db.Column(db.Boolean, default=False)
    date_joined = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    borrowings = db.relationship('Borrowing', backref='user', lazy=True)
    
    def __repr__(self):
        return f'<User {self.username}>'


class Category(db.Model):
    """Category model for book classification."""
    __tablename__ = 'categories'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    books = db.relationship('Book', backref='category', lazy=True)
    
    def __repr__(self):
        return f'<Category {self.name}>'


class Book(db.Model):
    """Book model - mirrors Django Book for analytics."""
    __tablename__ = 'books'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    author = db.Column(db.String(200), nullable=False)
    isbn = db.Column(db.String(13), unique=True)
    publication_date = db.Column(db.Date)
    total_copies = db.Column(db.Integer, default=1)
    available_copies = db.Column(db.Integer, default=1)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Foreign Keys
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'), nullable=True)
    
    # Relationships
    borrowings = db.relationship('Borrowing', backref='book', lazy=True)
    
    def __repr__(self):
        return f'<Book {self.title}>'


class Borrowing(db.Model):
    """Borrowing model - core entity for analytics."""
    __tablename__ = 'borrowings'
    
    id = db.Column(db.Integer, primary_key=True)
    borrow_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    due_date = db.Column(db.DateTime, nullable=False)
    return_date = db.Column(db.DateTime, nullable=True)  # NULL if not returned
    is_returned = db.Column(db.Boolean, default=False)
    late_fee = db.Column(db.Decimal(10, 2), default=0.00)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Foreign Keys
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    book_id = db.Column(db.Integer, db.ForeignKey('books.id'), nullable=False)
    
    def __repr__(self):
        return f'<Borrowing {self.id}: {self.book.title} by {self.user.username}>'
    
    @property
    def is_overdue(self):
        """Check if borrowing is overdue."""
        if self.is_returned:
            return False
        return datetime.utcnow() > self.due_date
    
    @property
    def days_overdue(self):
        """Calculate days overdue."""
        if not self.is_overdue:
            return 0
        return (datetime.utcnow() - self.due_date).days


# Utility functions for common analytics queries
class AnalyticsQueries:
    """Common analytics query helpers."""
    
    @staticmethod
    def get_monthly_borrowing_stats(year=None):
        """Get borrowing statistics by month."""
        if year is None:
            year = datetime.now().year
            
        return db.session.query(
            func.extract('month', Borrowing.borrow_date).label('month'),
            func.count(Borrowing.id).label('count')
        ).filter(
            func.extract('year', Borrowing.borrow_date) == year
        ).group_by(
            func.extract('month', Borrowing.borrow_date)
        ).order_by('month').all()
    
    @staticmethod
    def get_top_borrowed_books(limit=10):
        """Get most borrowed books."""
        return db.session.query(
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
    
    @staticmethod
    def get_borrowings_by_category():
        """Get borrowing counts by book category."""
        return db.session.query(
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
    
    @staticmethod
    def get_borrowed_vs_returned():
        """Get borrowed vs returned statistics."""
        total_borrowed = db.session.query(func.count(Borrowing.id)).scalar()
        total_returned = db.session.query(func.count(Borrowing.id)).filter(
            Borrowing.is_returned == True
        ).scalar()
        
        return {
            'total_borrowed': total_borrowed or 0,
            'total_returned': total_returned or 0,
            'currently_borrowed': (total_borrowed or 0) - (total_returned or 0)
        }
