"""
Data Synchronization Script
Sync data from Django SQLite database to PostgreSQL analytics database
"""

import sqlite3
import os
import sys
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from database import db
from models import User, BookCategory, Book, BorrowRecord


def get_django_data():
    """Read data from Django SQLite database."""
    django_db_path = '../library/db.sqlite3'
    
    if not os.path.exists(django_db_path):
        print(f"❌ Django database not found at: {django_db_path}")
        return None, None, None, None
    
    print(f"📖 Reading from Django database: {django_db_path}")
    
    conn = sqlite3.connect(django_db_path)
    conn.row_factory = sqlite3.Row  # This enables column access by name
    cursor = conn.cursor()
    
    try:
        # Get users and user profiles
        cursor.execute('''
            SELECT u.id, u.username, u.email, u.first_name, u.last_name, 
                   u.is_staff, u.is_active, u.date_joined,
                   up.full_name, up.address, up.phone
            FROM auth_user u
            LEFT JOIN library_app_userprofile up ON u.id = up.user_id
        ''')
        users = cursor.fetchall()
        print(f"Found {len(users)} users")
        
        # Get book categories
        cursor.execute('SELECT * FROM library_app_bookcategory')
        categories = cursor.fetchall()
        print(f"Found {len(categories)} categories")
        
        # Get books
        cursor.execute('SELECT * FROM library_app_book')
        books = cursor.fetchall()
        print(f"Found {len(books)} books")
        
        # Get borrow records
        cursor.execute('SELECT * FROM library_app_borrowrecord')
        borrow_records = cursor.fetchall()
        print(f"Found {len(borrow_records)} borrow records")
        
        return users, categories, books, borrow_records
        
    except sqlite3.Error as e:
        print(f"❌ Error reading Django database: {e}")
        return None, None, None, None
    finally:
        conn.close()


def sync_to_postgres(users, categories, books, borrow_records):
    """Sync data to PostgreSQL analytics database."""
    app = create_app()
    
    with app.app_context():
        try:
            # Clear existing data (optional - remove if you want to keep existing data)
            print("🗑️ Clearing existing data...")
            BorrowRecord.query.delete()
            Book.query.delete()
            BookCategory.query.delete()
            User.query.delete()
            db.session.commit()
            
            # Sync categories first (no foreign keys)
            print("📚 Syncing categories...")
            for cat in categories:
                new_category = BookCategory(
                    id=cat['id'],
                    name=cat['name']
                )
                db.session.add(new_category)
            
            db.session.commit()
            print(f"✅ Synced {len(categories)} categories")
            
            # Sync users with duplicate handling
            print("👥 Syncing users...")
            user_mapping = {}
            synced_users = 0
            seen_emails = set()
            
            for user in users:
                # Handle duplicate emails
                email = user['email'] if user['email'] else f"user_{user['id']}@example.com"
                
                # If we've seen this email before, modify it
                if email in seen_emails:
                    email = f"{user['username']}_{user['id']}@example.com"
                    print(f"⚠️ Modified duplicate email for user {user['username']}: {email}")
                
                seen_emails.add(email)
                
                new_user = User(
                    id=user['id'],
                    username=user['username'],
                    email=email,
                    first_name=user['first_name'],
                    last_name=user['last_name'],
                    is_staff=bool(user['is_staff']),
                    is_active=bool(user['is_active']),
                    date_joined=datetime.fromisoformat(user['date_joined'].replace('Z', '+00:00')) if user['date_joined'] else datetime.utcnow(),
                    full_name=user['full_name'],
                    address=user['address'],
                    phone=user['phone']
                )
                db.session.add(new_user)
                user_mapping[user['id']] = new_user
                synced_users += 1
            
            db.session.commit()
            print(f"✅ Synced {synced_users} users")
            
            # Sync books
            print("📖 Syncing books...")
            for book in books:
                new_book = Book(
                    id=book['id'],
                    title=book['title'],
                    author=book['author'],
                    isbn=book['isbn'],
                    total_copies=book['total_copies'],
                    available_copies=book['available_copies'],
                    cover_image=book['cover_image'],
                    category_id=book['category_id']
                )
                db.session.add(new_book)
            
            db.session.commit()
            print(f"✅ Synced {len(books)} books")
            
            # Sync borrow records
            print("📋 Syncing borrow records...")
            for record in borrow_records:
                new_record = BorrowRecord(
                    id=record['id'],
                    borrow_date=datetime.fromisoformat(record['borrow_date'].replace('Z', '+00:00')) if record['borrow_date'] else datetime.utcnow(),
                    return_date=datetime.fromisoformat(record['return_date'].replace('Z', '+00:00')) if record['return_date'] else None,
                    due_date=datetime.fromisoformat(record['due_date'].replace('Z', '+00:00')) if record['due_date'] else None,
                    is_returned=bool(record['is_returned']),
                    fine=float(record['fine']) if record['fine'] else 0.0,
                    user_id=record['user_id'],
                    book_id=record['book_id']
                )
                db.session.add(new_record)
            
            db.session.commit()
            print(f"✅ Synced {len(borrow_records)} borrow records")
            
            # Verify sync
            print("\n📊 Sync Summary:")
            print(f"Users: {User.query.count()}")
            print(f"Categories: {BookCategory.query.count()}")
            print(f"Books: {Book.query.count()}")
            print(f"Borrow Records: {BorrowRecord.query.count()}")
            
            return True
            
        except Exception as e:
            print(f"❌ Error syncing to PostgreSQL: {e}")
            db.session.rollback()
            return False


def main():
    """Main sync function."""
    print("🔄 Starting Django to PostgreSQL data sync...")
    
    # Read Django data
    users, categories, books, borrow_records = get_django_data()
    
    if not all([users is not None, categories is not None, books is not None, borrow_records is not None]):
        print("❌ Failed to read Django data. Exiting.")
        return
    
    # Sync to PostgreSQL
    success = sync_to_postgres(users, categories, books, borrow_records)
    
    if success:
        print("\n🎉 Data sync completed successfully!")
        print("🚀 You can now test the analytics endpoints with real data")
    else:
        print("\n❌ Data sync failed!")


if __name__ == '__main__':
    main()
