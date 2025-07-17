# Literatium-2.0
Django Rest Framework
# Literatrium 2.0

## Project Structure

```
Literatrium - 2.0/
├── library/                  # Django backend
│   ├── library_app/          # Django app (models, templates, etc.)
│   ├── library_api/          # Django REST Framework API
│   ├── manage.py
│   └── ...
├── frontend/                 # React frontend (new)
│   ├── src/
│   │   ├── components/
│   │   │   ├── Layout.js         # User layout (navbar, profile, notifications)
│   │   │   └── AdminLayout.js    # Admin layout (navbar)
│   │   ├── pages/
│   │   │   ├── HomePage.js
│   │   │   ├── LoginPage.js
│   │   │   ├── SignupPage.js
│   │   │   ├── BookListPage.js
│   │   │   ├── BookDetailsPage.js
│   │   │   ├── BooksByCategoryPage.js
│   │   │   ├── SearchPage.js
│   │   │   ├── MyBorrowingsPage.js
│   │   │   ├── UserBorrowingsPage.js
│   │   │   ├── ManageReviewsPage.js
│   │   │   ├── AdminDashboardPage.js
│   │   │   ├── AdminManageBooksPage.js
│   │   │   ├── AdminAddBookPage.js
│   │   │   ├── AdminManageBorrowingsPage.js
│   │   │   └── AdminManageCategoriesPage.js
│   │   ├── App.js
│   │   └── index.js
│   └── ...
├── README.md                 # (this file)
└── ...
```

## Page/Component Summary

### User Pages
- **HomePage.js**: Landing page, featured books, categories.
- **LoginPage.js**: User login form.
- **SignupPage.js**: User registration form.
- **BookListPage.js**: All books, paginated.
- **BookDetailsPage.js**: Book info, reviews, add review.
- **BooksByCategoryPage.js**: Books in a category, paginated.
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