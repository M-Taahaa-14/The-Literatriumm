from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from sqlalchemy import func, Numeric

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
    """User model - synced from Django auth_user table."""
    __tablename__ = 'auth_user'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    email = db.Column(db.String(254), unique=True, nullable=False)
    first_name = db.Column(db.String(30))
    last_name = db.Column(db.String(30))
    is_staff = db.Column(db.Boolean, default=False)
    is_active = db.Column(db.Boolean, default=True)
    date_joined = db.Column(db.DateTime, default=datetime.utcnow)
    
    full_name = db.Column(db.String(200))
    address = db.Column(db.Text)
    phone = db.Column(db.String(20))
    
    def __repr__(self):
        return f'<User {self.username}>'


class Category(db.Model):
    __tablename__ = 'library_app_bookcategory'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    
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
    
    def __repr__(self):
        return f'<Book {self.title}>'


class Borrowing(db.Model):
    __tablename__ = 'library_app_borrowrecord'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False)
    book_id = db.Column(db.Integer, nullable=False)
    borrow_date = db.Column(db.DateTime, nullable=False)
    due_date = db.Column(db.DateTime, nullable=False)
    return_date = db.Column(db.DateTime, nullable=True)
    is_returned = db.Column(db.Boolean, default=False)
    fine = db.Column(Numeric(10, 2), default=0.00)
    
    def __repr__(self):
        return f'<Borrowing {self.id}: Book {self.book_id} by User {self.user_id}>'


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
