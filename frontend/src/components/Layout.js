import React from 'react';

const Layout = ({ children }) => {
  return (
    <div className="layout">
      <nav className="navbar">
        <div className="nav-brand">
          <h2>Literatrium</h2>
        </div>
        <div className="nav-links">
          <a href="/">Home</a>
          <a href="/books">Books</a>
          <a href="/my-borrowings">My Borrowings</a>
          <div className="user-menu">
            <span>Profile</span>
            <span>Notifications</span>
            <span>Logout</span>
          </div>
        </div>
      </nav>
      <main className="main-content">
        {children}
      </main>
    </div>
  );
};

export default Layout;
