import React, { useEffect, useState, useRef } from 'react';
import { Link, Outlet, useNavigate } from 'react-router-dom';
import 'bootstrap-icons/font/bootstrap-icons.css';
import api from '../api';
import '../App.css'; 

function getInitials(name) {
    if (!name) return '';
    const parts = name.trim().split(' ');
    if (parts.length >= 2) return (parts[0][0] + parts[1][0]).toUpperCase();
    return parts[0][0].toUpperCase();
}

function Layout() {
    const [profile, setProfile] = useState(null);
    const [notifications, setNotifications] = useState([]);
    const [notifOpen, setNotifOpen] = useState(false);
    const [profileOpen, setProfileOpen] = useState(false);
    const [notifUnread, setNotifUnread] = useState(0);
    const navigate = useNavigate();
    const notifRef = useRef();
    const profileRef = useRef();

    useEffect(() => {
        const token = localStorage.getItem('token');
        if (token) {
            api.get('profile/')
                .then(res => setProfile(res.data))
                .catch(() => setProfile(null));
            api.get('notifications/')
                .then(res => {
                    setNotifications(res.data);
                    setNotifUnread(res.data.filter(n => !n.is_read).length);
                })
                .catch(() => setNotifications([]));
        } else {
            setProfile(null);
            setNotifications([]);
            setNotifUnread(0);
        }
    }, []);

    useEffect(() => {
        function handleClick(e) {
            if (notifRef.current && !notifRef.current.contains(e.target)) setNotifOpen(false);
            if (profileRef.current && !profileRef.current.contains(e.target)) setProfileOpen(false);
        }
        document.addEventListener('mousedown', handleClick);
        return () => document.removeEventListener('mousedown', handleClick);
    }, []);

    const handleLogout = () => {
        localStorage.removeItem('token');
        localStorage.removeItem('is_admin');
        localStorage.removeItem('full_name');
        setProfile(null);
        setNotifications([]);
        setNotifUnread(0);
        navigate('/login');
    };

    const handleMarkAllRead = async () => {
        const token = localStorage.getItem('token');
        if (!token) return;
        await api.post('notifications/mark_all_read/');
        setNotifications(notifications.map(n => ({ ...n, is_read: true })));
        setNotifUnread(0);
    };

    return (
        <>
            <div style={{
                position: 'fixed',
                top: 0,
                left: 0,
                width: '100vw',
                height: '100vh',
                zIndex: -2,
                background: 'url("/books1.png") no-repeat center center fixed',
                backgroundSize: 'cover',
            }} />
            <div style={{
                position: 'fixed',
                top: 0,
                left: 0,
                width: '100vw',
                height: '100vh',
                backgroundColor: 'rgba(255,254,254,0.45)',
                zIndex: -1,
            }} />

            {profile && <nav className="navbar navbar-expand-lg navbar-dark bg-dark">
                <div className="container-fluid">
                    <Link className="navbar-brand" to="/">The Literatrium</Link>
                    <button className="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarNav" aria-controls="navbarNav" aria-expanded="false" aria-label="Toggle navigation">
                        <span className="navbar-toggler-icon"></span>
                    </button>
                    <div className="collapse navbar-collapse" id="navbarNav">
                        <ul className="navbar-nav ms-auto align-items-center">
                            <li className="nav-item"><Link className="nav-link" to="/books">Books</Link></li>
                            <li className="nav-item"><Link className="nav-link" to="/user_borrowings">My Borrowings</Link></li>
                            {!profile && <li className="nav-item"><Link className="nav-link" to="/login">Login</Link></li>}
                            {!profile && <li className="nav-item"><Link className="nav-link" to="/signup">Signup</Link></li>}
                            {profile && (
                                <>
                                    <li className="nav-item position-relative" ref={notifRef}>
                                        <button className="btn btn-link nav-link position-relative p-0" onClick={() => setNotifOpen(!notifOpen)}>
                                            <i className="bi bi-bell" style={{ fontSize: '1.3rem' }}></i>
                                            {notifUnread > 0 && <span className="position-absolute top-0 start-100 translate-middle badge rounded-pill bg-danger">{notifUnread}</span>}
                                        </button>
                                        {notifOpen && (
                                            <div className="dropdown-menu dropdown-menu-end show mt-2" style={{ minWidth: 300, right: 0 }}>
                                                <div className="dropdown-header d-flex justify-content-between align-items-center">
                                                    Notifications
                                                    <button className="btn btn-sm btn-link" onClick={handleMarkAllRead}>Mark all as read</button>
                                                </div>
                                                <div style={{ maxHeight: 250, overflowY: 'auto' }}>
                                                    {notifications.length === 0 && <div className="dropdown-item">No notifications</div>}
                                                    {notifications.map(n => (
                                                        <div key={n.id} className={`dropdown-item${n.is_read ? '' : ' fw-bold'}`}>{n.message}</div>
                                                    ))}
                                                </div>
                                            </div>
                                        )}
                                    </li>
                                    <li className="nav-item ms-3 position-relative" ref={profileRef}>
                                        <button className="btn btn-link nav-link p-0" onClick={() => setProfileOpen(!profileOpen)}>
                                            <span className="rounded-circle bg-primary text-white d-inline-flex justify-content-center align-items-center" style={{ width: 36, height: 36, fontWeight: 'bold', fontSize: 18 }}>
                                                {getInitials(profile.full_name)}
                                            </span>
                                        </button>
                                        {profileOpen && (
                                            <div className="dropdown-menu dropdown-menu-end show mt-2" style={{ minWidth: 250, right: 0 }}>
                                                <div className="dropdown-header">{profile.full_name}</div>
                                                <div className="dropdown-item"><strong>Phone:</strong> {profile.phone}</div>
                                                <div className="dropdown-item"><strong>Address:</strong> {profile.address}</div>
                                                <div className="dropdown-divider"></div>
                                                <button className="dropdown-item text-danger" onClick={handleLogout}>Logout</button>
                                            </div>
                                        )}
                                    </li>
                                </>
                            )}
                        </ul>
                    </div>
                </div>
            </nav>}

            <div style={{ minHeight: '100vh', display: 'flex', flexDirection: 'column' }}>
                <main className="container mt-4 flex-grow-1">
                    <Outlet />
                </main>
                <footer className="bg-dark text-white py-3 text-center mt-auto" style={{ position: 'relative', zIndex: 1 }}>
                    <p className="mb-0">&copy; 2025 The Literatrium. All rights reserved.</p>
                </footer>
            </div>
        </>
    );
}

export default Layout; 
