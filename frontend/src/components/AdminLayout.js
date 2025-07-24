import React, { useState, useEffect } from 'react';
import { Link, Outlet, useNavigate } from 'react-router-dom';
import api from '../api';
import '../App.css';
import { BiMenu, BiBook, BiCategory, BiUser, BiLogOut, BiHome, BiListCheck, BiPlusCircle, BiStar, BiBarChart, BiTrendingUp } from 'react-icons/bi';
import 'bootstrap-icons/font/bootstrap-icons.css';

function getInitials(name) {
    if (!name) return '';
    const parts = name.trim().split(' ');
    if (parts.length >= 2) return (parts[0][0] + parts[1][0]).toUpperCase();
    return parts[0][0].toUpperCase();
}

function AdminLayout() {
    const [profile, setProfile] = useState(null);
    const [collapsed, setCollapsed] = useState(false);
    const navigate = useNavigate();

    useEffect(() => {
        const token = localStorage.getItem('token');
        if (token) {
            api.get('profile/').then(res => setProfile(res.data)).catch(() => setProfile(null));
        } else {
            setProfile(null);
        }
    }, []);

    const handleLogout = () => {
        localStorage.removeItem('token');
        localStorage.removeItem('is_admin');
        localStorage.removeItem('full_name');
        setProfile(null);
        navigate('/login');
    };

    return (
        <div style={{ minHeight: '100vh', display: 'flex', flexDirection: 'column' }}>
            <div style={{ display: 'flex', flex: 1, minHeight: 0 }}>
                <aside className={`admin-sidebar${collapsed ? ' collapsed' : ''}`} style={{ width: collapsed ? 70 : 220, background: '#111', color: '#fff', display: 'flex', flexDirection: 'column', alignItems: 'center', padding: '2rem 0', minHeight: '100vh', transition: 'width 0.2s' }}>
                    <button className="btn btn-link text-white mb-4" style={{ fontSize: 24 }} onClick={() => setCollapsed(!collapsed)}>
                        <BiMenu />
                    </button>
                    {profile && !collapsed && (
                        <div className="mb-4 text-center">
                            <div className="rounded-circle bg-primary text-white d-inline-flex justify-content-center align-items-center mb-2" style={{ width: 48, height: 48, fontWeight: 'bold', fontSize: 22 }}>
                                {getInitials(profile.full_name)}
                            </div>
                            <div>{profile.full_name}</div>
                            <button className="btn btn-sm mt-2" onClick={handleLogout}><BiLogOut className="me-1" />Logout</button>
                        </div>
                    )}
                    {profile && collapsed && (
                        <div className="mb-4 text-center">
                            <div className="rounded-circle bg-primary text-white d-inline-flex justify-content-center align-items-center mb-2" style={{ width: 40, height: 40, fontWeight: 'bold', fontSize: 18 }}>
                                {getInitials(profile.full_name)}
                            </div>
                        </div>
                    )}
                    <nav className="nav flex-column w-100 align-items-center">
                        <Link className="nav-link text-white d-flex align-items-center justify-content-center mb-2" to="/admin/dashboard" title="Dashboard">
                            <BiHome size={22} />{!collapsed && <span className="ms-2">Dashboard</span>}
                        </Link>
                        <Link className="nav-link text-white d-flex align-items-center justify-content-center mb-2" to="/admin/books" title="Manage Books">
                            <BiBook size={22} />{!collapsed && <span className="ms-2">Manage Books</span>}
                        </Link>
                        <Link className="nav-link text-white d-flex align-items-center justify-content-center mb-2" to="/admin/borrowings" title="Manage Borrowings">
                            <BiListCheck size={22} />{!collapsed && <span className="ms-2">Manage Borrowings</span>}
                        </Link>
                        <Link className="nav-link text-white d-flex align-items-center justify-content-center mb-2" to="/admin/categories" title="Manage Categories">
                            <BiCategory size={22} />{!collapsed && <span className="ms-2">Manage Categories</span>}
                        </Link>
                        <Link className="nav-link text-white d-flex align-items-center justify-content-center mb-2" to="/admin/reviews" title="Manage Reviews">
                            <BiStar size={22} />{!collapsed && <span className="ms-2">Manage Reviews</span>}
                        </Link>
                        
                        {/* Analytics Section */}
                        {!collapsed && (
                            <div className="text-light text-uppercase mt-3 mb-2" style={{ fontSize: '0.75rem', fontWeight: 'bold', letterSpacing: '1px', opacity: 0.7 }}>
                                Analytics
                            </div>
                        )}
                        <Link className="nav-link text-white d-flex align-items-center justify-content-center mb-2" to="/top-books" title="Top Books">
                            <BiTrendingUp size={22} />{!collapsed && <span className="ms-2">Top Books</span>}
                        </Link>
                        <Link className="nav-link text-white d-flex align-items-center justify-content-center mb-2" to="/monthly_borrowings" title="Monthly Borrowings">
                            <BiBarChart size={22} />{!collapsed && <span className="ms-2">Monthly Borrowings</span>}
                        </Link>
                    </nav>
                </aside>
                <div style={{ flex: 1, padding: '2rem', minWidth: 0 }}>
                    <Outlet />
                </div>
            </div>
            <footer className="bg-dark text-white py-3 text-center mt-auto" style={{ position: 'relative', zIndex: 1 }}>
                <p className="mb-0">&copy; 2025 The Literatrium. All rights reserved.</p>
            </footer>
        </div>
    );
}

export default AdminLayout; 