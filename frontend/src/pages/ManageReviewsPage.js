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
        // eslint-disable-next-line
    }, []);

    const handleFilter = (e) => {
        e.preventDefault();
        fetchReviews();
    };

    const handleDelete = async (id) => {
        const token = localStorage.getItem('token');
        if (!token) return;
        try {
            await api.delete(`admin/reviews/${id}/delete/`);
            setSuccess('Review deleted.');
            fetchReviews();
        } catch {
            setError('Could not delete review.');
        }
    };

    return (
        <div>
            <h2>Manage Reviews</h2>
            <form className="row g-3 mb-4" onSubmit={handleFilter}>
                <div className="col-md-5">
                    <input type="text" className="form-control" placeholder="Filter by book title" value={bookQuery} onChange={e => setBookQuery(e.target.value)} />
                </div>
                <div className="col-md-3">
                    <select className="form-select" value={ratingQuery} onChange={e => setRatingQuery(e.target.value)}>
                        <option value="">All Ratings</option>
                        {[1, 2, 3, 4, 5].map(n => <option key={n} value={n}>{n}</option>)}
                    </select>
                </div>
                <div className="col-md-2">
                    <button className="btn btn-primary w-100" type="submit">Filter</button>
                </div>
            </form>
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
                                    <td>{review.user}</td>
                                    <td>{review.book}</td>
                                    <td>{review.rating}</td>
                                    <td>{review.content}</td>
                                    <td>{review.created_at ? new Date(review.created_at).toLocaleDateString() : ''}</td>
                                    <td>
                                        <button className="btn btn-danger btn-sm" onClick={() => handleDelete(review.id)}>Delete</button>
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