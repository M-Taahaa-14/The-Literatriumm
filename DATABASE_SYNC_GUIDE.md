# Database Synchronization Across Devices

This guide explains how to sync your library database across multiple devices using GitHub.

## 📋 Overview

The database sync system uses two Python scripts:
- `export_database.py` - Exports your current database to JSON files
- `import_database.py` - Imports database from JSON files

## 🚀 Setup Instructions

### 1. Initial Export (Device 1)

On your current device with the populated database:

```bash
# Navigate to your library project
cd "d:\Git Practice\library"

# Export your current database
python export_database.py
```

This will:
- Create a `database_export/` folder
- Export all your data to timestamped JSON files
- Create "latest" files for easy access
- Show a summary of exported data

### 2. Commit and Push to GitHub

```bash
# Add the exported files to git
git add database_export/

# Commit the export
git commit -m "Database export - $(date)"

# Push to GitHub
git push origin main
```

## 📥 Import on Another Device (Device 2)

### 1. Clone/Pull the Repository

```bash
# If first time, clone the repository
git clone https://github.com/YOUR-USERNAME/Git-Practice.git
cd Git-Practice/library

# If already cloned, just pull the latest changes
git pull origin main
```

### 2. Setup Django Environment

```bash
# Install dependencies (if needed)
pip install django

# Run migrations to create database structure
python manage.py migrate
```

### 3. Import the Database

```bash
# Import the database from exported files
python import_database.py
```

This will:
- Load all JSON files from `database_export/`
- Create users, categories, books, borrowings, reviews, and notifications
- Skip existing records to avoid duplicates
- Show a summary of imported data

### 4. Start the Server

```bash
# Start your Django server
python manage.py runserver
```

## 🔄 Regular Syncing Workflow

### From Device 1 (Export)
```bash
python export_database.py
git add database_export/
git commit -m "Database sync - $(date)"
git push origin main
```

### To Device 2 (Import)
```bash
git pull origin main
python import_database.py
```

## 📁 File Structure

After export, you'll have:
```
database_export/
├── latest_users.json          # Current users and profiles
├── latest_categories.json     # Book categories
├── latest_books.json          # All books
├── latest_borrowings.json     # Borrow records
├── latest_reviews.json        # Book reviews
├── latest_notifications.json  # User notifications
├── latest_metadata.json       # Export information
├── users_20250724_143022.json # Timestamped backup
├── categories_20250724_143022.json
└── ... (timestamped backups)
```

## ⚠️ Important Notes

### Security
- Default password for all users is `password123`
- Admin user: username=`admin`, password=`password123`
- Change passwords after import for security

### Data Safety
- The import script skips existing records to avoid duplicates
- Timestamped backups are kept for safety
- Always test import on a development database first

### Limitations
- Book cover images are not synced (only file paths)
- User passwords are reset to default
- File attachments need separate syncing

## 🛠️ Troubleshooting

### Import Fails
```bash
# Run migrations first
python manage.py migrate

# Then try import again
python import_database.py
```

### Missing Export Files
```bash
# Check if files exist
ls database_export/

# If missing, pull latest changes
git pull origin main
```

### Permission Issues
```bash
# Ensure you're in the correct directory
cd "path/to/your/library/project"

# Check file permissions
ls -la database_export/
```

## 📊 What Gets Synced

✅ **Included:**
- User accounts and profiles
- Book categories
- Books (title, author, ISBN, copies)
- Borrow records and history
- Reviews and ratings
- Notifications

❌ **Not Included:**
- User passwords (reset to default)
- Book cover image files
- Django sessions
- Log files

## 🔧 Advanced Usage

### Export Specific Date Range
The scripts export all data. For partial exports, modify the scripts to filter by date ranges.

### Multiple Export Formats
The current system uses JSON. You can modify to export to:
- CSV files
- Django fixtures
- SQL dumps

### Automated Syncing
Set up automated exports using:
- Cron jobs (Linux/Mac)
- Task Scheduler (Windows)
- GitHub Actions

## 💡 Tips

1. **Regular Exports**: Export database changes regularly (daily/weekly)
2. **Backup Before Import**: Always backup your current database before importing
3. **Test First**: Try import on a test database first
4. **Document Changes**: Use descriptive commit messages for exports
5. **Version Control**: Keep multiple timestamped exports for rollback options

## 🆘 Support

If you encounter issues:
1. Check file permissions and paths
2. Ensure Django migrations are up to date
3. Verify JSON file integrity
4. Check console output for specific error messages
5. Try importing on a fresh database for testing

Happy syncing! 🚀
