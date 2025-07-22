import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import HomePage from './pages/HomePage';
import LoginPage from './pages/LoginPage';
import SignupPage from './pages/SignupPage';
import BookListPage from './pages/BookListPage';
import BookDetailsPage from './pages/BookDetailsPage';
import MyBorrowingsPage from './pages/MyBorrowingsPage';
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
  if (!isAdmin) return <Navigate to="/home" replace />; 
  return children;
}

function PublicRoute({ children }) {
  const token = localStorage.getItem('token');
  const isAdmin = localStorage.getItem('is_admin') === 'true';
  
  if (token) {
    return <Navigate to={isAdmin ? "/admin/dashboard" : "/home"} replace />;
  }
  return children;
}

function App() {
  return (
    <Router>
      <Routes>
        <Route element={<Layout />}>
          <Route path="/" element={<ProtectedRoute><HomePage /></ProtectedRoute>} />
          <Route path="/login" element={<PublicRoute><LoginPage /></PublicRoute>} />
          <Route path="/signup" element={<PublicRoute><SignupPage /></PublicRoute>} />
          <Route path="/home" element={<ProtectedRoute><HomePage /></ProtectedRoute>} />
          <Route path="/books" element={<ProtectedRoute><BookListPage /></ProtectedRoute>} />
          <Route path="/books/:id" element={<ProtectedRoute><BookDetailsPage /></ProtectedRoute>} />
          <Route path="/user_borrowings" element={<ProtectedRoute><MyBorrowingsPage /></ProtectedRoute>} />
          <Route path="/top-books" element={<ProtectedRoute><TopBooksPage /></ProtectedRoute>} />
          </Route>

        <Route element={<AdminLayout />}>
          <Route path="/admin/dashboard" element={<AdminProtectedRoute><AdminDashboardPage /></AdminProtectedRoute>} />
          <Route path="/admin/books" element={<AdminProtectedRoute><AdminManageBooksPage /></AdminProtectedRoute>} />
          <Route path="/admin/books/add" element={<AdminProtectedRoute><AdminAddBookPage /></AdminProtectedRoute>} />
          <Route path="/admin/borrowings" element={<AdminProtectedRoute><AdminManageBorrowingsPage /></AdminProtectedRoute>} />
          <Route path="/admin/categories" element={<AdminProtectedRoute><AdminManageCategoriesPage /></AdminProtectedRoute>} />
          <Route path="/admin/reviews" element={<AdminProtectedRoute><ManageReviewsPage /></AdminProtectedRoute>} />
        </Route>
      </Routes>
    </Router>
  );
}

export default App;
