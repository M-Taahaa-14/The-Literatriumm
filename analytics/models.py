from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from sqlalchemy import func, Numeric
from database import db
# Initialize db here to avoid circular imports
# 
# WHY THIS PATTERN?
# =================
# 1. CIRCULAR IMPORT PROBLEM:
#    - If we create db in app.py: models.py would need to import from app.py
#    - If app.py imports from models.py: creates circular dependency
#    - Python can't resolve: app.py ← → models.py
#
# 2. SOLUTION - APPLICATION FACTORY PATTERN:
#    - Create db instance HERE (in models.py) without attaching to app
#    - Use db.init_app(app) LATER in app.py to connect them
#    - No circular imports: models.py doesn't import from app.py
#
# 3. FLOW:
#    models.py: db = SQLAlchemy()  # Creates unbound instance
#    app.py: db.init_app(app)      # Binds db to Flask app later
#    app.py imports db from models.py  
#    models.py NEVER imports from app.py  
#    No circular dependency!  
db = SQLAlchemy()


class User(db.Model):
    __tablename__ = 'auth_user'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    email = db.Column(db.String(254), unique=True, nullable=False)
    first_name = db.Column(db.String(30))
    last_name = db.Column(db.String(150))
    is_staff = db.Column(db.Boolean, default=False)
    is_active = db.Column(db.Boolean, default=True)
    date_joined = db.Column(db.DateTime, default=datetime.utcnow)
    
    full_name = db.Column(db.String(150))
    address = db.Column(db.Text)
    phone = db.Column(db.String(13))
    
    # Relationships
    borrow_records = db.relationship('BorrowRecord', backref='user', lazy=True)
    
    def __repr__(self):
        return f'<User {self.username}>'


class Category(db.Model):
    __tablename__ = 'library_app_bookcategory'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)

    # Relationships
    books = db.relationship('Book', backref='category', lazy=True)    

    def __repr__(self):
        return f'<Category {self.name}>'


class Book(db.Model):
    __tablename__ = 'library_app_book'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    author = db.Column(db.String(200), nullable=False)
    isbn = db.Column(db.String(13), unique=True)
    total_copies = db.Column(db.Integer, default=1)
    available_copies = db.Column(db.Integer, default=1)
    category_id = db.Column(db.Integer, nullable=True)
    cover_image = db.Column(db.String(255), nullable=True)

    # Foreign Keys
    category_id = db.Column(db.Integer, db.ForeignKey('library_app_bookcategory.id'), nullable=False)
    
    # Relationships
    borrow_records = db.relationship('BorrowRecord', backref='book', lazy=True)
        
    def __repr__(self):
        return f'<Book {self.title}>'


class BorrowRecord(db.Model):
    __tablename__ = 'library_app_borrowrecord'  
    
    id = db.Column(db.Integer, primary_key=True)
    borrow_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, index=True)
    return_date = db.Column(db.DateTime, nullable=True)
    due_date = db.Column(db.DateTime, nullable=True)
    is_returned = db.Column(db.Boolean, default=False)
    fine = db.Column(Numeric(6, 2), default=0.00)  
    
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


class Review(db.Model):
    __tablename__ = 'library_app_review'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False)
    book_id = db.Column(db.Integer, nullable=False)
    rating = db.Column(db.Integer, nullable=False)  
    comment = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Review {self.id}: User {self.user_id} rated Book {self.book_id} ⭐{self.rating}>'

# Analytics helper functions for common queries
def get_top_books_by_borrowings(limit=10):
    from sqlalchemy import text
    
    query = text("""
        SELECT 
            b.id,
            b.title,
            b.author,
            b.cover_image,
            COUNT(br.id) as borrow_count
        FROM library_app_book b
        INNER JOIN library_app_borrowrecord br ON b.id = br.book_id
        GROUP BY b.id, b.title, b.author, b.cover_image
        HAVING COUNT(br.id) >= 1
        ORDER BY borrow_count DESC
        LIMIT :limit
    """)
    
    result = db.session.execute(query, {'limit': limit})
    return result.fetchall()


def get_top_books_by_ratings(limit=10):
    """Get top rated books with minimum 1 review."""
    from sqlalchemy import text
    
    query = text("""
        SELECT 
            b.id,
            b.title,
            b.author,
            b.cover_image,
            AVG(CAST(r.rating AS FLOAT)) as avg_rating,
            COUNT(r.id) as review_count
        FROM library_app_book b
        INNER JOIN library_app_review r ON b.id = r.book_id
        GROUP BY b.id, b.title, b.author, b.cover_image
        HAVING COUNT(r.id) >= 1
        ORDER BY avg_rating DESC, review_count DESC
        LIMIT :limit
    """)
    
    result = db.session.execute(query, {'limit': limit})
    return result.fetchall()


def get_borrowing_stats():
    from sqlalchemy import text
    
    query = text("""
        SELECT 
            COUNT(*) as total_borrowings,
            COUNT(CASE WHEN is_returned = true THEN 1 END) as returned_books,
            COUNT(CASE WHEN is_returned = false THEN 1 END) as currently_borrowed
        FROM library_app_borrowrecord
    """)
    
    result = db.session.execute(query)
    return result.fetchone()

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
            Category.name,
            func.count(BorrowRecord.id).label('borrow_count')
        ).join(
            Book, Category.id == Book.category_id
        ).join(
            BorrowRecord, Book.id == BorrowRecord.book_id
        ).group_by(
            Category.id, Category.name
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
