import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import HomePage from './pages/HomePage';
import LoginPage from './pages/LoginPage';
import SignupPage from './pages/SignupPage';
import BookListPage from './pages/BookListPage';
import BookDetailsPage from './pages/BookDetailsPage';
import MyBorrowingsPage from './pages/MyBorrowingsPage';
import AnalyticsPage from './pages/AnalyticsPage';
import TopBooksPage from './pages/TopBooksPage';
import ManageReviewsPage from './pages/ManageReviewsPage';
import AdminDashboardPage from './pages/AdminDashboardPage';
import AdminManageBooksPage from './pages/AdminManageBooksPage';
import AdminAddBookPage from './pages/AdminAddBookPage';
import AdminManageBorrowingsPage from './pages/AdminManageBorrowingsPage';
import AdminManageCategoriesPage from './pages/AdminManageCategoriesPage';
import Layout from './components/Layout';
import AdminLayout from './components/AdminLayout';

function ProtectedRoute({ children }) {
  const token = localStorage.getItem('token');
  return token ? children : <Navigate to="/login" replace />;
}

function AdminProtectedRoute({ children }) {
  const token = localStorage.getItem('token');
  const isAdmin = localStorage.getItem('is_admin') === 'true';
  
  if (!token) return <Navigate to="/login" replace />;
  if (!isAdmin) return <Navigate to="/" replace />;
  return children;
}

function App() {
  return (
    <Router>
      <Routes>
        <Route element={<Layout />}>
          <Route path="/login" element={<LoginPage />} />
          <Route path="/signup" element={<SignupPage />} />
          {/* Default redirect to login */}
          <Route path="/" element={<Navigate to="/home" replace />} />
          <Route path="/home" element={<ProtectedRoute><HomePage /></ProtectedRoute>} />
          <Route path="/books" element={<ProtectedRoute><BookListPage /></ProtectedRoute>} />
          <Route path="/books/:id" element={<ProtectedRoute><BookDetailsPage /></ProtectedRoute>} />
          <Route path="/user_borrowings" element={<ProtectedRoute><MyBorrowingsPage /></ProtectedRoute>} />
          <Route path="/top-books" element={<ProtectedRoute><TopBooksPage /></ProtectedRoute>} />
          <Route path="/monthly_borrowings" element={<ProtectedRoute><AnalyticsPage /></ProtectedRoute>} />
        </Route>
        
        <Route element={<AdminProtectedRoute><AdminLayout /></AdminProtectedRoute>}>
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