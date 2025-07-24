# Library Management System - Full Stack Project

A comprehensive library management system built with Django REST Framework, React, and Flask microservices.

## 🏗️ Architecture Overview

- **Django Backend** (`library/`) - Main application with REST API (SQLite)
- **React Frontend** (`frontend/`) - User interface for library operations
- **Flask Analytics** (`analytics/`) - Microservice for analytics and reporting (PostgreSQL)

## 📁 Project Structure

```
library-management-system/
├── library/                    # Django Backend (SQLite)
│   ├── library_app/           # Django app (models, templates, etc.)
│   ├── library_api/           # Django REST Framework API
│   ├── manage.py
│   └── db.sqlite3
├── frontend/                   # React Frontend
│   ├── src/
│   │   ├── components/
│   │   │   ├── Layout.js          # User layout (navbar, profile, notifications)
│   │   │   └── AdminLayout.js     # Admin layout (navbar)
│   │   ├── pages/
│   │   │   ├── HomePage.js
│   │   │   ├── LoginPage.js
│   │   │   ├── SignupPage.js
│   │   │   ├── BookListPage.js
│   │   │   ├── BookDetailsPage.js
│   │   │   ├── MyBorrowingsPage.js
│   │   │   ├── ManageReviewsPage.js
│   │   │   ├── AdminDashboardPage.js
│   │   │   ├── AdminManageBooksPage.js
│   │   │   ├── AdminAddBookPage.js
│   │   │   ├── AdminManageBorrowingsPage.js
│   │   │   └── AdminManageCategoriesPage.js
│   │   ├── App.js
│   │   └── index.js
│   └── package.json
├── analytics/                  # Flask Analytics Microservice (PostgreSQL)
│   ├── app.py                 # Flask application factory
│   ├── models.py              # SQLAlchemy models
│   ├── services.py            # Business logic layer
│   ├── config.py              # Configuration settings
│   ├── requirements.txt       # Python dependencies
│   └── README.md              # Analytics service documentation
└── README.md                  # This file
```

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Node.js 16+
- PostgreSQL (for analytics)

