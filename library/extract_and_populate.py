"""
Extract Current Database Data and Create Population Script
Reads existing SQLite database and creates a script to populate with current data structure
"""
import os
import sys
import django
import json
from datetime import datetime

# Setup Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'library.settings')
django.setup()

from django.contrib.auth.models import User
from library_app.models import BookCategory, Book, UserProfile, BorrowRecord, Review, Notification

def extract_current_data():
    """Extract all current data from the database"""
    print("🔍 Extracting current database data...")
    
    # Extract Users and Profiles
    users_data = []
    for user in User.objects.all():
        user_info = {
            'username': user.username,
            'email': user.email,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'is_staff': user.is_staff,
            'is_superuser': user.is_superuser,
            'date_joined': user.date_joined.isoformat(),
        }
        
        # Get profile if exists
        try:
            profile = user.userprofile
            user_info['profile'] = {
                'full_name': profile.full_name,
                'address': profile.address,
                'phone': profile.phone,
            }
        except UserProfile.DoesNotExist:
            user_info['profile'] = None
        
        users_data.append(user_info)
    
    # Extract Categories
    categories_data = []
    for category in BookCategory.objects.all():
        categories_data.append({
            'id': category.id,
            'name': category.name,
        })
    
    # Extract Books
    books_data = []
    for book in Book.objects.all():
        books_data.append({
            'id': book.id,
            'title': book.title,
            'author': book.author,
            'category': book.category.name,
            'total_copies': book.total_copies,
            'available_copies': book.available_copies,
            'isbn': book.isbn,
            'cover_image': str(book.cover_image) if book.cover_image else None,
            'average_rating': book.average_rating,
        })
    
    # Extract Borrow Records
    borrowings_data = []
    for borrow in BorrowRecord.objects.all():
        borrowings_data.append({
            'id': borrow.id,
            'user': borrow.user.username,
            'book': borrow.book.title,
            'borrow_date': borrow.borrow_date.isoformat(),
            'return_date': borrow.return_date.isoformat() if borrow.return_date else None,
            'is_returned': borrow.is_returned,
            'due_date': borrow.due_date.isoformat() if borrow.due_date else None,
            'fine': float(borrow.fine),
        })
    
    # Extract Reviews
    reviews_data = []
    for review in Review.objects.all():
        reviews_data.append({
            'id': review.id,
            'user': review.user.username,
            'book': review.book.title,
            'content': review.content,
            'rating': review.rating,
            'created_at': review.created_at.isoformat(),
        })
    
    # Extract Notifications
    notifications_data = []
    for notification in Notification.objects.all():
        notifications_data.append({
            'id': notification.id,
            'user': notification.user.username,
            'message': notification.message,
            'created_at': notification.created_at.isoformat(),
            'is_read': notification.is_read,
        })
    
    return {
        'users': users_data,
        'categories': categories_data,
        'books': books_data,
        'borrowings': borrowings_data,
        'reviews': reviews_data,
        'notifications': notifications_data,
        'extraction_date': datetime.now().isoformat(),
        'stats': {
            'users_count': len(users_data),
            'categories_count': len(categories_data),
            'books_count': len(books_data),
            'borrowings_count': len(borrowings_data),
            'reviews_count': len(reviews_data),
            'notifications_count': len(notifications_data),
        }
    }

def save_extracted_data(data):
    """Save extracted data to JSON file"""
    filename = f"database_snapshot_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    print(f"💾 Saved database snapshot to: {filename}")
    return filename

