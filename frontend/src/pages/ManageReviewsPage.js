import React, { useEffect, useState } from 'react';
import api from '../api';

function ManageReviewsPage() {
    const [reviews, setReviews] = useState([]);
    const [bookQuery, setBookQuery] = useState('');
    const [ratingQuery, setRatingQuery] = useState('');
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState('');
    const [success, setSuccess] = useState('');

    const fetchReviews = () => {
        const token = localStorage.getItem('token');
        if (!token) {
            setError('You must be logged in as admin to manage reviews.');
            setLoading(false);
            return;
        }
        setLoading(true);
        api.get('admin/reviews/', {
            params: {
                book: bookQuery,
                rating: ratingQuery
            }
        })
            .then(res => {
                setReviews(res.data);
                setLoading(false);
            })
            .catch(() => {
                setError('Could not fetch reviews.');
                setLoading(false);
            });
    };

    useEffect(() => {
        fetchReviews();
    }, []);

    // Auto-filter when search inputs change
    useEffect(() => {
        const delayedFilter = setTimeout(() => {
            fetchReviews();
        }, 300); // 300ms delay to avoid too many API calls while typing

        return () => clearTimeout(delayedFilter);
        // eslint-disable-next-line
    }, [bookQuery, ratingQuery]);

    const handleDelete = async (id, username, bookTitle) => {
        const confirmDelete = window.confirm(
            `Are you sure you want to delete the review by "${username}" for "${bookTitle}"?\n\nThis action cannot be undone.`
        );
        
        if (!confirmDelete) {
            return;
        }
        
        setError(''); setSuccess('');
        const token = localStorage.getItem('token');
        if (!token) return;
        
        try {
            await api.delete(`admin/reviews/${id}/delete/`);
            setSuccess(`Review by "${username}" for "${bookTitle}" has been deleted successfully.`);
            fetchReviews();
        } catch (err) {
            console.error('Delete review error:', err);
            setError('Could not delete review. Please try again.');
        }
    };

    return (
        <div>
            <h2>Manage Reviews</h2>
            <div className="row g-3 mb-4">
                <div className="col-md-8">
                    <input 
                        type="text" 
                        className="form-control" 
                        placeholder="Filter by book title (auto-filter)" 
                        value={bookQuery} 
                        onChange={e => setBookQuery(e.target.value)} 
                    />
                </div>
                <div className="col-md-4">
                    <select 
                        className="form-select" 
                        value={ratingQuery} 
                        onChange={e => setRatingQuery(e.target.value)}
                    >
                        <option value="">All Ratings</option>
                        {[1, 2, 3, 4, 5].map(n => <option key={n} value={n}>{n} Star{n > 1 ? 's' : ''}</option>)}
                    </select>
                </div>
            </div>
            {error && <div className="alert alert-danger">{error}</div>}
            {success && <div className="alert alert-success">{success}</div>}
            {loading ? (
                <div className="text-center my-5">
                    <div className="spinner-border" role="status">
                        <span className="visually-hidden">Loading...</span>
                    </div>
                </div>
            ) : reviews.length === 0 ? (
                <p>No reviews found.</p>
            ) : (
                <div className="table-responsive">
                    <table className="table table-striped">
                        <thead>
                            <tr>
                                <th>User</th>
                                <th>Book</th>
                                <th>Rating</th>
                                <th>Content</th>
                                <th>Created At</th>
                                <th>Action</th>
                            </tr>
                        </thead>
                        <tbody>
                            {reviews.map(review => (
                                <tr key={review.id}>
                                    <td>
                                        <strong>{review.username || 'Unknown User'}</strong>
                                        <br />
                                        <small className="text-muted">ID: {review.user}</small>
                                    </td>
                                    <td>
                                        <strong>{review.book_title || 'Unknown Book'}</strong>
                                        <br />
                                        <small className="text-muted">ID: {review.book}</small>
                                    </td>
                                    <td>
                                        <div className="d-flex align-items-center">
                                            <span style={{ fontSize: '1.2rem', color: '#ffc107' }}>
                                                {[1, 2, 3, 4, 5].map(star => (
                                                    <span key={star}>
                                                        {star <= review.rating ? '★' : '☆'}
                                                    </span>
                                                ))}
                                            </span>
                                            <span className="ms-2 text-muted">({review.rating}/5)</span>
                                        </div>
                                    </td>
                                    <td>
                                        <div style={{ maxWidth: '300px', wordWrap: 'break-word' }}>
                                            {review.content || <em className="text-muted">No content</em>}
                                        </div>
                                    </td>
                                    <td>{review.created_at ? new Date(review.created_at).toLocaleDateString() : ''}</td>
                                    <td>
                                        <button 
                                            className="btn btn-danger btn-sm" 
                                            onClick={() => handleDelete(review.id, review.username, review.book_title)}
                                            title="Delete this review"
                                        >
                                            <i className="bi bi-trash"></i> Delete
                                        </button>
                                    </td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                </div>
            )}
        </div>
    );
}

export default ManageReviewsPage; 