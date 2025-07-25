"""
Database Import Script
Imports data from JSON export files to populate your library database
"""
import os
import sys
import django
import json
from datetime import datetime
from decimal import Decimal
from pathlib import Path

# Setup Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'library.settings')
django.setup()

from django.contrib.auth.models import User
from django.utils import timezone
from library_app.models import BookCategory, Book, UserProfile, BorrowRecord, Review, Notification

def find_export_files():
    """Find the latest export files"""
    export_dir = Path('database_export')
    
    if not export_dir.exists():
        print(f"❌ Export directory not found: {export_dir}")
        print("   Make sure you've pulled the latest changes with database_export folder")
        return None
    
    # Check for latest files
    latest_metadata = export_dir / "latest_metadata.json"
    
    if not latest_metadata.exists():
        print("❌ No export metadata found in database_export/")
        print("   Available files:", list(export_dir.glob("*.json")))
        return None
    
    # Load metadata
    with open(latest_metadata, 'r', encoding='utf-8') as f:
        metadata = json.load(f)
    
    # Check all required files exist
    required_files = ['users', 'categories', 'books', 'borrowings', 'reviews', 'notifications']
    file_paths = {}
    
    for file_type in required_files:
        file_path = export_dir / f"latest_{file_type}.json"
        if not file_path.exists():
            print(f"❌ Missing export file: {file_path}")
            return None
        file_paths[file_type] = file_path
    
    return metadata, file_paths

def load_export_data(file_paths):
    """Load all export data from JSON files"""
    print("📥 Loading export data...")
    
    data = {}
    for file_type, file_path in file_paths.items():
        print(f"   📄 Loading {file_type}...")
        with open(file_path, 'r', encoding='utf-8') as f:
            data[file_type] = json.load(f)
    
    print(f"   ✅ Loaded all export files")
    return data

def import_users(users_data):
    """Import users and their profiles"""
    print("👥 Importing users and profiles...")
    
    created_users = []
    for user_data in users_data:
        # Create or get user
        user, created = User.objects.get_or_create(
            username=user_data['username'],
            defaults={
                'email': user_data['email'],
                'first_name': user_data['first_name'],
                'last_name': user_data['last_name'],
                'is_staff': user_data['is_staff'],
                'is_superuser': user_data['is_superuser']
            }
        )
        
        if created:
            user.set_password('password123')  # Default password
            user.save()
            print(f"   ✅ Created user: {user.username}")
        else:
            print(f"   ⏭️  User already exists: {user.username}")
        
        # Create or update profile if exists
        if user_data['profile']:
            profile, profile_created = UserProfile.objects.get_or_create(
                user=user,
                defaults={
                    'full_name': user_data['profile']['full_name'],
                    'address': user_data['profile']['address'],
                    'phone': user_data['profile']['phone']
                }
            )
            
            if profile_created:
                print(f"      📝 Created profile for {user.username}")
        
        created_users.append(user)
    
    return created_users

def import_categories(categories_data):
    """Import book categories"""
    print("\n📚 Importing book categories...")
    
    created_categories = []
    for category_data in categories_data:
        category, created = BookCategory.objects.get_or_create(
            name=category_data['name']
        )
        if created:
            print(f"   ✅ Created category: {category_data['name']}")
        else:
            print(f"   ⏭️  Category already exists: {category_data['name']}")
        created_categories.append(category)
    
    return created_categories

def import_books(books_data, categories):
    """Import books"""
    print("\n📖 Importing books...")
    
    created_books = []
    category_dict = {cat.name: cat for cat in categories}
    
    for book_data in books_data:
        category = category_dict.get(book_data['category'])
        if not category:
            print(f"   ❌ Category not found: {book_data['category']}")
            continue
        
        book, created = Book.objects.get_or_create(
            title=book_data['title'],
            author=book_data['author'],
            defaults={
                'category': category,
                'total_copies': book_data['total_copies'],
                'available_copies': book_data['available_copies'],
                'isbn': book_data['isbn']
            }
        )
        
        if created:
            print(f"   ✅ Created book: {book.title} by {book.author}")
        else:
            print(f"   ⏭️  Book already exists: {book.title}")
        
        created_books.append(book)
    
    return created_books