def generate_population_script(data):
    """Generate a new population script based on extracted data"""
    script_content = f'''"""
Database Population Script Generated from Current Data
Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Based on existing database with:
- {data['stats']['users_count']} users
- {data['stats']['categories_count']} categories  
- {data['stats']['books_count']} books
- {data['stats']['borrowings_count']} borrowings
- {data['stats']['reviews_count']} reviews
- {data['stats']['notifications_count']} notifications
"""
import os
import sys
import django
from datetime import datetime, timedelta
from decimal import Decimal

# Setup Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'library.settings')
django.setup()

from django.contrib.auth.models import User
from django.utils import timezone
from library_app.models import BookCategory, Book, UserProfile, BorrowRecord, Review, Notification

# Extracted data from current database
USERS_DATA = {repr(data['users'])}

CATEGORIES_DATA = {repr(data['categories'])}

BOOKS_DATA = {repr(data['books'])}

BORROWINGS_DATA = {repr(data['borrowings'])}

REVIEWS_DATA = {repr(data['reviews'])}

NOTIFICATIONS_DATA = {repr(data['notifications'])}

def create_users():
    """Create users from extracted data"""
    print("👥 Creating users and profiles...")
    
    created_users = []
    for user_data in USERS_DATA:
        # Create or get user
        user, created = User.objects.get_or_create(
            username=user_data['username'],
            defaults={{
                'email': user_data['email'],
                'first_name': user_data['first_name'],
                'last_name': user_data['last_name'],
                'is_staff': user_data['is_staff'],
                'is_superuser': user_data['is_superuser']
            }}
        )
        
        if created:
            user.set_password('password123')  # Default password
            user.save()
            print(f"   ✅ Created user: {{user.username}}")
        else:
            print(f"   ⏭️  User already exists: {{user.username}}")
        
        # Create or update profile if exists
        if user_data['profile']:
            profile, profile_created = UserProfile.objects.get_or_create(
                user=user,
                defaults={{
                    'full_name': user_data['profile']['full_name'],
                    'address': user_data['profile']['address'],
                    'phone': user_data['profile']['phone']
                }}
            )
            
            if profile_created:
                print(f"      📝 Created profile for {{user.username}}")
        
        created_users.append(user)
    
    return created_users

def create_categories():
    """Create categories from extracted data"""
    print("\\n📚 Creating book categories...")
    
    created_categories = []
    for category_data in CATEGORIES_DATA:
        category, created = BookCategory.objects.get_or_create(
            name=category_data['name']
        )
        if created:
            print(f"   ✅ Created category: {{category_data['name']}}")
        else:
            print(f"   ⏭️  Category already exists: {{category_data['name']}}")
        created_categories.append(category)
    
    return created_categories

def create_books(categories):
    """Create books from extracted data"""
    print("\\n📖 Creating books...")
    
    created_books = []
    category_dict = {{cat.name: cat for cat in categories}}
    
    for book_data in BOOKS_DATA:
        category = category_dict.get(book_data['category'])
        if not category:
            print(f"   ❌ Category not found: {{book_data['category']}}")
            continue
        
        book, created = Book.objects.get_or_create(
            title=book_data['title'],
            author=book_data['author'],
            defaults={{
                'category': category,
                'total_copies': book_data['total_copies'],
                'available_copies': book_data['available_copies'],
                'isbn': book_data['isbn']
            }}
        )
        
        if created:
            print(f"   ✅ Created book: {{book.title}} by {{book.author}}")
            created_books.append(book)
        else:
            print(f"   ⏭️  Book already exists: {{book.title}}")
            created_books.append(book)
    
    return created_books

def create_borrowings(users, books):
    """Create borrow records from extracted data"""
    print("\\n📋 Creating borrow records...")
    
    user_dict = {{user.username: user for user in users}}
    book_dict = {{book.title: book for book in books}}
    
    created_borrowings = []
    
    for borrow_data in BORROWINGS_DATA:
        user = user_dict.get(borrow_data['user'])
        book = book_dict.get(borrow_data['book'])
        
        if not user or not book:
            print(f"   ❌ User or book not found for borrow record")
            continue
        
        # Check if record already exists
        existing = BorrowRecord.objects.filter(
            user=user,
            book=book,
            borrow_date=borrow_data['borrow_date']
        ).first()
        
        if existing:
            print(f"   ⏭️  Borrow record already exists: {{user.username}} - {{book.title}}")
            continue
        
        borrow_date = datetime.fromisoformat(borrow_data['borrow_date'].replace('Z', '+00:00'))
        return_date = None
        if borrow_data['return_date']:
            return_date = datetime.fromisoformat(borrow_data['return_date'].replace('Z', '+00:00'))
        
        due_date = None
        if borrow_data['due_date']:
            due_date = datetime.fromisoformat(borrow_data['due_date'].replace('Z', '+00:00'))
        
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
        print(f"   ✅ {{user.username}} borrowed '{{book.title}}' ({{status}})")
        created_borrowings.append(borrow_record)
    
    return created_borrowings

def create_reviews(users, books):
    """Create reviews from extracted data"""
    print("\\n⭐ Creating reviews...")
    
    user_dict = {{user.username: user for user in users}}
    book_dict = {{book.title: book for book in books}}
    
    created_reviews = []
    
    for review_data in REVIEWS_DATA:
        user = user_dict.get(review_data['user'])
        book = book_dict.get(review_data['book'])
        
        if not user or not book:
            print(f"   ❌ User or book not found for review")
            continue
        
        # Check if review already exists
        existing_review = Review.objects.filter(user=user, book=book).first()
        if existing_review:
            print(f"   ⏭️  Review already exists: {{user.username}} - {{book.title}}")
            continue
        
        created_at = datetime.fromisoformat(review_data['created_at'].replace('Z', '+00:00'))
        
        review = Review.objects.create(
            user=user,
            book=book,
            content=review_data['content'],
            rating=review_data['rating'],
            created_at=created_at
        )
        
        print(f"   ✅ {{user.username}} reviewed '{{book.title}}' - {{review_data['rating']}}⭐")
        created_reviews.append(review)
    
    return created_reviews

def create_notifications(users):
    """Create notifications from extracted data"""
    print("\\n🔔 Creating notifications...")
    
    user_dict = {{user.username: user for user in users}}
    
    created_notifications = []
    
    for notif_data in NOTIFICATIONS_DATA:
        user = user_dict.get(notif_data['user'])
        
        if not user:
            print(f"   ❌ User not found for notification")
            continue
        
        created_at = datetime.fromisoformat(notif_data['created_at'].replace('Z', '+00:00'))
        
        notification = Notification.objects.create(
            user=user,
            message=notif_data['message'],
            created_at=created_at,
            is_read=notif_data['is_read']
        )
        
        status = "📖 Read" if notif_data['is_read'] else "🔔 Unread"
        print(f"   ✅ Notification for {{user.username}}: {{status}}")
        created_notifications.append(notification)
    
    return created_notifications

def show_summary():
    """Show database population summary"""
    print("\\n" + "="*60)
    print("📊 DATABASE POPULATION SUMMARY")
    print("="*60)
    
    print(f"👥 Users: {{User.objects.count()}}")
    print(f"📝 User Profiles: {{UserProfile.objects.count()}}")
    print(f"📚 Categories: {{BookCategory.objects.count()}}")
    print(f"📖 Books: {{Book.objects.count()}}")
    print(f"📋 Borrow Records: {{BorrowRecord.objects.count()}}")
    print(f"   - Active: {{BorrowRecord.objects.filter(is_returned=False).count()}}")
    print(f"   - Returned: {{BorrowRecord.objects.filter(is_returned=True).count()}}")
    print(f"⭐ Reviews: {{Review.objects.count()}}")
    print(f"🔔 Notifications: {{Notification.objects.count()}}")
    print(f"   - Unread: {{Notification.objects.filter(is_read=False).count()}}")
    
    # Show some statistics
    total_books = Book.objects.count()
    if total_books > 0:
        total_copies = sum(book.total_copies for book in Book.objects.all())
        available_copies = sum(book.available_copies for book in Book.objects.all())
        borrowed_copies = total_copies - available_copies
        
        print(f"\\n📊 Library Statistics:")
        print(f"   - Total book copies: {{total_copies}}")
        print(f"   - Available copies: {{available_copies}}")
        print(f"   - Currently borrowed: {{borrowed_copies}}")
    
    # Show average rating
    reviews = Review.objects.all()
    if reviews:
        avg_rating = sum(r.rating for r in reviews) / len(reviews)
        print(f"   - Average book rating: {{avg_rating:.1f}}⭐")
    
    print(f"\\n🎉 Database population completed successfully!")
    print(f"💡 Default password for all users: 'password123'")

def main():
    """Main function to populate the database"""
    print("🗄️ Library Database Population Script")
    print("Generated from existing database snapshot")
    print("="*50)
    print("This script will recreate your current database structure.")
    print("⚠️  This will add data to your existing database.")
    
    response = input("\\nContinue? (y/N): ").lower().strip()
    if response != 'y':
        print("❌ Operation cancelled by user")
        return
    
    try:
        # Create all data in order
        users = create_users()
        categories = create_categories()
        books = create_books(categories)
        borrowings = create_borrowings(users, books)
        reviews = create_reviews(users, books)
        notifications = create_notifications(users)
        
        # Show summary
        show_summary()
        
    except Exception as e:
        print(f"\\n❌ Error during database population: {{str(e)}}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()
'''
    
    script_filename = f"populate_from_snapshot_{datetime.now().strftime('%Y%m%d_%H%M%S')}.py"
    
    with open(script_filename, 'w', encoding='utf-8') as f:
        f.write(script_content)
    
    print(f"📝 Generated population script: {script_filename}")
    return script_filename