### 1. Django Backend Setup
```bash
cd library
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

### 2. React Frontend Setup
```bash
cd frontend
npm install
npm start
```

### 3. Flask Analytics Setup
```bash
cd analytics
pip install -r requirements.txt
cp .env.example .env
# Edit .env with your PostgreSQL credentials
python app.py
```

## 🌟 Services Overview

### Django Backend (Port 8000)
- **Purpose**: Main library management operations
- **Database**: SQLite
- **Features**: User management, book catalog, borrowing system, categories
- **API**: RESTful API for frontend consumption

### React Frontend (Port 3000)
- **Purpose**: User interface for library operations
- **Features**: Book browsing, user dashboard, admin panel, responsive design
- **Integration**: Consumes Django REST API

### Flask Analytics (Port 5001)
- **Purpose**: Analytics and reporting microservice
- **Database**: PostgreSQL (separate from main app)
- **Features**: Borrowing analytics, usage statistics, data visualization endpoints

## 📊 Analytics API Endpoints

- `GET /analytics/borrowed-per-month` - Monthly borrowing trends
- `GET /analytics/top-10-books` - Most popular books
- `GET /analytics/borrowed-by-category` - Category-wise statistics
- `GET /analytics/borrowed-vs-returned` - Return rate analysis

## 🔄 Git Workflow Strategy

### Branch Structure
- `main` - Production-ready code
- `deployment` - Deployment configurations
- `feature/*` - Feature development branches

### Development Process
1. Start from latest `main`
2. Create feature branch: `git checkout -b feature/feature-name`
3. Develop, test, and commit incrementally
4. Push feature branch and create Pull Request
5. Code review and merge to `main`
6. Start next feature from updated `main`

### Commit Guidelines
- Use clear, descriptive commit messages
- Keep commits focused and atomic
- Follow conventional commit format when possible

## 💾 Database Synchronization Across Devices

When working on multiple devices, you need to sync your database state. This project uses Django fixtures for cross-device database synchronization.

### 🗄️ Sync Tool Usage

The project includes a `sync_database.py` script for easy database synchronization:

```bash
cd library
python sync_database.py [command]
```

#### Available Commands:
- `export` - Export current database to fixtures
- `import` - Import database from fixtures  
- `setup` - Setup fresh database (run migrations)
- `status` - Show current database and sync status

### 📤 Exporting Database (Device 1)

```bash
# Export your current database
cd library
python sync_database.py export

# Commit and push the database files
git add database_sync/
git commit -m "Database sync - $(date +%Y%m%d)"
git push origin main
```

This creates:
- `database_sync/full_backup_TIMESTAMP.json` - Complete database backup
- `database_sync/library_data_TIMESTAMP.json` - Library app data only
- `database_sync/users_TIMESTAMP.json` - User accounts and profiles
- `database_sync/latest_*.json` - Latest versions for easy import
- `database_sync/sync_info.json` - Sync metadata and statistics

### 📥 Importing Database (Device 2)

```bash
# Pull the latest changes
git pull origin main

# For fresh setup (first time)
cd library
python sync_database.py setup
python sync_database.py import

# For existing setup
cd library
python sync_database.py import
```

### 🔄 Regular Sync Workflow

#### On your main development device:
```bash
# After making database changes (adding books, users, etc.)
python sync_database.py export
git add database_sync/
git commit -m "Database sync: Added new books and categories"
git push origin main
```

#### On your secondary device:
```bash
# Pull latest changes including database
git pull origin main
python sync_database.py import

# Start working
python manage.py runserver
```

### 📊 Checking Sync Status

```bash
# View current database state and available sync files
python sync_database.py status
```

### ⚠️ Important Notes

1. **Backup First**: Always backup important data before importing
2. **Development Only**: This method is ideal for development/testing
3. **User Passwords**: User passwords are included in sync (development convenience)
4. **Production**: For production, use proper database migration strategies
5. **Conflicts**: Import overwrites existing data - handle conflicts manually if needed

### 🎯 Benefits

- ✅ **Git Integration**: Database state is version controlled
- ✅ **Cross-Device Sync**: Work seamlessly across multiple devices  
- ✅ **Easy Setup**: New team members can get full database quickly
- ✅ **Selective Sync**: Choose what data to sync
- ✅ **Backup History**: All database states are preserved in Git history
- ✅ **Development Friendly**: Perfect for development and testing environments

### 📁 File Structure

```
library/
├── sync_database.py           # Database sync tool
├── database_sync/             # Sync files directory
│   ├── .gitkeep              # Ensures directory is tracked
│   ├── latest_full_backup.json
│   ├── latest_library_data.json
│   ├── latest_users.json
│   ├── sync_info.json
│   └── [timestamped backups...]
```

## 🔧 Data Synchronization

The analytics microservice requires data synchronization from Django to PostgreSQL:
- Manual sync script for transferring data between databases
- Scheduled sync capability for regular updates
- Maintains data consistency between SQLite and PostgreSQL

## 🧪 Testing

Each service includes its own testing setup:
- Django: `python manage.py test`
- React: `npm test`
- Flask: `pytest`
- **SearchPage.js**: Search books by title/author, paginated.
- **MyBorrowingsPage.js**: User's borrow records.
- **UserBorrowingsPage.js**: (Admin) All users' borrow records.

### Admin Pages
- **AdminDashboardPage.js**: Stats (users, books, borrowings, reviews, categories).
- **AdminManageBooksPage.js**: Manage/search all books, paginated.
- **AdminAddBookPage.js**: Add a new book.
- **AdminManageBorrowingsPage.js**: Manage borrowings, filter by status, send reminders, update fines.
- **AdminManageCategoriesPage.js**: Add/edit/delete categories.
- **ManageReviewsPage.js**: (Admin) Manage, filter, and delete reviews.

### Layouts/Components
- **Layout.js**: User navbar, profile dropdown, notification bell, shared layout.
- **AdminLayout.js**: Admin navbar, shared layout.

## Setup & Usage

### 1. Backend (Django + DRF)
- Install dependencies:
  ```bash
  cd library
  pip install -r requirements.txt
  ```
- Run migrations:
  ```bash
  python manage.py migrate
  ```
- Create a superuser (for admin):
  ```bash
  python manage.py createsuperuser
  ```
- Start the backend server:
  ```bash
  python manage.py runserver
  ```
- The API will be available at `http://localhost:8000/api/`

### 2. Frontend (React)
- Install dependencies:
  ```bash
  cd frontend
  npm install
  ```
- Start the React app:
  ```bash
  npm start
  ```
- The frontend will run at `http://localhost:3000/`

### 3. API Proxy (for local dev)
- To avoid CORS issues, add this to `frontend/package.json`:
  ```json
  "proxy": "http://localhost:8000"
  ```
- This lets React make API calls to Django without CORS errors.

### 4. Usage
- Register/login as a user to borrow books, review, etc.
- Login as admin (superuser) to access admin dashboard and management pages.
- All navigation, profile, and notifications are available in the navbar.

## Notes
- All pages are responsive and styled with Bootstrap.
- Pagination is implemented for all book lists and search.
- User profile and notifications are available in the navbar when logged in.
- Admin and user pages are separated by layout and permissions.

---

For any issues, check your browser console and Django server logs for errors. 