def import_borrowings(borrowings_data, users, books):
    """Import borrow records"""
    print("\n📋 Importing borrow records...")
    
    user_dict = {user.username: user for user in users}
    book_dict = {book.title: book for book in books}
    
    created_borrowings = []
    
    for borrow_data in borrowings_data:
        user = user_dict.get(borrow_data['user'])
        book = book_dict.get(borrow_data['book'])
        
        if not user or not book:
            print(f"   ❌ User or book not found for borrow record")
            continue
        
        # Parse dates
        try:
            borrow_date = datetime.fromisoformat(borrow_data['borrow_date'].replace('Z', '+00:00'))
            return_date = None
            if borrow_data['return_date']:
                return_date = datetime.fromisoformat(borrow_data['return_date'].replace('Z', '+00:00'))
            
            due_date = None
            if borrow_data['due_date']:
                due_date = datetime.fromisoformat(borrow_data['due_date'].replace('Z', '+00:00'))
        except ValueError as e:
            print(f"   ❌ Invalid date format in borrow record: {e}")
            continue
        
        # Check if record already exists (avoid duplicates)
        existing = BorrowRecord.objects.filter(
            user=user,
            book=book,
            borrow_date__date=borrow_date.date()
        ).first()
        
        if existing:
            print(f"   ⏭️  Borrow record already exists: {user.username} - {book.title}")
            continue
        
        borrow_record = BorrowRecord.objects.create(
            user=user,
            book=book,
            borrow_date=borrow_date,
            return_date=return_date,
            is_returned=borrow_data['is_returned'],
            due_date=due_date,
            fine=Decimal(str(borrow_data['fine']))
        )
        
        status = "returned" if borrow_data['is_returned'] else "active"
        print(f"   ✅ {user.username} borrowed '{book.title}' ({status})")
        created_borrowings.append(borrow_record)
    
    return created_borrowings

def import_reviews(reviews_data, users, books):
    """Import reviews"""
    print("\n⭐ Importing reviews...")
    
    user_dict = {user.username: user for user in users}
    book_dict = {book.title: book for book in books}
    
    created_reviews = []
    
    for review_data in reviews_data:
        user = user_dict.get(review_data['user'])
        book = book_dict.get(review_data['book'])
        
        if not user or not book:
            print(f"   ❌ User or book not found for review")
            continue
        
        # Check if review already exists
        existing_review = Review.objects.filter(user=user, book=book).first()
        if existing_review:
            print(f"   ⏭️  Review already exists: {user.username} - {book.title}")
            continue
        
        # Parse date
        try:
            created_at = datetime.fromisoformat(review_data['created_at'].replace('Z', '+00:00'))
        except ValueError as e:
            print(f"   ❌ Invalid date format in review: {e}")
            continue
        
        review = Review.objects.create(
            user=user,
            book=book,
            content=review_data['content'],
            rating=review_data['rating'],
            created_at=created_at
        )
        
        print(f"   ✅ {user.username} reviewed '{book.title}' - {review_data['rating']}⭐")
        created_reviews.append(review)
    
    return created_reviews

def import_notifications(notifications_data, users):
    """Import notifications"""
    print("\n🔔 Importing notifications...")
    
    user_dict = {user.username: user for user in users}
    
    created_notifications = []
    
    for notif_data in notifications_data:
        user = user_dict.get(notif_data['user'])
        
        if not user:
            print(f"   ❌ User not found for notification")
            continue
        
        # Parse date
        try:
            created_at = datetime.fromisoformat(notif_data['created_at'].replace('Z', '+00:00'))
        except ValueError as e:
            print(f"   ❌ Invalid date format in notification: {e}")
            continue
        
        # Check for duplicate notifications (same user, message, and date)
        existing = Notification.objects.filter(
            user=user,
            message=notif_data['message'],
            created_at__date=created_at.date()
        ).first()
        
        if existing:
            print(f"   ⏭️  Similar notification already exists for {user.username}")
            continue
        
        notification = Notification.objects.create(
            user=user,
            message=notif_data['message'],
            created_at=created_at,
            is_read=notif_data['is_read']
        )
        
        status = "📖 Read" if notif_data['is_read'] else "🔔 Unread"
        print(f"   ✅ Notification for {user.username}: {status}")
        created_notifications.append(notification)
    
    return created_notifications