def show_current_stats():
    """Show current database statistics"""
    print("\n📊 CURRENT DATABASE STATISTICS")
    print("="*50)
    
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
    
    # Show category breakdown
    print(f"\n📚 Categories breakdown:")
    for category in BookCategory.objects.all():
        book_count = Book.objects.filter(category=category).count()
        print(f"   - {category.name}: {book_count} books")
    
    # Show recent activity
    print(f"\n📋 Recent borrow activity:")
    recent_borrows = BorrowRecord.objects.order_by('-borrow_date')[:5]
    for borrow in recent_borrows:
        status = "✅ Returned" if borrow.is_returned else "📖 Active"
        print(f"   - {borrow.user.username} borrowed '{borrow.book.title}' ({status})")

def main():
    """Main function"""
    print("🔍 Database Extraction and Population Script Generator")
    print("="*60)
    print("This script will:")
    print("1. Extract all current data from your database")
    print("2. Save it as a JSON snapshot")
    print("3. Generate a new population script based on your data")
    print()
    
    # Show current stats
    show_current_stats()
    
    response = input("\nProceed with extraction? (y/N): ").lower().strip()
    if response != 'y':
        print("❌ Operation cancelled by user")
        return
    
    try:
        # Extract current data
        data = extract_current_data()
        
        # Save snapshot
        json_file = save_extracted_data(data)
        
        # Generate population script
        script_file = generate_population_script(data)
        
        print(f"\n✅ Extraction completed successfully!")
        print(f"📁 Files created:")
        print(f"   • JSON snapshot: {json_file}")
        print(f"   • Population script: {script_file}")
        print(f"\n💡 You can now use the generated script to populate")
        print(f"   a fresh database with your current data structure:")
        print(f"   python {script_file}")
        
    except Exception as e:
        print(f"\n❌ Error during extraction: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()
