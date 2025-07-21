"""
SQLAlchemy models for Analytics microservice.
These models mirror the Django models exactly for analytics purposes.
"""

from database import db
from datetime import datetime
from sqlalchemy import func, Numeric


class User(db.Model):
    """User model - mirrors Django User + UserProfile for analytics."""
    __tablename__ = 'auth_user'  # Django's default User table name
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    email = db.Column(db.String(254), unique=True, nullable=False)
    first_name = db.Column(db.String(30))
    last_name = db.Column(db.String(150))
    is_staff = db.Column(db.Boolean, default=False)
    is_active = db.Column(db.Boolean, default=True)
    date_joined = db.Column(db.DateTime, default=datetime.utcnow)
    
    # UserProfile fields (from Django UserProfile model)
    full_name = db.Column(db.String(150))
    address = db.Column(db.Text)
    phone = db.Column(db.String(13))
    
    # Relationships
    borrow_records = db.relationship('BorrowRecord', backref='user', lazy=True)
    
    def __repr__(self):
        return f'<User {self.username}>'


class BookCategory(db.Model):
    """BookCategory model - mirrors Django BookCategory exactly."""
    __tablename__ = 'library_app_bookcategory'  # Django's table name
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    
    # Relationships
    books = db.relationship('Book', backref='category', lazy=True)
    
    def __repr__(self):
        return f'<BookCategory {self.name}>'


class Book(db.Model):
    """Book model - mirrors Django Book exactly."""
    __tablename__ = 'library_app_book'  # Django's table name
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    author = db.Column(db.String(200), nullable=False)
    isbn = db.Column(db.String(13), unique=True, nullable=False)
    total_copies = db.Column(db.Integer, nullable=False)
    available_copies = db.Column(db.Integer, nullable=False)
    cover_image = db.Column(db.String(100), nullable=True)  # Django ImageField path
    
    # Foreign Keys
    category_id = db.Column(db.Integer, db.ForeignKey('library_app_bookcategory.id'), nullable=False)
    
    # Relationships
    borrow_records = db.relationship('BorrowRecord', backref='book', lazy=True)
    
    def __repr__(self):
        return f'<Book {self.title}>'


class BorrowRecord(db.Model):
    """BorrowRecord model - mirrors Django BorrowRecord exactly."""
    __tablename__ = 'library_app_borrowrecord'  # Django's table name
    
    id = db.Column(db.Integer, primary_key=True)
    borrow_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, index=True)
    return_date = db.Column(db.DateTime, nullable=True)
    due_date = db.Column(db.DateTime, nullable=True)
    is_returned = db.Column(db.Boolean, default=False)
    fine = db.Column(Numeric(6, 2), default=0.00)  # Matches Django DecimalField
    
    # Foreign Keys
    user_id = db.Column(db.Integer, db.ForeignKey('auth_user.id'), nullable=False)
    book_id = db.Column(db.Integer, db.ForeignKey('library_app_book.id'), nullable=False)
    
    def __repr__(self):
        return f'<BorrowRecord {self.id}: {self.book.title} by {self.user.username}>'
    
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
            func.extract('month', BorrowRecord.borrow_date).label('month'),
            func.count(BorrowRecord.id).label('count')
        ).filter(
            func.extract('year', BorrowRecord.borrow_date) == year
        ).group_by(
            func.extract('month', BorrowRecord.borrow_date)
        ).order_by('month').all()
    
    @staticmethod
    def get_top_borrowed_books(limit=10):
        """Get most borrowed books."""
        return db.session.query(
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
    
    @staticmethod
    def get_borrowings_by_category():
        """Get borrowing counts by book category."""
        return db.session.query(
            BookCategory.name,
            func.count(BorrowRecord.id).label('borrow_count')
        ).join(
            Book, BookCategory.id == Book.category_id
        ).join(
            BorrowRecord, Book.id == BorrowRecord.book_id
        ).group_by(
            BookCategory.id, BookCategory.name
        ).order_by(
            func.count(BorrowRecord.id).desc()
        ).all()
    
    @staticmethod
    def get_borrowed_vs_returned():
        """Get borrowed vs returned statistics."""
        total_borrowed = db.session.query(func.count(BorrowRecord.id)).scalar()
        total_returned = db.session.query(func.count(BorrowRecord.id)).filter(
            BorrowRecord.is_returned == True
        ).scalar()
        
        return {
            'total_borrowed': total_borrowed or 0,
            'total_returned': total_returned or 0,
            'currently_borrowed': (total_borrowed or 0) - (total_returned or 0)
        }
