"""
Database models for analytics microservice.
Represents the borrowings table for library analytics.
"""

from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class Borrowing(db.Model):
    """
    Model representing book borrowing records for analytics.
    
    This table stores historical borrowing data that will be queried
    for various analytics endpoints.
    """
    __tablename__ = 'borrowings'
    
    id = db.Column(db.Integer, primary_key=True)
    book_title = db.Column(db.String(200), nullable=False)
    category = db.Column(db.String(100), nullable=False)
    borrow_date = db.Column(db.Date, nullable=False)
    return_date = db.Column(db.Date, nullable=True)
    
    def __repr__(self):
        return f'<Borrowing {self.book_title} - {self.borrow_date}>'
    
    def to_dict(self):
        """Convert model instance to dictionary for JSON serialization."""
        return {
            'id': self.id,
            'book_title': self.book_title,
            'category': self.category,
            'borrow_date': self.borrow_date.isoformat() if self.borrow_date else None,
            'return_date': self.return_date.isoformat() if self.return_date else None
        }
