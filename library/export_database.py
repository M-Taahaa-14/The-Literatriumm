"""
Database Export Script
Extracts all data from your current library database and saves it to JSON files for syncing
"""
import os
import sys
import django
import json
from datetime import datetime
from pathlib import Path

# Setup Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'library.settings')
django.setup()

from django.contrib.auth.models import User
from library_app.models import BookCategory, Book, UserProfile, BorrowRecord, Review, Notification

def create_export_directory():
    """Create database_export directory if it doesn't exist"""
    export_dir = Path('database_export')
    export_dir.mkdir(exist_ok=True)
    return export_dir

def export_users():
    """Export all users and their profiles"""
    print("👥 Exporting users and profiles...")
    
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
    
    print(f"   ✅ Exported {len(users_data)} users")
    return users_data

def export_categories():
    """Export all book categories"""
    print("📚 Exporting categories...")
    
    categories_data = []
    for category in BookCategory.objects.all():
        categories_data.append({
            'id': category.id,
            'name': category.name,
        })
    
    print(f"   ✅ Exported {len(categories_data)} categories")
    return categories_data

def export_books():
    """Export all books"""
    print("📖 Exporting books...")
    
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
    
    print(f"   ✅ Exported {len(books_data)} books")
    return books_data

def export_borrowings():
    """Export all borrow records"""
    print("📋 Exporting borrow records...")
    
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
    
    print(f"   ✅ Exported {len(borrowings_data)} borrow records")
    return borrowings_data

def export_reviews():
    """Export all reviews"""
    print("⭐ Exporting reviews...")
    
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
    
    print(f"   ✅ Exported {len(reviews_data)} reviews")
    return reviews_data

def export_notifications():
    """Export all notifications"""
    print("🔔 Exporting notifications...")
    
    notifications_data = []
    for notification in Notification.objects.all():
        notifications_data.append({
            'id': notification.id,
            'user': notification.user.username,
            'message': notification.message,
            'created_at': notification.created_at.isoformat(),
            'is_read': notification.is_read,
        })
    
    print(f"   ✅ Exported {len(notifications_data)} notifications")
    return notifications_data

def save_export_data(export_dir, data):
    """Save all exported data to separate JSON files"""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    files_created = []
    
    # Save each data type to separate files
    for data_type, content in data.items():
        if data_type in ['export_date', 'stats']:
            continue
            
        filename = export_dir / f"{data_type}_{timestamp}.json"
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(content, f, indent=2, ensure_ascii=False)
        
        files_created.append(filename)
        print(f"   💾 Saved {data_type} to {filename.name}")
    
    # Save metadata
    metadata = {
        'export_date': data['export_date'],
        'timestamp': timestamp,
        'stats': data['stats'],
        'files': {
            'users': f"users_{timestamp}.json",
            'categories': f"categories_{timestamp}.json",
            'books': f"books_{timestamp}.json",
            'borrowings': f"borrowings_{timestamp}.json",
            'reviews': f"reviews_{timestamp}.json",
            'notifications': f"notifications_{timestamp}.json"
        }
    }
    
    metadata_file = export_dir / f"export_metadata_{timestamp}.json"
    with open(metadata_file, 'w', encoding='utf-8') as f:
        json.dump(metadata, f, indent=2, ensure_ascii=False)
    
    files_created.append(metadata_file)
    print(f"   📋 Saved metadata to {metadata_file.name}")
    
    # Create "latest" symlinks/copies for easy access
    latest_files = {}
    for data_type in ['users', 'categories', 'books', 'borrowings', 'reviews', 'notifications']:
        latest_file = export_dir / f"latest_{data_type}.json"
        source_file = export_dir / f"{data_type}_{timestamp}.json"
        
        # Copy to latest file
        import shutil
        shutil.copy2(source_file, latest_file)
        latest_files[data_type] = latest_file.name
        print(f"   🔗 Created latest_{data_type}.json")
    
    # Create latest metadata
    latest_metadata = export_dir / "latest_metadata.json"
    shutil.copy2(metadata_file, latest_metadata)
    print(f"   🔗 Created latest_metadata.json")
    
    return files_created, latest_files

def show_export_summary(data):
    """Show summary of exported data"""
    print("\n" + "="*60)
    print("📊 DATABASE EXPORT SUMMARY")
    print("="*60)
    
    print(f"📅 Export Date: {data['export_date']}")
    print(f"👥 Users: {data['stats']['users_count']}")
    print(f"📚 Categories: {data['stats']['categories_count']}")
    print(f"📖 Books: {data['stats']['books_count']}")
    print(f"📋 Borrow Records: {data['stats']['borrowings_count']}")
    print(f"⭐ Reviews: {data['stats']['reviews_count']}")
    print(f"🔔 Notifications: {data['stats']['notifications_count']}")
    
    # Show category breakdown
    print(f"\n📚 Categories in export:")
    categories = {cat['name'] for cat in data['categories']}
    for category in sorted(categories):
        book_count = len([book for book in data['books'] if book['category'] == category])
        print(f"   - {category}: {book_count} books")

def main():
    """Main export function"""
    print("📤 Library Database Export Script")
    print("="*50)
    print("This script will export all your database data to JSON files")
    print("for syncing with another device via GitHub.")
    print()
    
    # Show current database stats
    print("📊 Current Database Statistics:")
    print(f"   👥 Users: {User.objects.count()}")
    print(f"   📚 Categories: {BookCategory.objects.count()}")
    print(f"   📖 Books: {Book.objects.count()}")
    print(f"   📋 Borrowings: {BorrowRecord.objects.count()}")
    print(f"   ⭐ Reviews: {Review.objects.count()}")
    print(f"   🔔 Notifications: {Notification.objects.count()}")
    
    response = input("\nProceed with export? (y/N): ").lower().strip()
    if response != 'y':
        print("❌ Export cancelled by user")
        return
    
    try:
        # Create export directory
        export_dir = create_export_directory()
        
        # Export all data
        print(f"\n🗄️ Starting database export...")
        
        users_data = export_users()
        categories_data = export_categories()
        books_data = export_books()
        borrowings_data = export_borrowings()
        reviews_data = export_reviews()
        notifications_data = export_notifications()
        
        # Compile all data
        export_data = {
            'users': users_data,
            'categories': categories_data,
            'books': books_data,
            'borrowings': borrowings_data,
            'reviews': reviews_data,
            'notifications': notifications_data,
            'export_date': datetime.now().isoformat(),
            'stats': {
                'users_count': len(users_data),
                'categories_count': len(categories_data),
                'books_count': len(books_data),
                'borrowings_count': len(borrowings_data),
                'reviews_count': len(reviews_data),
                'notifications_count': len(notifications_data),
            }
        }
        
        # Save to files
        files_created, latest_files = save_export_data(export_dir, export_data)
        
        # Show summary
        show_export_summary(export_data)
        
        print(f"\n✅ Export completed successfully!")
        print(f"📁 Files saved in: {export_dir}")
        print(f"📊 Total files created: {len(files_created)}")
        
        print(f"\n📤 Next Steps for GitHub Sync:")
        print(f"   1. Add files to git: git add {export_dir}/")
        print(f"   2. Commit: git commit -m 'Database export - {datetime.now().strftime('%Y-%m-%d %H:%M')}'")
        print(f"   3. Push: git push origin main")
        print(f"   4. On other device: git pull")
        print(f"   5. Run: python import_database.py")
        
    except Exception as e:
        print(f"\n❌ Export failed: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()
