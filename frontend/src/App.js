import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import HomePage from './pages/HomePage';
import LoginPage from './pages/LoginPage';
import SignupPage from './pages/SignupPage';
import BookListPage from './pages/BookListPage';
import BookDetailsPage from './pages/BookDetailsPage';
import MyBorrowingsPage from './pages/MyBorrowingsPage';
import ManageReviewsPage from './pages/ManageReviewsPage';
import AdminDashboardPage from './pages/AdminDashboardPage';
import AdminManageBooksPage from './pages/AdminManageBooksPage';
import AdminAddBookPage from './pages/AdminAddBookPage';
import AdminManageBorrowingsPage from './pages/AdminManageBorrowingsPage';
import AdminManageCategoriesPage from './pages/AdminManageCategoriesPage';
import Layout from './components/Layout';
import AdminLayout from './components/AdminLayout';

function App() {
  return (
    <Router>
      <Routes>
        <Route element={<Layout />}>
          <Route path="/" element={<HomePage />} />
          <Route path="/login" element={<LoginPage />} />
          <Route path="/signup" element={<SignupPage />} />
          <Route path="/books" element={<BookListPage />} />
          <Route path="/books/:id" element={<BookDetailsPage />} />
          <Route path="/user_borrowings" element={<MyBorrowingsPage />} />
        </Route>
        <Route element={<AdminLayout />}>
          <Route path="/admin/dashboard" element={<AdminDashboardPage />} />
          <Route path="/admin/books" element={<AdminManageBooksPage />} />
          <Route path="/admin/books/add" element={<AdminAddBookPage />} />
          <Route path="/admin/borrowings" element={<AdminManageBorrowingsPage />} />
          <Route path="/admin/categories" element={<AdminManageCategoriesPage />} />
          <Route path="/admin/reviews" element={<ManageReviewsPage />} />
        </Route>
      </Routes>
    </Router>
  );
}

export default App;
