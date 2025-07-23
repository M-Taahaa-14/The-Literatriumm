# Analytics Microservice - Flask

This microservice provides real-time analytics and reporting for the library management system with secure configuration management.

## 🔐 Security First Setup

**Important**: This project uses environment variables for all sensitive data. Never commit secrets to git!

### 1. Install Dependencies
```bash
cd analytics
pip install -r requirements.txt
```

### 2. Environment Configuration
```bash
cp .env.example .env
# Edit .env with your actual database credentials and secrets
```

**Required Environment Variables:**
- `SECRET_KEY` - Flask secret key for security
- `DATABASE_URL` - PostgreSQL connection string

See `ENVIRONMENT_SETUP.md` for complete configuration guide.

### 3. Database Setup
Make sure PostgreSQL is running and create the database:
```sql
CREATE DATABASE library_analytics;
```

### 4. Run the Application
```bash
python app.py
```

The analytics service will be available at `http://localhost:5001`

## API Endpoints

### Health Check
- `GET /health` - Service health status
- `GET /analytics` - Service information

### Analytics Endpoints
- `GET /analytics/borrowed-per-month` - Monthly borrowing statistics
- `GET /analytics/top-books-by-borrowings` - Top 10 books by borrowing count
- `GET /analytics/top-books-by-ratings` - Top 10 books by average rating
- `GET /analytics/borrowed-by-category` - Borrowings by book category (planned)
- `GET /analytics/borrowed-vs-returned` - Borrowed vs returned statistics (planned)

## Response Format
All analytics endpoints return data in the format:
```json
{
  "labels": ["Label1", "Label2", ...],
  "values": [value1, value2, ...]
}
```

### Top Books Endpoints Format
Top books endpoints return additional metadata:
```json
{
  "labels": ["Book Title 1", "Book Title 2", ...],
  "values": [count1, count2, ...],
  "book_details": [
    {
      "id": 1,
      "title": "Book Title",
      "author": "Author Name",
      "cover_image": "http://localhost:8000/media/book_covers/cover.jpg",
      "borrowing_count": 15,
      "average_rating": 4.5
    }
  ]
}
```

## Database Models
- `User` - User information (synced from Django)
- `Category` - Book categories (synced from Django)
- `Book` - Book information with category relationship (synced from Django)
- `Borrowing` - Core borrowing records for analytics (synced from Django)
- `Review` - Book reviews with ratings (synced from Django)

## Data Synchronization
The analytics database is automatically synchronized with the main Django database using Django signals. When data changes in the main application, it's immediately reflected in the analytics database for real-time reporting.

## Development Features
- Flask application factory pattern for modular design
- SQLAlchemy ORM with raw SQL for performance-critical queries
- CORS enabled for React frontend integration
- PostgreSQL for analytics data storage
- Environment-based configuration for security
- Real-time data sync from Django via signals
- Comprehensive error handling and logging

## 🔒 Security & GitHub Safety

This project is designed to be **GitHub-safe** with no hardcoded secrets:

✅ **What's Safe to Commit:**
- `config.py` - Only contains environment variable references
- `.env.example` - Template with example values
- All application code - No hardcoded credentials

❌ **Never Commit:**
- `.env` - Contains your actual secrets (automatically ignored by git)
- Any files with real database passwords or API keys

### Verification Before Push:
```bash
# Verify .env is ignored
git check-ignore analytics/.env

# Check for any secrets in staged files
git diff --cached | grep -i "password\|secret\|key"
```

## Frontend Integration

The React frontend (`TopBooksPage.js`) integrates with these endpoints to display:
- Interactive bar charts for top books by borrowings
- Doughnut charts for top books by ratings  
- Book cover images and metadata
- Tabbed interface for different ranking methods