def show_import_summary():
    """Show database import summary"""
    print("\n" + "="*60)
    print("📊 DATABASE IMPORT SUMMARY")
    print("="*60)
    
    print(f"👥 Users: {User.objects.count()}")
    print(f"📝 User Profiles: {UserProfile.objects.count()}")
    print(f"📚 Categories: {BookCategory.objects.count()}")
    print(f"📖 Books: {Book.objects.count()}")
    print(f"📋 Borrow Records: {BorrowRecord.objects.count()}")
    print(f"   - Active: {BorrowRecord.objects.filter(is_returned=False).count()}")
    print(f"   - Returned: {BorrowRecord.objects.filter(is_returned=True).count()}")
    print(f"⭐ Reviews: {Review.objects.count()}")
    print(f"🔔 Notifications: {Notification.objects.count()}")
    print(f"   - Unread: {Notification.objects.filter(is_read=False).count()}")
    
    # Show some statistics
    total_books = Book.objects.count()
    if total_books > 0:
        total_copies = sum(book.total_copies for book in Book.objects.all())
        available_copies = sum(book.available_copies for book in Book.objects.all())
        borrowed_copies = total_copies - available_copies
        
        print(f"\n📊 Library Statistics:")
        print(f"   - Total book copies: {total_copies}")
        print(f"   - Available copies: {available_copies}")
        print(f"   - Currently borrowed: {borrowed_copies}")
    
    # Show average rating
    reviews = Review.objects.all()
    if reviews:
        avg_rating = sum(r.rating for r in reviews) / len(reviews)
        print(f"   - Average book rating: {avg_rating:.1f}⭐")
    
    print(f"\n🎉 Database import completed successfully!")
    print(f"💡 Default password for all users: 'password123'")

def main():
    """Main import function"""
    print("📥 Library Database Import Script")
    print("="*50)
    print("This script will import data from exported JSON files")
    print("to populate your library database.")
    print()
    
    # Find export files
    export_files = find_export_files()
    if not export_files:
        return
    
    metadata, file_paths = export_files
    
    # Show export info
    print(f"📅 Found export from: {metadata['export_date']}")
    print(f"📊 Export contains:")
    for key, count in metadata['stats'].items():
        print(f"   - {key.replace('_count', '').title()}: {count}")
    
    print(f"\n⚠️  This will add data to your current database!")
    print(f"💡 Existing records will be skipped to avoid duplicates.")
    
    response = input("\nContinue with import? (y/N): ").lower().strip()
    if response != 'y':
        print("❌ Import cancelled by user")
        return
    
    try:
        # Load all export data
        data = load_export_data(file_paths)
        
        # Import data in correct order
        print(f"\n🗄️ Starting database import...")
        
        users = import_users(data['users'])
        categories = import_categories(data['categories'])
        books = import_books(data['books'], categories)
        borrowings = import_borrowings(data['borrowings'], users, books)
        reviews = import_reviews(data['reviews'], users, books)
        notifications = import_notifications(data['notifications'], users)
        
        # Show summary
        show_import_summary()
        
        print(f"\n💡 You can now run your Django server:")
        print(f"   python manage.py runserver")
        
    except Exception as e:
        print(f"\n❌ Import failed: {str(e)}")
        import traceback
        traceback.print_exc()
        print(f"\n💡 Try running migrations first if you see database errors:")
        print(f"   python manage.py migrate")

if __name__ == '__main__':
    main()
