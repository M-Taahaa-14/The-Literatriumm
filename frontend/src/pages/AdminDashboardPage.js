import React, { useEffect, useState } from 'react';
import api from '../api';
import { Link } from 'react-router-dom';

function AdminDashboardPage() {
    const [stats, setStats] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState('');

    useEffect(() => {
        const token = localStorage.getItem('token');
        if (!token) {
            setError('You must be logged in as admin to view the dashboard.');
            setLoading(false);
            return;
        }
        api.get('admin/dashboard/')
            .then(res => {
                setStats(res.data);
                setLoading(false);
            })
            .catch(() => {
                setError('Could not fetch dashboard stats.');
                setLoading(false);
            });
    }, []);

    return (
        <div>
            <style jsx>{`
                .card-hover {
                    transition: transform 0.2s ease-in-out, box-shadow 0.2s ease-in-out;
                    cursor: pointer;
                }
                .card-hover:hover {
                    transform: translateY(-5px);
                    box-shadow: 0 8px 25px rgba(0,0,0,0.3);
                }
            `}</style>
            <h2>Admin Dashboard</h2>
            {loading ? (
                <div className="text-center my-5">
                    <div className="spinner-border" role="status">
                        <span className="visually-hidden">Loading...</span>
                    </div>
                </div>
            ) : error ? (
                <div className="alert alert-danger">{error}</div>
            ) : stats ? (
                <div className="row g-4">
                    <div className="col-md-3">
                        <Link to="#" className="text-decoration-none">
                            <div className="card text-bg-primary mb-3 h-100 card-hover">
                                <div className="card-body text-center">
                                    <h5 className="card-title">Users</h5>
                                    <p className="card-text display-5">{stats.user_count}</p>
                                    <small className="text-white-50">Click to manage</small>
                                </div>
                            </div>
                        </Link>
                    </div>
                    <div className="col-md-3">
                        <Link to="/admin/books" className="text-decoration-none">
                            <div className="card text-bg-success mb-3 h-100 card-hover">
                                <div className="card-body text-center">
                                    <h5 className="card-title">Books</h5>
                                    <p className="card-text display-5">{stats.book_count}</p>
                                    <small className="text-white-50">Click to manage</small>
                                </div>
                            </div>
                        </Link>
                    </div>
                    <div className="col-md-3">
                        <Link to="/admin/borrowings" className="text-decoration-none">
                            <div className="card text-bg-warning mb-3 h-100 card-hover">
                                <div className="card-body text-center">
                                    <h5 className="card-title">Borrowings</h5>
                                    <p className="card-text display-5">{stats.borrow_count}</p>
                                    <small className="text-white-50">Click to manage</small>
                                </div>
                            </div>
                        </Link>
                    </div>
                    <div className="col-md-3">
                        <Link to="/admin/reviews" className="text-decoration-none">
                            <div className="card text-bg-info mb-3 h-100 card-hover">
                                <div className="card-body text-center">
                                    <h5 className="card-title">Reviews</h5>
                                    <p className="card-text display-5">{stats.review_count}</p>
                                    <small className="text-white-50">Click to manage</small>
                                </div>
                            </div>
                        </Link>
                    </div>
                    <div className="col-md-3">
                        <Link to="/admin/categories" className="text-decoration-none">
                            <div className="card text-bg-secondary mb-3 h-100 card-hover">
                                <div className="card-body text-center">
                                    <h5 className="card-title">Categories</h5>
                                    <p className="card-text display-5">{stats.category_count}</p>
                                    <small className="text-white-50">Click to manage</small>
                                </div>
                            </div>
                        </Link>
                    </div>
                </div>
            ) : null}
        </div>
    );
}

export default AdminDashboardPage; 