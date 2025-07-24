"""
Database Sync Script for Cross-Device Development
Exports and imports Django database data using fixtures
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

from django.core.management import call_command
from django.core.management.base import CommandError
from library_app.models import Book, BookCategory, BorrowRecord, UserProfile, Review, Notification
from django.contrib.auth.models import User

def create_sync_directory():
    """Create database_sync directory if it doesn't exist"""
    sync_dir = Path('database_sync')
    sync_dir.mkdir(exist_ok=True)
    return sync_dir

def export_database():
    """Export all database data to fixtures"""
    print("🗄️ Starting database export...")
    
    sync_dir = create_sync_directory()
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    try:
        # Export all data to a comprehensive fixture
        full_backup_path = sync_dir / f"full_backup_{timestamp}.json"
        print(f"📦 Exporting full database to {full_backup_path}")
        
        with open(full_backup_path, 'w') as f:
            call_command('dumpdata', 
                        '--indent=2', 
                        stdout=f)
        
        # Export specific app data
        library_backup_path = sync_dir / f"library_data_{timestamp}.json"
        print(f"📚 Exporting library app data to {library_backup_path}")
        
        with open(library_backup_path, 'w') as f:
            call_command('dumpdata', 
                        'library_app',
                        '--indent=2', 
                        stdout=f)
        
        # Export users (for development - in production, handle separately)
        users_backup_path = sync_dir / f"users_{timestamp}.json"
        print(f"👥 Exporting user data to {users_backup_path}")
        
        with open(users_backup_path, 'w') as f:
            call_command('dumpdata', 
                        'auth.User',
                        'library_app.UserProfile',
                        '--indent=2', 
                        stdout=f)
        
        # Create a "latest" symlink/copy for easy access
        latest_full = sync_dir / "latest_full_backup.json"
        latest_library = sync_dir / "latest_library_data.json"
        latest_users = sync_dir / "latest_users.json"
        
        # Copy to latest files
        import shutil
        shutil.copy2(full_backup_path, latest_full)
        shutil.copy2(library_backup_path, latest_library)
        shutil.copy2(users_backup_path, latest_users)
        
        # Create sync info
        sync_info = {
            "export_date": datetime.now().isoformat(),
            "timestamp": timestamp,
            "files": {
                "full_backup": str(full_backup_path.name),
                "library_data": str(library_backup_path.name),
                "users": str(users_backup_path.name)
            },
            "stats": get_database_stats()
        }
        
        with open(sync_dir / "sync_info.json", 'w') as f:
            json.dump(sync_info, f, indent=2)
        
        print("\n✅ Database export completed successfully!")
        print(f"📁 Files created in: {sync_dir}")
        print(f"   • Full backup: {full_backup_path.name}")
        print(f"   • Library data: {library_backup_path.name}")
        print(f"   • Users: {users_backup_path.name}")
        print(f"   • Latest symlinks created for easy access")
        
        # Display stats
        stats = get_database_stats()
        print(f"\n📊 Export Statistics:")
        for model_name, count in stats.items():
            print(f"   • {model_name}: {count} records")
        
        print(f"\n💡 To sync to another device:")
        print(f"   1. Commit these files: git add database_sync/ && git commit -m 'Database sync {timestamp}'")
        print(f"   2. Push: git push origin main")
        print(f"   3. On other device: git pull && python sync_database.py import")
        
    except Exception as e:
        print(f"❌ Export failed: {str(e)}")
        return False
    
    return True

