# Analytics Microservice - Flask

This microservice handles analytics and reporting for the library management system.

## Setup Instructions

### 1. Install Dependencies
```bash
cd analytics
pip install -r requirements.txt
```

### 2. Environment Configuration
```bash
cp .env.example .env
# Edit .env with your database credentials
```

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

### Analytics Endpoints (To be implemented)
- `GET /analytics/borrowed-per-month` - Monthly borrowing statistics
- `GET /analytics/top-10-books` - Most borrowed books
- `GET /analytics/borrowed-by-category` - Borrowings by book category  
- `GET /analytics/borrowed-vs-returned` - Borrowed vs returned statistics

## Response Format
All analytics endpoints return data in the format:
```json
{
  "labels": ["Label1", "Label2", ...],
  "values": [value1, value2, ...]
}
```

## Database Models
- `User` - User information (mirrors Django model)
- `Category` - Book categories
- `Book` - Book information with category relationship
- `Borrowing` - Core borrowing records for analytics

## Development
- The service uses Flask application factory pattern
- SQLAlchemy for ORM
- CORS enabled for React frontend integration
- PostgreSQL for analytics data storage
