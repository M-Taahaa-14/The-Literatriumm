# Analytics Microservice

A Flask-based REST API for library management analytics, providing data insights for the main Django + React application.

## Features
- Books borrowed per month analytics
- Top 10 most borrowed books
- Books borrowed by category breakdown
- Books borrowed vs returned comparison

## Tech Stack
- **Backend**: Flask + SQLAlchemy
- **Database**: PostgreSQL
- **API**: RESTful JSON endpoints
- **CORS**: Enabled for React frontend integration

## Setup
1. Install dependencies: `pip install -r requirements.txt`
2. Configure database in `.env` file
3. Run: `python app.py`

## API Endpoints
- `GET /analytics/borrowed-per-month` - Monthly borrowing trends
- `GET /analytics/top-10-books` - Most popular books
- `GET /analytics/borrowed-by-category` - Category-wise breakdown
- `GET /analytics/borrowed-vs-returned` - Borrow vs return statistics

## Development
Each feature is developed on separate branches following PR-based workflow.