def import_database():
    """Import database data from fixtures"""
    print("📥 Starting database import...")
    
    sync_dir = Path('database_sync')
    
    if not sync_dir.exists():
        print(f"❌ Sync directory not found: {sync_dir}")
        print("   Make sure you've pulled the latest changes with database_sync folder")
        return False
    
    # Check for latest files
    latest_full = sync_dir / "latest_full_backup.json"
    latest_library = sync_dir / "latest_library_data.json"
    latest_users = sync_dir / "latest_users.json"
    
    if not latest_full.exists():
        print("❌ No backup files found in database_sync/")
        print("   Available files:", list(sync_dir.glob("*.json")))
        return False
    
    try:
        # Show sync info
        sync_info_path = sync_dir / "sync_info.json"
        if sync_info_path.exists():
            with open(sync_info_path, 'r') as f:
                sync_info = json.load(f)
                print(f"📅 Import data from: {sync_info['export_date']}")
                print(f"📊 Data summary:")
                for model_name, count in sync_info['stats'].items():
                    print(f"   • {model_name}: {count} records")
        
        print(f"\n⚠️  This will overwrite your current database!")
        response = input("Continue? (y/N): ").lower().strip()
        
        if response != 'y':
            print("❌ Import cancelled by user")
            return False
        
        print(f"🗄️ Importing database from fixtures...")
        
        # Import in order: users first, then library data
        print(f"👥 Importing users...")
        call_command('loaddata', str(latest_users))
        
        print(f"📚 Importing library data...")
        call_command('loaddata', str(latest_library))
        
        print(f"\n✅ Database import completed successfully!")
        
        # Show current stats
        stats = get_database_stats()
        print(f"\n📊 Current Database Statistics:")
        for model_name, count in stats.items():
            print(f"   • {model_name}: {count} records")
        
        print(f"\n🎉 Your database is now synced!")
        print(f"💡 You can now run: python manage.py runserver")
        
    except Exception as e:
        print(f"❌ Import failed: {str(e)}")
        print(f"💡 Try running migrations first: python manage.py migrate")
        return False
    
    return True

def get_database_stats():
    """Get current database statistics"""
    try:
        return {
            "Users": User.objects.count(),
            "User Profiles": UserProfile.objects.count(),
            "Categories": BookCategory.objects.count(),
            "Books": Book.objects.count(),
            "Borrow Records": BorrowRecord.objects.count(),
            "Reviews": Review.objects.count(),
            "Notifications": Notification.objects.count(),
        }
    except Exception as e:
        return {"Error": f"Could not get stats: {str(e)}"}

def setup_fresh_database():
    """Setup a fresh database with migrations"""
    print("🔧 Setting up fresh database...")
    
    try:
        print("📋 Running migrations...")
        call_command('migrate')
        
        print("✅ Fresh database setup completed!")
        print("💡 Now run: python sync_database.py import")
        
    except Exception as e:
        print(f"❌ Setup failed: {str(e)}")
        return False
    
    return True

def show_status():
    """Show current database status and available sync files"""
    print("📊 Database Sync Status")
    print("=" * 50)
    
    # Current database stats
    stats = get_database_stats()
    print("Current Database:")
    for model_name, count in stats.items():
        print(f"  • {model_name}: {count} records")
    
    # Available sync files
    sync_dir = Path('database_sync')
    if sync_dir.exists():
        print(f"\nAvailable Sync Files:")
        backup_files = list(sync_dir.glob("*.json"))
        if backup_files:
            for file in sorted(backup_files):
                size = file.stat().st_size / 1024  # KB
                print(f"  • {file.name} ({size:.1f} KB)")
        else:
            print("  • No sync files found")
    else:
        print(f"\nNo sync directory found")
    
    # Latest sync info
    sync_info_path = sync_dir / "sync_info.json" if sync_dir.exists() else None
    if sync_info_path and sync_info_path.exists():
        with open(sync_info_path, 'r') as f:
            sync_info = json.load(f)
            print(f"\nLatest Export: {sync_info['export_date']}")

def main():
    """Main function"""
    if len(sys.argv) < 2:
        print("🗄️ Database Sync Tool")
        print("=" * 50)
        print("Usage: python sync_database.py [command]")
        print("")
        print("Commands:")
        print("  export    - Export current database to fixtures")
        print("  import    - Import database from fixtures")
        print("  setup     - Setup fresh database (run migrations)")
        print("  status    - Show current database and sync status")
        print("")
        print("Typical workflow:")
        print("  Device 1: python sync_database.py export")
        print("           git add . && git commit -m 'Database sync' && git push")
        print("  Device 2: git pull")
        print("           python sync_database.py setup  # if fresh setup")
        print("           python sync_database.py import")
        return
    
    command = sys.argv[1].lower()
    
    if command == 'export':
        export_database()
    elif command == 'import':
        import_database()
    elif command == 'setup':
        setup_fresh_database()
    elif command == 'status':
        show_status()
    else:
        print(f"❌ Unknown command: {command}")
        print("Valid commands: export, import, setup, status")

if __name__ == '__main__':
    main()
