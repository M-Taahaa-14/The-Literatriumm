import React from 'react';

const AdminLayout = ({ children }) => {
  return (
    <div className="admin-layout">
      <nav className="admin-navbar">
        <div className="nav-brand">
          <h2>Literatrium Admin</h2>
        </div>
        <div className="nav-links">
          <a href="/admin">Dashboard</a>
          <a href="/admin/books">Manage Books</a>
          <a href="/admin/borrowings">Manage Borrowings</a>
          <a href="/admin/categories">Manage Categories</a>
          <a href="/admin/reviews">Manage Reviews</a>
        </div>
      </nav>
      <main className="admin-content">
        {children}
      </main>
    </div>
  );
};

export default AdminLayout;
